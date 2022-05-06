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
    "Bac":  3,                  
    "Bol":  5,        
    "Cha": 10, 
    "C2S":  2, 
    "ECS": 10,
    "Fox": 10,
    "Hus":  3,
    "Jiv":  2,
    "Mam":  5,     
    "Mer":  2,     
    "NC2":  3,
    "PD":   0,     # i have no paso songs yet
    "Pea":  0,     # i have no peabody songs yet
    "Q":    2,
    "Rum": 10,    
    "Sam":  3,
    "Tan": 10,  
    "VW":   5,
    "Wal": 10,
    "WCS":  5,
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

HOLIDAY_CHOICES = [
    ("Jul4", "4th of July"),
    ("Hween", "Halloween"),
    ("Xmas", "Christmas"),
    ("NYE",  "New Year's Eve"),
    ]

HOLIDAY_USE_OPTIONS = [
    ("Ex", "Exclude"),
    ("In", "Include At Random"), 
    ("Ev2", "Every Other Song"),
    ("Ev3", "Every Third Song"),
    ("Ev4", "Every Fourth Song"),
    ]

HOLIDAY_DEFAULT_USAGE = {
    "Jul4" : "In",
    "Hween": "In",
    "Xmas" : "Ex",  # exclude Christmas songs by default
    "NYE"  : "In"
    }

def good_filename(filename):
    '''slugify replaces whitespace with a dash and removes everything but alphanumerics,
       underscores and dashes.
       get_valid_filename finds an available filename to avoid duplicates.'''
    print(filename)
    temp_filename = get_valid_filename(filename)
    print(temp_filename)
    filename, ext = os.path.splitext(temp_filename)
    filename = slugify(filename)
    if ext:
        return "%s.%s" % (filename, slugify(ext))
    else:
        return filename

    
def create_valid_filename(instance, filename):
    ''' When uploading audio files, find a valid name that django can use.'''

    # save music files in a "music" subfolder under MEDIA_ROOT
    path = 'music/' + good_filename(filename)
    return path


def create_valid_image_filename(instance, filename):
    ''' When uploading audio files, find a valid name that django can use.'''

    # save image files in a "img" subfolder under MEDIA_ROOT
    path = 'img/' + good_filename(filename)
    print(path)
    return path


class SongFileInput(models.Model):
    '''This model is for uploading audio files. It consists of the filename,
      dance type, and holiday (if any) '''
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
    
    def __str__(self):
        return self.audio_file.url + ": " + self.dance_type
    
    
class SpotifyTrackInput(models.Model):
    '''This model is for uploading spotify preview auido. It consists of the track URI,
      dance type, and holiday (if any) '''
    track_URI = models.CharField(max_length=100) 
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
    
    def __str__(self):
        return self.track_URI + ": " + self.dance_type 
    

class Song(models.Model):
    '''This the model for a song in our music database.
       The music itself is either in a filename or link to the file. 
       The metadata (artist and title) are stored.
       There is also an image filename for the cover art.
       Finally, the dance_type is also stored.'''
    
    audio_file = models.FileField(blank=True, null=True)
    spotify_track_id = models.CharField(max_length=50,blank=True, null=True) 
    
    # these will be created from the audio_file
    title = models.CharField(max_length=200,default="Unknown")
    artist = models.CharField(max_length=200,default="Unknown")
    image = models.ImageField(upload_to=create_valid_image_filename, null=True)
    image_link = models.CharField(max_length=200,blank=True, null=True) 
    

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
        
    def __str__(self):
        return self.title