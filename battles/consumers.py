"""
WebSocket Consumers for Real-Time Code Battles
Handles live battle updates, spectating, and real-time interactions
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta


class BattleConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time code battles."""
    
    async def connect(self):
        self.battle_id = self.scope['url_route']['kwargs']['battle_id']
        self.battle_group_name = f'battle_{self.battle_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user is authorized to view this battle
        is_authorized = await self.check_authorization()
        if not is_authorized:
            await self.close()
            return
        
        # Join battle group
        await self.channel_layer.group_add(
            self.battle_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send battle state to newly connected user
        battle_state = await self.get_battle_state()
        await self.send(text_data=json.dumps({
            'type': 'battle_state',
            'data': battle_state
        }))
        
        # Notify others of spectator join (if spectating)
        is_participant = await self.is_participant()
        if not is_participant:
            await self.channel_layer.group_send(
                self.battle_group_name,
                {
                    'type': 'spectator_joined',
                    'user': self.user.username
                }
            )
    
    async def disconnect(self, close_code):
        # Leave battle group
        await self.channel_layer.group_discard(
            self.battle_group_name,
            self.channel_name
        )
        
        # Notify others of spectator leave (if spectating)
        is_participant = await self.is_participant()
        if not is_participant:
            await self.channel_layer.group_send(
                self.battle_group_name,
                {
                    'type': 'spectator_left',
                    'user': self.user.username
                }
            )
    
    async def receive(self, text_data):
        """Handle incoming messages from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'code_update':
                await self.handle_code_update(data)
            elif message_type == 'submit_solution':
                await self.handle_submit_solution(data)
            elif message_type == 'forfeit':
                await self.handle_forfeit()
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_code_update(self, data):
        """Handle real-time code updates (for spectators)."""
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        # Broadcast code update to spectators only
        await self.channel_layer.group_send(
            self.battle_group_name,
            {
                'type': 'code_updated',
                'user': self.user.username,
                'code_preview': code[:100],  # Send preview only for performance
                'language': language,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_submit_solution(self, data):
        """Handle solution submission during battle."""
        from battles.models import Battle, BattleSubmission
        from problems.models import Submission
        from judge.executor import execute_test_cases
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        # Get battle
        battle = await self.get_battle()
        if not battle or battle.status != 'in_progress':
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Battle is not active'
            }))
            return
        
        # Check if user already submitted
        has_submitted = await self.has_user_submitted()
        if has_submitted:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You have already submitted'
            }))
            return
        
        # Execute code against test cases
        test_cases = await self.get_test_cases(battle)
        
        # Run execution (this would ideally be async with Celery)
        # For real-time, we do quick execution
        try:
            result = await database_sync_to_async(execute_test_cases)(
                language=language,
                code=code,
                test_cases=test_cases,
                timeout=5
            )
            
            # Create submission
            submission = await self.create_submission(
                battle=battle,
                code=code,
                language=language,
                result=result
            )
            
            # Check if all tests passed
            all_passed = result['passed'] == result['total_tests']
            
            if all_passed:
                # User won the battle!
                await self.end_battle(battle, winner=self.user)
                
                # Broadcast battle end
                await self.channel_layer.group_send(
                    self.battle_group_name,
                    {
                        'type': 'battle_ended',
                        'winner': self.user.username,
                        'time_taken': str(timezone.now() - battle.started_at),
                        'stake': battle.stake
                    }
                )
            else:
                # Submission failed, notify user
                await self.send(text_data=json.dumps({
                    'type': 'submission_failed',
                    'result': result
                }))
                
                # Notify opponent of attempt
                await self.channel_layer.group_send(
                    self.battle_group_name,
                    {
                        'type': 'opponent_attempted',
                        'user': self.user.username
                    }
                )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Execution failed: {str(e)}'
            }))
    
    async def handle_forfeit(self):
        """Handle battle forfeit."""
        battle = await self.get_battle()
        if not battle or battle.status != 'in_progress':
            return
        
        # Determine winner (opponent)
        opponent = battle.opponent if self.user == battle.challenger else battle.challenger
        
        # End battle
        await self.end_battle(battle, winner=opponent)
        
        # Broadcast forfeit
        await self.channel_layer.group_send(
            self.battle_group_name,
            {
                'type': 'battle_forfeited',
                'forfeiter': self.user.username,
                'winner': opponent.username
            }
        )
    
    async def handle_chat_message(self, data):
        """Handle chat messages during battle."""
        message = data.get('message', '').strip()
        if not message:
            return
        
        # Broadcast chat message
        await self.channel_layer.group_send(
            self.battle_group_name,
            {
                'type': 'chat_message_received',
                'user': self.user.username,
                'message': message,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    # Event handlers for group messages
    async def spectator_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'spectator_joined',
            'user': event['user']
        }))
    
    async def spectator_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'spectator_left',
            'user': event['user']
        }))
    
    async def code_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'code_updated',
            'user': event['user'],
            'code_preview': event['code_preview'],
            'language': event['language'],
            'timestamp': event['timestamp']
        }))
    
    async def battle_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'battle_ended',
            'winner': event['winner'],
            'time_taken': event['time_taken'],
            'stake': event['stake']
        }))
    
    async def battle_forfeited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'battle_forfeited',
            'forfeiter': event['forfeiter'],
            'winner': event['winner']
        }))
    
    async def opponent_attempted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'opponent_attempted',
            'user': event['user']
        }))
    
    async def chat_message_received(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user': event['user'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    # Database operations
    @database_sync_to_async
    def check_authorization(self):
        """Check if user is authorized to view this battle."""
        from battles.models import Battle
        try:
            battle = Battle.objects.get(battle_id=self.battle_id)
            # User must be participant or spectator
            return (self.user == battle.challenger or 
                    self.user == battle.opponent or
                    battle.spectators.filter(id=self.user.id).exists())
        except Battle.DoesNotExist:
            return False
    
    @database_sync_to_async
    def is_participant(self):
        """Check if user is a participant (not spectator)."""
        from battles.models import Battle
        try:
            battle = Battle.objects.get(battle_id=self.battle_id)
            return self.user == battle.challenger or self.user == battle.opponent
        except Battle.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_battle(self):
        """Get battle object."""
        from battles.models import Battle
        try:
            return Battle.objects.select_related('challenger', 'opponent', 'problem').get(
                battle_id=self.battle_id
            )
        except Battle.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_battle_state(self):
        """Get current battle state."""
        from battles.models import Battle
        try:
            battle = Battle.objects.select_related('challenger', 'opponent', 'problem').get(
                battle_id=self.battle_id
            )
            
            time_remaining = None
            if battle.status == 'in_progress' and battle.started_at:
                elapsed = timezone.now() - battle.started_at
                limit = timedelta(minutes=battle.time_limit)
                remaining = limit - elapsed
                time_remaining = max(remaining.total_seconds(), 0)
            
            return {
                'battle_id': str(battle.battle_id),
                'status': battle.status,
                'challenger': battle.challenger.username,
                'opponent': battle.opponent.username if battle.opponent else None,
                'problem_id': battle.problem.id,
                'problem_title': battle.problem.title,
                'stake': battle.stake,
                'time_limit': battle.time_limit,
                'time_remaining': time_remaining,
                'spectator_count': battle.spectator_count,
                'started_at': battle.started_at.isoformat() if battle.started_at else None
            }
        except Battle.DoesNotExist:
            return {}
    
    @database_sync_to_async
    def has_user_submitted(self):
        """Check if user has already submitted."""
        from battles.models import BattleSubmission
        return BattleSubmission.objects.filter(
            battle__battle_id=self.battle_id,
            user=self.user
        ).exists()
    
    @database_sync_to_async
    def get_test_cases(self, battle):
        """Get test cases for battle problem."""
        from problems.models import TestCase
        test_cases = TestCase.objects.filter(problem=battle.problem).order_by('order')
        return [{
            'input': tc.input_data,
            'expected_output': tc.expected_output
        } for tc in test_cases]
    
    @database_sync_to_async
    def create_submission(self, battle, code, language, result):
        """Create battle submission."""
        from battles.models import BattleSubmission
        from problems.models import Submission
        
        # Create regular submission
        submission = Submission.objects.create(
            user=self.user,
            problem=battle.problem,
            code=code,
            language=language,
            status='accepted' if result['passed'] == result['total_tests'] else 'wrong_answer',
            execution_time=result.get('total_time', 0),
            score=int((result['passed'] / result['total_tests']) * 100)
        )
        
        # Create battle submission
        time_taken = timezone.now() - battle.started_at
        battle_submission = BattleSubmission.objects.create(
            battle=battle,
            user=self.user,
            submission=submission,
            time_taken=time_taken
        )
        
        return battle_submission
    
    @database_sync_to_async
    def end_battle(self, battle, winner):
        """End the battle."""
        battle.end_battle(winner=winner)
        
        # Update battle stats for both users
        from battles.models import BattleStats
        
        winner_stats, _ = BattleStats.objects.get_or_create(user=winner)
        winner_stats.update_stats(battle, won=True)
        
        loser = battle.opponent if winner == battle.challenger else battle.challenger
        loser_stats, _ = BattleStats.objects.get_or_create(user=loser)
        loser_stats.update_stats(battle, won=False)

