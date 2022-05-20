# Generated by Django 4.0.4 on 2022-05-01 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0015_spotifypreviewinput'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SpotifyPreviewInput',
            new_name='SpotifyTrackInput',
        ),
        migrations.DeleteModel(
            name='StreamingSongInput',
        ),
        migrations.RemoveField(
            model_name='song',
            name='audio_link',
        ),
        migrations.AddField(
            model_name='song',
            name='spotify_track_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
