# Generated by Django 4.0.4 on 2022-05-28 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0018_rename_track_uri_spotifytrackinput_track_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='streaming',
            field=models.BooleanField(default=False),
        ),
    ]
