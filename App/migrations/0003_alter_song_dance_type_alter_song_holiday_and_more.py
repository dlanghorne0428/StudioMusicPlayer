# Generated by Django 4.0 on 2022-02-14 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_playlist_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo/Salsa'), ('Mer', 'Merengue'), ('NC2', 'Nite Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('Q', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing')], default='Cha', max_length=10),
        ),
        migrations.AlterField(
            model_name='song',
            name='holiday',
            field=models.CharField(blank=True, choices=[('Jul4', '4th of July'), ('Hall', 'Halloween'), ('Xmas', 'Christmas'), ('NYE', "New Year's Eve")], default='', max_length=5),
        ),
        migrations.AlterField(
            model_name='songfileinput',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo/Salsa'), ('Mer', 'Merengue'), ('NC2', 'Nite Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('Q', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing')], default='Cha', max_length=10),
        ),
        migrations.AlterField(
            model_name='songfileinput',
            name='holiday',
            field=models.CharField(blank=True, choices=[('Jul4', '4th of July'), ('Hall', 'Halloween'), ('Xmas', 'Christmas'), ('NYE', "New Year's Eve")], default='', max_length=5),
        ),
    ]
