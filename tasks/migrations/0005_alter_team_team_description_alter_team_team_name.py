# Generated by Django 4.2.6 on 2023-11-23 14:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_alter_team_team_description_alter_team_team_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='team_description',
            field=models.CharField(max_length=150, validators=[django.core.validators.MinLengthValidator(10, message='Team description must be a minimum of 10 characters')]),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_name',
            field=models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(3, message='Team name must be a minimum of 3 characters')]),
        ),
    ]
