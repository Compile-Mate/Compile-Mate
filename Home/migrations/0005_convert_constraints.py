from django.db import migrations, models
import json

def convert_constraints_to_text(apps, schema_editor):
    Problem = apps.get_model('Home', 'Problem')
    for problem in Problem.objects.all():
        if problem.constraints:
            if isinstance(problem.constraints, list):
                problem.constraints = '\n'.join(problem.constraints)
            elif isinstance(problem.constraints, str):
                try:
                    # If it's a JSON string, parse it and convert to text
                    constraints_list = json.loads(problem.constraints)
                    if isinstance(constraints_list, list):
                        problem.constraints = '\n'.join(constraints_list)
                except json.JSONDecodeError:
                    # If it's already a text string, leave it as is
                    pass
            problem.save()

class Migration(migrations.Migration):
    dependencies = [
        ('Home', '0004_alter_problem_task'),
    ]

    operations = [
        migrations.RunPython(convert_constraints_to_text),
    ] 