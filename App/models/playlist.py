from django.db import models
from django.utils.text import get_valid_filename
from App.models.song import Song
from App.models.user import User


class Playlist(models.Model):
    '''A playlist has a short title and longer description. 
      A many-to-many field is used to represent the list of songs.'''
    
    # a short title for the playlist
    title = models.CharField(max_length=50)
    
    # a longer description for the playlist
    description = models.TextField(blank=True)
    
    # the owner of the playlist will be allowed to edit and delete their playlist
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # a playlist has many songs, a song can be in multiple playlists
    songs = models.ManyToManyField(Song, through='SongInPlaylist')
    
    # should the playlist automatically play the next track?
    auto_continue = models.BooleanField(default=True)

    # should the playlist have a maximum song duration?
    # if enabled, the volume will fade when the song hits this limit
    max_song_duration = models.TimeField(null=True, blank=True)
    
    def add_song(self, song):
        ''' add a song to the end of a playlist '''
        playlist_length = self.songs.count()
        new_playlist_entry = SongInPlaylist(
            song = song,
            playlist = self,
            order = playlist_length
        )
        new_playlist_entry.save()           

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
        ordering = ['order']
