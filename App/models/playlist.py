from django.db import models
from django.utils.text import get_valid_filename
from App.models.song import Song


class Playlist(models.Model):
    '''A playlist has a short title and longer description. 
      A many-to-many field is used to represent the list of songs.'''
    
    title = models.CharField(max_length=50)
    
    description = models.TextField(blank=True)
    
    # a playlist has many songs, a song can be in multiple playlists
    songs = models.ManyToManyField(Song, through='SongInPlaylist')
    
    # should the playlist automatically play the next track?
    auto_continue = models.BooleanField(default=True)

    # should the playlist have a maximum song duration?
    # if enabled, the volume will fade when the song hits this limit
    max_song_duration_in_sec = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    
class SongInPlaylist(models.Model):
    '''This model is used for the mapping of songs to playlists. 
      It also provides the ordering of songs within the playlist.'''
    
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    order = models.IntegerField()
    
    class Meta:
        unique_together = ['song', 'playlist', 'order']    
