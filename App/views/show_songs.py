from django.shortcuts import render, redirect
from django.core.paginator import Paginator

# imported our models
from App.models.song import Song
from App.filters import SongFilter
from App.models.playlist import Playlist

def show_songs(request, song_id = None):
    ''' shows all the Songs in the database. '''

    if not request.user.is_authenticated:
        return redirect('login')
    
    playlists = None
    
    if request.user.has_spotify_token:
        streaming = True
        
        if song_id is None:       
            # get the filtered list of Songs, ordered by title 
            songs = SongFilter(request.GET, queryset=Song.objects.exclude(spotify_track_id__isnull=True).order_by('title')) 
            page_title = "Songs added from Spotify"
        else:
            songs = SongFilter(request.GET, queryset=Song.objects.filter(pk=song_id));
            page_title="Track already added from Spotify"             

        # get all playlists of streaming songs owned by the current user
        playlists = Playlist.objects.filter(owner=request.user, streaming=True).order_by('title')  
        
    else:
        songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=True).order_by('title')) 
        page_title = "Songs on this Computer"
        streaming = False
        
        # get all local playlists owned by the current user
        playlists = Playlist.objects.filter(owner=request.user, streaming=False).order_by('title')         
        
    
    # render the template
    return render(request, 'show_songs.html', 
                  {'filter': songs,
                   'songs': songs.qs,
                   'playlists': playlists,
                   'streaming': streaming,
                   'page_title': page_title
                  })
