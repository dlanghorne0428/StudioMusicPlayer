# Generated by Django 4.0 on 2022-02-18 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_alter_song_dance_type_alter_song_holiday_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo/Salsa'), ('Mer', 'Merengue'), ('NC2', 'Night Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('QS', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing')], default='Cha', max_length=10),
        ),
        migrations.AlterField(
            model_name='songfileinput',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo/Salsa'), ('Mer', 'Merengue'), ('NC2', 'Night Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('QS', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing')], default='Cha', max_length=10),
        ),
    ]