from django.db import migrations, models
import django.db.models.deletion


def repopulate_quiz_results(apps, schema_editor):
    QuizResult = apps.get_model('quizzes', 'QuizResult')
    QuizAttempt = apps.get_model('quizzes', 'QuizAttempt')

    quiz_attempts = QuizAttempt.objects.all()

    for quiz_attempt in quiz_attempts:
        QuizResult.objects.filter(quiz=quiz_attempt.quiz, user=quiz_attempt.user).update(quiz_attempt_id=quiz_attempt.id)



class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0003_alter_quizresult_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='quiz_attempt',
            field=models.ForeignKey(
                default=None, 
                on_delete=django.db.models.deletion.CASCADE, 
                to='quizzes.QuizAttempt', 
                null=True
                ),
        ),
        migrations.RunPython(repopulate_quiz_results, migrations.RunPython.noop),
    ]
