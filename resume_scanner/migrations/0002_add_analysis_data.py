# Generated migration for adding analysis_data field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume_scanner', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumescan',
            name='analysis_data',
            field=models.JSONField(blank=True, default=dict, help_text='Complete analysis data'),
        ),
        migrations.AlterModelOptions(
            name='resumescan',
            options={'ordering': ['-uploaded_at'], 'verbose_name': 'Resume Scan', 'verbose_name_plural': 'Resume Scans'},
        ),
    ]

