# Generated by Django 4.2.5 on 2023-10-25 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0003_alter_companyinvitation_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyinvitation',
            options={'verbose_name_plural': 'CompanyInvites'},
        ),
        migrations.AlterField(
            model_name='companyinvitation',
            name='status',
            field=models.CharField(choices=[('invited', 'INVITED'), ('requested', 'REQUESTED'), ('accepted', 'ACCEPTED'), ('rejected', 'REJECTED'), ('canceled', 'CANCELED')], max_length=20),
        ),
    ]
