# Generated by Django 4.0.4 on 2022-05-19 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0017_user_has_spotify_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spotifytrackinput',
            old_name='track_URI',
            new_name='track_id',
        ),
        migrations.AddField(
            model_name='spotifytrackinput',
            name='artist',
            field=models.CharField(default='Unknown', max_length=200),
        ),
        migrations.AddField(
            model_name='spotifytrackinput',
            name='title',
            field=models.CharField(default='Unknown', max_length=200),
        ),
    ]