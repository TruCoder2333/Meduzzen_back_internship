# Generated by Django 4.2.5 on 2023-10-23 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinvitation',
            name='status',
            field=models.CharField(choices=[('invited', 'invited'), ('requested', 'requested'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=20),
        ),
    ]