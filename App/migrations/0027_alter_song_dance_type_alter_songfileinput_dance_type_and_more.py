# Generated by Django 4.0.4 on 2023-03-18 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0026_alter_playlist_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo / Salsa'), ('Mer', 'Merengue'), ('NC2', 'Night Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('Q', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing'), ('gen', 'General')], default='Cha', max_length=10),
        ),
        migrations.AlterField(
            model_name='songfileinput',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo / Salsa'), ('Mer', 'Merengue'), ('NC2', 'Night Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('Q', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing'), ('gen', 'General')], default='Cha', max_length=10),
        ),
        migrations.AlterField(
            model_name='spotifytrackinput',
            name='dance_type',
            field=models.CharField(choices=[('Bac', 'Bachata'), ('Bol', 'Bolero'), ('Cha', 'Cha-Cha'), ('C2S', 'Country Two Step'), ('ECS', 'East Coast Swing'), ('Fox', 'Foxtrot'), ('Hus', 'Hustle'), ('Jiv', 'Jive'), ('Mam', 'Mambo / Salsa'), ('Mer', 'Merengue'), ('NC2', 'Night Club 2-Step'), ('PD', 'Paso Doble'), ('Pea', 'Peabody'), ('Q', 'Quickstep'), ('Rum', 'Rumba'), ('Sam', 'Samba'), ('Tan', 'Tango'), ('VW', 'Viennese Waltz'), ('Wal', 'Waltz'), ('WCS', 'West Coast Swing'), ('gen', 'General')], default='Cha', max_length=10),
        ),
    ]