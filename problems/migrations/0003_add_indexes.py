# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0002_initial'),
    ]

    operations = [
        # Add indexes for Problem model
        migrations.AddIndex(
            model_name='problem',
            index=models.Index(fields=['difficulty', 'status'], name='problems_prob_diff_status_idx'),
        ),
        migrations.AddIndex(
            model_name='problem',
            index=models.Index(fields=['-acceptance_rate'], name='problems_prob_accept_rate_idx'),
        ),
        migrations.AddIndex(
            model_name='problem',
            index=models.Index(fields=['-created_at'], name='problems_prob_created_idx'),
        ),
        migrations.AddIndex(
            model_name='problem',
            index=models.Index(fields=['slug'], name='problems_prob_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='problem',
            index=models.Index(fields=['status'], name='problems_prob_status_idx'),
        ),
        
        # Add indexes for Submission model  
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['user', '-submitted_at'], name='problems_sub_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['problem', '-submitted_at'], name='problems_sub_prob_time_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['user', 'problem', 'status'], name='problems_sub_user_prob_status_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['status', '-submitted_at'], name='problems_sub_status_time_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['-judged_at'], name='problems_sub_judged_idx'),
        ),
        
        # Add indexes for TestCase model
        migrations.AddIndex(
            model_name='testcase',
            index=models.Index(fields=['problem', 'order'], name='problems_test_prob_order_idx'),
        ),
        migrations.AddIndex(
            model_name='testcase',
            index=models.Index(fields=['problem', 'is_hidden'], name='problems_test_prob_hidden_idx'),
        ),
        
        # Add indexes for ProblemDiscussion model
        migrations.AddIndex(
            model_name='problemdiscussion',
            index=models.Index(fields=['problem', '-created_at'], name='problems_disc_prob_time_idx'),
        ),
        migrations.AddIndex(
            model_name='problemdiscussion',
            index=models.Index(fields=['user', '-created_at'], name='problems_disc_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='problemdiscussion',
            index=models.Index(fields=['parent'], name='problems_disc_parent_idx'),
        ),
        migrations.AddIndex(
            model_name='problemdiscussion',
            index=models.Index(fields=['is_solution'], name='problems_disc_solution_idx'),
        ),
    ]

