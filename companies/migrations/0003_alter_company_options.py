# Generated by Django 4.2.5 on 2023-10-19 03:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_company_created_at_company_updated_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'Companies'},
        ),
    ]