# Generated by Django 4.2.7 on 2025-06-25 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rewards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucherredemption',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voucher_redemptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='voucherredemption',
            name='voucher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='rewards.voucher'),
        ),
        migrations.AddField(
            model_name='userreward',
            name='reward',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_rewards', to='rewards.reward'),
        ),
        migrations.AddField(
            model_name='userreward',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earned_rewards', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reward',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rewards', to='rewards.rewardcategory'),
        ),
        migrations.AddField(
            model_name='referralreward',
            name='referred_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='referralreward',
            name='referrer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals_made', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dailyreward',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_rewards', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='userreward',
            unique_together={('user', 'reward')},
        ),
        migrations.AlterUniqueTogether(
            name='referralreward',
            unique_together={('referrer', 'referred_user')},
        ),
        migrations.AlterUniqueTogether(
            name='dailyreward',
            unique_together={('user', 'date')},
        ),
    ]
