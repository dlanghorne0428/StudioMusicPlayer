# Generated by Django 4.0.4 on 2022-06-03 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0020_song_explicit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='auto_continue',
        ),
        migrations.RemoveField(
            model_name='playlist',
            name='is_showcase_or_comp',
        ),
        migrations.AddField(
            model_name='playlist',
            name='category',
            field=models.CharField(choices=[('Norm', 'Normal'), ('Party', 'Party'), ('Show', 'Showcase')], default='Norm', max_length=10),
        ),
    ]
