# Generated by Django 4.2.6 on 2024-03-10 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0033_tag_tagged_songs'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tagged_Songs',
            new_name='Tagged_Song',
        ),
        migrations.AddField(
            model_name='song',
            name='tags',
            field=models.ManyToManyField(through='App.Tagged_Song', to='App.tag'),
        ),
    ]
