# Generated by Django 4.0 on 2022-03-06 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0010_remove_user_percentage_preferences_user_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='preferences',
            field=models.JSONField(null=True),
        ),
    ]
