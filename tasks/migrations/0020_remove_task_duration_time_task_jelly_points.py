# Generated by Django 4.2.6 on 2023-12-12 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0019_task_duration_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='duration_time',
        ),
        migrations.AddField(
            model_name='task',
            name='jelly_points',
            field=models.IntegerField(default=0),
        ),
    ]