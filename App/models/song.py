from django.conf import settings
from django.db import models
from django.utils.text import get_valid_filename, slugify

from App.models.tag import Tag

import os
import logging
logger = logging.getLogger("django")

DANCE_TYPE_CHOICES = [
    ("Bchat", "Bachata"),
    ("Bolo", "Bolero"),    
    ("Cha", "Cha-Cha"), 
    ("C2S", "Country Two Step"), 
    ("ECS", "East Coast Swing"),
    ("Fox", "Foxtrot"),
    ("Hus", "Hustle"),
    ("Jive", "Jive"),
    ("Mam", "Mambo / Salsa"),
    ("Meren", "Merengue"),
    ("NC2", "Night Club 2-Step"),
    ("Paso",  "Paso Doble"),
    ("Pbody", "Peabody"),
    ("Qstep",   "Quickstep"),
    ("Rumba", "Rumba"),    
    ("Samba", "Samba"),
    ("Tango", "Tango"),  
    ("VWal",  "Viennese Waltz"),
    ("Waltz", "Waltz"),
    ("WCS", "West Coast Swing"),
    ("Show", "Showdance"),
    ("NoAlt", "N/A")
    ]

DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS = {
    "Bchat":  1,                  
    "Bolo":  2,        
    "Cha":  2, 
    "C2S":  1, 
    "ECS":  2,
    "Fox":  2,
    "Hus":  1,
    "Jive":  1,
    "Mam":  1,     
    "Meren":  1,     
    "NC2":  1,
    "Paso":   0,     
    "Pbody":  0,     
    "Qstep":    0,
    "Rumba":  2,    
    "Samba":  1,
    "Tango":  2,  
    "VWal":   2,
    "Waltz":  2,
    "WCS":  1,
    "Show":  0,
    "N/A":  0
    }

DANCE_TYPE_TEMPOS = {
    "Bchat": "Mid",                  
    "Bolo": "Slow",        
    "Cha": "Mid", 
    "C2S": "Mid",  
    "ECS": "Fast",
    "Fox": "Mid",
    "Hus": "Fast",  
    "Jive": "Fast",
    "Mam": "Fast",    
    "Meren": "Mid",    
    "NC2": "Slow",
    "Paso":  "Mid",   
    "Pbody": "Fast",    
    "Qstep":   "Fast",
    "Rumba": "Slow",    
    "Samba": "Mid",
    "Tango": "Mid",  
    "VWal":  "Fast",
    "Waltz": "Slow",
    "WCS": "Mid",
    "Show": "Mid",
    "N/A": "Mid"
    }


def good_filename(filename):
    '''slugify replaces whitespace with a dash and removes everything but alphanumerics,
       underscores and dashes.
       get_valid_filename finds an available filename to avoid duplicates.'''
    logger.debug("Initial filename is " + filename)
    temp_filename = get_valid_filename(filename)
    if temp_filename != filename:
        logger.debug("Good filename is " + temp_filename)
    filename, ext = os.path.splitext(temp_filename)
    filename = slugify(filename)
    if ext:
        return "%s.%s" % (filename, slugify(ext))
    else:
        return filename

    
def create_valid_filename(instance, filename):
    ''' When uploading audio files, find a valid name that django can use.'''
    # check if song file is already in the right folder
    current_dirname = os.path.dirname(filename)
    if current_dirname == settings.MEDIA_ROOT + 'music':
        return filename
    else:    
        # save music files in a "music" subfolder under MEDIA_ROOT
        path = 'music/' + good_filename(filename)
        return path


def create_valid_image_filename(instance, filename):
    ''' When uploading audio files, find a valid name that django can use.'''
    # check if image is already in the right folder
    current_dirname = os.path.dirname(filename)
    if current_dirname == settings.MEDIA_ROOT + 'img':
        return filename
    else:    
        # save image files in a "img" subfolder under MEDIA_ROOT
        path = 'img/' + good_filename(filename)
        print(path)
        return path


class SongFileInput(models.Model):
    '''This model is for uploading audio files. It consists of the filename and dance type.'''
    audio_file = models.FileField(upload_to=create_valid_filename)
    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )
    
    def __str__(self):
        return self.audio_file.url + ": " + self.dance_type
    
    
class SpotifyTrackInput(models.Model):
    '''This model is for uploading spotify preview auido. It consists of the track URI and dance type. '''
    track_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200,default="Unknown")
    artist = models.CharField(max_length=200,default="Unknown")   
    
    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )

    def __str__(self):
        return self.track_id + ": " + self.dance_type 
    

class Song(models.Model):
    '''This the model for a song in our music database.
       The music itself is either in a filename or link to the file. 
       The metadata (artist and title) are stored.
       There is also an image filename for the cover art.
       The tempo is stored in a BPM field.
       Statistics are kept on the number of plays, likes, and hates (dislikes).
       Finally, the dance_type is also stored.'''
    
    audio_file = models.FileField(blank=True, null=True)
    spotify_track_id = models.CharField(max_length=50,blank=True, null=True) 
    
    # these will be created from the audio_file
    title = models.CharField(max_length=200,default="Unknown")
    artist = models.CharField(max_length=200,default="Unknown")
    image = models.ImageField(upload_to=create_valid_image_filename, blank=True, null=True)
    image_link = models.CharField(max_length=200,blank=True, null=True) 
    explicit = models.BooleanField(default=False)
    
    # the song tempo in BPM will either be created from the audio file or read from Spotify
    bpm = models.IntegerField(default=-1)

    # number of times this song is played, liked, and hated
    num_plays = models.BigIntegerField(default=0)
    num_likes = models.BigIntegerField(default=0)
    num_hates = models.BigIntegerField(default=0)
    
    # number of playlists this song is a part of
    num_playlists = models.BigIntegerField(default=0)
    
    # a song can have many tags. Each tag can have several songs
    tags = models.ManyToManyField(Tag, through='Tagged_Song')

    # the dance type assigned to this song
    dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'Cha'
        )
    
    # an alternate dance type assigned to this song
    alt_dance_type = models.CharField(
        max_length = 10,
        choices = DANCE_TYPE_CHOICES,
        default = 'NoAlt'
        )    
    
    def spotify_uri(self):
        return "spotify:track:" + self.spotify_track_id
        
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
        
        
        
        
    
class Tagged_Song(models.Model):
    '''This model is used for the mapping of songs to tags. .'''
    
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    
    class Meta:
        unique_together = ['song', 'tag']  
        order_with_respect_to = "tag"