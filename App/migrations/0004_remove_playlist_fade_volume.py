# Generated by Django 4.0 on 2022-01-30 03:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_playlist_songinplaylist_playlist_songs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='fade_volume',
        ),
    ]
