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

def create_valid_filename(instance, filename):
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
    audio_file = models.FileField(upload_to=create_valid_filename)
    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )     
    
    def __str__(self):
        return self.audio_file.url + ": " + self.dance_type
    

# Create your models here.
class Song(models.Model):
    
    audio_file = models.FileField(blank=True, null=True)
    audio_link = models.CharField(max_length=200,blank=True, null=True) 
    
    # these will be created from the audio_file
    title = models.CharField(max_length=200,default="Unknown")
    artist = models.CharField(max_length=200,default="Unknown")
    image = models.ImageField(null=True)
    #duration=models.CharField(max_length=20)
    
    #paginate_by = 2
    
    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )        

    def __str__(self):
        return self.title