# Generated by Django 4.2.6 on 2023-11-30 12:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_merge_20231130_1230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='assignees',
        ),
        migrations.AddField(
            model_name='task',
            name='assignees',
            field=models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL),
        ),
    ]
