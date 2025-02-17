from django.db import models
from django.utils.text import get_valid_filename
from App.models.song import Song
from App.models.user import User


CATEGORY_CHOICES = [
    ("Norm", "Normal"),     # no time limit per song, play next
    ("Party", "Party"),     # time limit per song, play next
    ("Show", "Showcase"),   # time limit per song, pause before next
    ]


class Playlist(models.Model):
    '''A playlist has a short title and longer description. 
      A many-to-many field is used to represent the list of songs.'''
    
    # a short title for the playlist
    title = models.CharField(max_length=50)
    
    # a longer description for the playlist
    description = models.TextField(blank=True)
    
    # the owner of the playlist will be allowed to edit and delete their playlist
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # if the songs in this playlist are streamed from Spotify, this field is True 
    streaming = models.BooleanField(default=False)

    # a playlist has many songs, a song can be in multiple playlists
    songs = models.ManyToManyField(Song, through='SongInPlaylist')

    # the category of this playlist - see category choices
    # is this playlist for a showcase or competition?
    category = models.CharField(
        max_length = 10,
        choices = CATEGORY_CHOICES, 
        default = 'Party'
    )

    # for Party or Showcase playlist, the time limit
    max_song_duration = models.TimeField(null=True, blank=True)
    
    # indicate which song to resume if the playlist is paused, Default of zero starts at the beginning
    resume_index = models.IntegerField(default=0)
    
    # this field stores the preferences used when to generate this playlist
    preferences = models.JSONField(null=True, blank=True)    
    
    
    def add_song(self, song, index=None):
        ''' add a song to the end of a playlist unless index is specified'''
        if index is None:
            index = self.songs.count()
        new_playlist_entry = SongInPlaylist(
            song = song,
            playlist = self,
            order = index,
            feature = False
        )
        new_playlist_entry.save()     
        
    
    def number_of_songs(self):
        ''' return the number of songs stored in the playlist'''
        return SongInPlaylist.objects.filter(playlist=self).count()
    
        
    def delete_song(self, song):
        ''' delete the specified song from the playlist'''
        
        # obtain the number of songs in this playlist
        playlist_length = self.number_of_songs()

        # get the selected song from the playlist, find its index and delete it
        selected = SongInPlaylist.objects.get(playlist=self, song=song)  
        index = selected.order
        selected.delete()
                
        # move all songs after the selected index up one slot
        for higher_index in range(index+1, playlist_length):
            next_index = SongInPlaylist.objects.get(playlist=self, order=higher_index)
            next_index.order = higher_index - 1
            #print(next_index.song, next_index.order)
            next_index.save()          


    def move_song(self, song, old_index, new_index):
        ''' move the specified song to the new index in the playlist'''
        
        # get the selected song from the playlist
        selected = SongInPlaylist.objects.get(playlist=self, song=song)  
        
        if old_index < new_index:
            # move all songs after the old index up one slot
            for temp_index in range(old_index, new_index-1):
                next_index = SongInPlaylist.objects.get(playlist=self, order=temp_index+1)
                next_index.order = temp_index
                #print(next_index.song, next_index.order)
                next_index.save()
            selected.order = new_index - 1
            selected.save()
            
        elif old_index > new_index:
            # move all songs above the old index down one slot            
            for temp_index in range(old_index, new_index, -1):
                prev_index = SongInPlaylist.objects.get(playlist=self, order=temp_index-1)
                prev_index.order = temp_index
                #print(prev_index.song, prev_index.order)
                prev_index.save()
            selected.order = new_index
            selected.save()    
            
        
    def replace_song(self, index, new_song):
        # get the selected index in the playlist
        target = SongInPlaylist.objects.get(playlist=self, order=index)
        target.song = new_song
        target.save()
        
        
    def swap_songs(self, index1, index2):
        # get the selected songs from the playlist
        target1 = SongInPlaylist.objects.get(playlist=self, order=index1)
        target2 = SongInPlaylist.objects.get(playlist=self, order=index2)
        
        target1.order = index2
        target2.order = index1
        
        target1.save()
        target2.save()
        

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
    
    
class SongInPlaylist(models.Model):
    '''This model is used for the mapping of songs to playlists. 
      It also provides the ordering of songs within the playlist.'''
    
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    
    # this is the position in the playlist
    order = models.IntegerField()
    
    # use this for solos, showcases, or special events - 
    # play the entire song even if there's a time limit for the playlist 
    feature = models.BooleanField(default=False)      
    
    class Meta:
        unique_together = ['song', 'playlist', 'order']  
        ordering = ['order']
