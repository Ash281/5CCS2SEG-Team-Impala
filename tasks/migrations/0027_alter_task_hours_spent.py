# Generated by Django 4.2.6 on 2023-12-13 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0026_merge_20231213_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='hours_spent',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
