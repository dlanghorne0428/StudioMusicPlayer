from django.db import models
from django.utils.text import get_valid_filename, slugify

import os


DANCE_TYPE_CHOICES = [
    ("Bac", "Bachata"),
    ("Bol", "Bolero"),    
    ("Cha", "Cha-Cha"), 
    ("C2S", "Country Two Step"), 
    ("ECS", "East Coast Swing"),
    ("Fox", "Foxtrot"),
    ("Hus", "Hustle"),
    ("Jiv", "Jive"),
    ("Mam", "Mambo/Salsa"),
    ("Mer", "Merengue"),
    ("NC2", "Night Club 2-Step"),
    ("PD",  "Paso Doble"),
    ("Pea", "Peabody"),
    ("Q",   "Quickstep"),
    ("Rum", "Rumba"),    
    ("Sam", "Samba"),
    ("Tan", "Tango"),  
    ("VW",  "Viennese Waltz"),
    ("Wal", "Waltz"),
    ("WCS", "West Coast Swing"),
    ]

DANCE_TYPE_DEFAULT_PERCENTAGES = {
    "Bac":  0,      # i have no bachata songs yet             
    "Bol":  3,        
    "Cha": 15, 
    "C2S":  2, 
    "ECS": 15,
    "Fox": 10,
    "Hus":  5,
    "Jiv":  2,
    "Mam":  0,     # i have no mambo or salso songs yet 
    "Mer":  0,     # i have no merengue songs yet 
    "NC2":  3,
    "PD":   0,     # i have no paso songs yet
    "Pea":  0,     # i have no peabody songs yet
    "Q":    2,
    "Rum": 10,    
    "Sam":  3,
    "Tan":  0,  
    "VW":   5,
    "Wal": 10,
    "WCS": 15,
    }

DANCE_TYPE_TEMPOS = {
    "Bac": "Mid",                  
    "Bol": "Slow",        
    "Cha": "Mid", 
    "C2S": "Mid",  
    "ECS": "Fast",
    "Fox": "Mid",
    "Hus": "Fast",  
    "Jiv": "Fast",
    "Mam": "Fast",    
    "Mer": "Mid",    
    "NC2": "Slow",
    "PD":  "Mid",   
    "Pea": "Fast",    
    "Q":   "Fast",
    "Rum": "Slow",    
    "Sam": "Mid",
    "Tan": "Mid",  
    "VW":  "Fast",
    "Wal": "Slow",
    "WCS": "Mid",
    }

HOLIDAY_CHOICES = (
    ("Jul4", "4th of July"),
    ("Hall", "Halloween"),
    ("Xmas", "Christmas"),
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