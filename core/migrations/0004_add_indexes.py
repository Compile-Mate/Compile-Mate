# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_chattemplate_supportchat_chatrating_chatmessage_and_more'),
    ]

    operations = [
        # Add indexes for Notification model
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', '-created_at'], name='core_notif_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='core_notif_user_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['notification_type', '-created_at'], name='core_notif_type_time_idx'),
        ),
        
        # Add indexes for UserActivity model
        migrations.AddIndex(
            model_name='useractivity',
            index=models.Index(fields=['user', '-created_at'], name='core_activity_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='useractivity',
            index=models.Index(fields=['activity_type', '-created_at'], name='core_activity_type_time_idx'),
        ),
        
        # Add indexes for SupportChat model
        migrations.AddIndex(
            model_name='supportchat',
            index=models.Index(fields=['user', '-created_at'], name='core_chat_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='supportchat',
            index=models.Index(fields=['admin', 'status'], name='core_chat_admin_status_idx'),
        ),
        migrations.AddIndex(
            model_name='supportchat',
            index=models.Index(fields=['status', 'priority'], name='core_chat_status_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='supportchat',
            index=models.Index(fields=['category', '-created_at'], name='core_chat_cat_time_idx'),
        ),
        migrations.AddIndex(
            model_name='supportchat',
            index=models.Index(fields=['-last_activity'], name='core_chat_last_activity_idx'),
        ),
        
        # Add indexes for ChatMessage model
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['chat', 'created_at'], name='core_msg_chat_time_idx'),
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['sender', '-created_at'], name='core_msg_sender_time_idx'),
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['is_read'], name='core_msg_read_idx'),
        ),
        
        # Add indexes for ContactMessage model
        migrations.AddIndex(
            model_name='contactmessage',
            index=models.Index(fields=['status', '-created_at'], name='core_contact_status_time_idx'),
        ),
        
        # Add indexes for SystemLog model
        migrations.AddIndex(
            model_name='systemlog',
            index=models.Index(fields=['level', '-created_at'], name='core_log_level_time_idx'),
        ),
        migrations.AddIndex(
            model_name='systemlog',
            index=models.Index(fields=['-created_at'], name='core_log_time_idx'),
        ),
    ]

