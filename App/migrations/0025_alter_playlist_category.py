# Generated by Django 4.0.4 on 2023-03-16 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0024_alter_song_dance_type_alter_songfileinput_dance_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='category',
            field=models.CharField(choices=[('Norm', 'Normal'), ('Party', 'Party'), ('Show', 'Showcase'), ('Solo', 'Solos')], default='Norm', max_length=10),
        ),
    ]
