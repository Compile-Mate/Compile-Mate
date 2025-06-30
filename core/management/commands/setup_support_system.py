from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import ChatTemplate, AdminAvailability
from users.models import User

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the support chat system with sample templates and admin availability'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up support chat system...')
        
        # Create chat templates
        templates_data = [
            {
                'name': 'Welcome Message',
                'category': 'general',
                'subject': 'Welcome to CompileMate',
                'content': 'Hello! Welcome to CompileMate. How can I help you today?',
                'tags': ['welcome', 'greeting']
            },
            {
                'name': 'Technical Issue Response',
                'category': 'technical',
                'subject': 'Technical Issue',
                'content': 'I understand you\'re experiencing a technical issue. Let me help you resolve this. Could you please provide more details about what you\'re seeing?',
                'tags': ['technical', 'bug']
            },
            {
                'name': 'Account Issue Response',
                'category': 'account',
                'subject': 'Account Issue',
                'content': 'I\'m here to help with your account issue. Could you please describe what specific problem you\'re encountering?',
                'tags': ['account', 'login']
            },
            {
                'name': 'Billing Question Response',
                'category': 'billing',
                'subject': 'Billing Question',
                'content': 'Thank you for your question about billing and MateCoins. Let me clarify how our reward system works...',
                'tags': ['billing', 'coins']
            },
            {
                'name': 'Feature Request Response',
                'category': 'feature_request',
                'subject': 'Feature Request',
                'content': 'Thank you for your feature request! We appreciate your input. Let me gather more details about what you\'re looking for.',
                'tags': ['feature', 'request']
            },
            {
                'name': 'Contest Question Response',
                'category': 'contest',
                'subject': 'Contest Question',
                'content': 'I\'d be happy to help you with your contest question. What specific aspect of contests would you like to know more about?',
                'tags': ['contest', 'competition']
            },
            {
                'name': 'Problem Solving Help',
                'category': 'problem',
                'subject': 'Problem Solving',
                'content': 'I can help you with problem-solving strategies. What type of problem are you working on?',
                'tags': ['problem', 'algorithm']
            },
            {
                'name': 'Bug Report Response',
                'category': 'bug_report',
                'subject': 'Bug Report',
                'content': 'Thank you for reporting this bug. To help us fix it quickly, could you please provide:\n1. Steps to reproduce\n2. What you expected to happen\n3. What actually happened\n4. Your browser and OS',
                'tags': ['bug', 'report']
            }
        ]
        
        for template_data in templates_data:
            template, created = ChatTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created template: {template.name}')
            else:
                self.stdout.write(f'Template already exists: {template.name}')
        
        # Set up admin availability for superusers
        superusers = User.objects.filter(is_superuser=True)
        for admin in superusers:
            availability, created = AdminAvailability.objects.get_or_create(
                admin=admin,
                defaults={
                    'is_online': True,
                    'is_available': True,
                    'max_concurrent_chats': 5,
                    'current_chats': 0,
                    'working_hours': {
                        'monday': {'start': '09:00', 'end': '17:00'},
                        'tuesday': {'start': '09:00', 'end': '17:00'},
                        'wednesday': {'start': '09:00', 'end': '17:00'},
                        'thursday': {'start': '09:00', 'end': '17:00'},
                        'friday': {'start': '09:00', 'end': '17:00'},
                        'saturday': {'start': '10:00', 'end': '15:00'},
                        'sunday': {'start': '10:00', 'end': '15:00'},
                    },
                    'timezone': 'UTC',
                    'specializations': ['general', 'technical', 'billing'],
                    'languages': ['English']
                }
            )
            if created:
                self.stdout.write(f'Created admin availability for: {admin.username}')
            else:
                self.stdout.write(f'Admin availability already exists for: {admin.username}')
        
        self.stdout.write(
            self.style.SUCCESS('Support chat system setup completed successfully!')
        )
        self.stdout.write('Features available:')
        self.stdout.write('- Real-time chat between users and admins')
        self.stdout.write('- Chat templates for quick responses')
        self.stdout.write('- Admin availability tracking')
        self.stdout.write('- Chat rating and feedback system')
        self.stdout.write('- Floating chat widget on all pages') 