from django.db import models
from django.utils.text import get_valid_filename, slugify

import os


DANCE_TYPE_CHOICES = (
    ("Wal", "Waltz"),
    ("Tan", "Tango"),
    ("Fox", "Foxtrot"),
    ("VW",  "Viennese Waltz"),
    ("Cha", "Cha-Cha"),
    ("Rum", "Rumba"),
    ("ECS", "East Coast Swing"),
    ("Bol", "Bolero"),
    ("Mam", "Mambo"),      # consider Mambo / Salsa
    ("Q",   "Quickstep"),
    ("Sam", "Samba"),
    ("PD",  "Paso Doble"),
    ("Jiv", "Jive"),
    ("Pea", "Peabody"),
    ("Bac", "Bachata"),
    ("Mer", "Merengue"),
    ("Hus", "Hustle"), 
    ("WCS", "West Coast Swing"),
    ("NC2", "Nite Club 2-Step"),
    ("C2S", "Country Two Step"), 
    )

HOLIDAY_CHOICES = (
    ("Xmas", "Christmas"),
    ("Hall", "Halloween"),
    ("Jul4", "4th of July"),
    ("NYE",  "New Year's Eve"),
    )


SPECIAL_CHOICES = (
    ("Featr", "Feature"),          # is this for solos, play entire song?
    ("Req.O", "Request Only"),
    ("Teach", "Teaching"),
    )
    

def create_valid_filename(instance, filename):
    ''' When uploading audio files, find a valid name that django can use.
       slugify replaces whitespace with a dash and removes everything but alphanumerics,
       underscores and dashes.
       get_valid_filename finds an available filename to avoid duplicates.'''
    temp_filename = get_valid_filename(filename)
    filename, ext = os.path.splitext(temp_filename)
    filename = slugify(filename)
    if ext:
        valid_filename = "%s.%s" % (filename, slugify(ext))
    else:
        valid_filename = filename
        
    # save music files in a "music" subfolder under MEDIA_ROOT
    path = 'music/' + valid_filename
    return path


class SongFileInput(models.Model):
    '''This model is for uploading audio files. It consists of the filename,
      dance type, holiday (if any) and special (if any) '''
    audio_file = models.FileField(upload_to=create_valid_filename)
    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )
    holiday = models.CharField(
        max_length = 5,
        choices = HOLIDAY_CHOICES,
        blank = True,
        default = ""
        )
    special = models.CharField(
        max_length = 10,
        choices = SPECIAL_CHOICES,
        blank = True,
        default = ""
        )
    
    def __str__(self):
        return self.audio_file.url + ": " + self.dance_type
    

class Song(models.Model):
    '''This the model for a song in our music database.
       The music itself is either in a filename or link to the file. 
       The metadata (artist and title) are stored.
       There is also an image filename for the cover art.
       Finally, the dance_type is also stored.'''
    
    audio_file = models.FileField(blank=True, null=True)
    audio_link = models.CharField(max_length=200,blank=True, null=True) 
    
    # these will be created from the audio_file
    title = models.CharField(max_length=200,default="Unknown")
    artist = models.CharField(max_length=200,default="Unknown")
    image = models.ImageField(null=True)

    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )
    
    holiday = models.CharField(
        max_length = 5,
        choices = HOLIDAY_CHOICES,
        blank = True,
        default = ""
        )  
    
    special = models.CharField(
        max_length = 10,
        choices = SPECIAL_CHOICES,
        blank = True,
        default = ""
        )
        

    def __str__(self):
        return self.title