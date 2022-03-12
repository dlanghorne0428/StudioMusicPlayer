from django.shortcuts import render
from django.core.paginator import Paginator

# imported our models
from App.models.song import Song
from App.filters import SongFilter
from App.models.playlist import Playlist

def all_songs(request):
    ''' shows all the Songs in the database. '''

    # get the filtered list of Songs, ordered by title 
    songs = SongFilter(request.GET, queryset=Song.objects.all().order_by('title'))  
    
    playlists = None
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_teacher:
            # get all playlists owned by the current user
            playlists = Playlist.objects.filter(owner=request.user).order_by('title')  
    
    # render the template
    return render(request, 'all_songs.html', 
                  {'filter': songs,
                   'songs': songs.qs,
                   'playlists': playlists
                  })
