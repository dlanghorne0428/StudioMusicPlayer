# Generated by Django 4.0 on 2022-02-03 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0005_song_holiday_songfileinput_holiday'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='special',
            field=models.CharField(blank=True, choices=[('Featr', 'Feature'), ('Req.O', 'Request Only'), ('Teach', 'Teaching')], default='', max_length=10),
        ),
        migrations.AddField(
            model_name='songfileinput',
            name='special',
            field=models.CharField(blank=True, choices=[('Featr', 'Feature'), ('Req.O', 'Request Only'), ('Teach', 'Teaching')], default='', max_length=10),
        ),
    ]