# Generated by Django 4.2.5 on 2023-11-04 03:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_alter_company_administrators'),
        ('quizzes', '0002_quizresult_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizresult',
            name='company',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]