# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Add indexes for User model
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['-xp'], name='users_user_xp_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['-problems_solved'], name='users_user_prob_solved_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['-current_streak'], name='users_user_curr_streak_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['last_activity'], name='users_user_last_activity_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='users_user_email_idx'),
        ),
        
        # Add indexes for CoinTransaction model
        migrations.AddIndex(
            model_name='cointransaction',
            index=models.Index(fields=['user', '-timestamp'], name='users_coin_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='cointransaction',
            index=models.Index(fields=['transaction_type', '-timestamp'], name='users_coin_type_time_idx'),
        ),
        
        # Add indexes for UserAchievement model
        migrations.AddIndex(
            model_name='userachievement',
            index=models.Index(fields=['user', '-earned_at'], name='users_achv_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='userachievement',
            index=models.Index(fields=['achievement_type'], name='users_achv_type_idx'),
        ),
    ]

