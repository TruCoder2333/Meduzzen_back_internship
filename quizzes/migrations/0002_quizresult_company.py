# Generated by Django 4.2.5 on 2023-11-04 02:38

from django.db import migrations, models
import django.db.models.deletion

def set_company_for_quiz_results(apps, schema_editor):
    QuizResult = apps.get_model('quizzes', 'QuizResult')

    for quiz_result in QuizResult.objects.all():
        if not quiz_result.company_id and quiz_result.quiz:
            quiz_result.company = quiz_result.quiz.company
            quiz_result.save()

class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_alter_company_administrators'),
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='company',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='companies.company', null=True),
        ),
        migrations.RunPython(set_company_for_quiz_results),
    ]
