# Generated by Django 4.0.4 on 2022-06-02 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0019_playlist_streaming'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='explicit',
            field=models.BooleanField(default=False),
        ),
    ]
