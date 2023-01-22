from django.shortcuts import render, redirect
from django.core.paginator import Paginator

# imported our models
from App.models.song import Song
from App.filters import SongFilter
from App.models.playlist import Playlist

import logging
logger = logging.getLogger("django")


def show_songs(request, song_id = None):
    ''' shows all the Songs in the database. '''

    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    
    playlists = None
    
    if request.user.has_spotify_token:
        streaming = True
        
        if song_id is None:       
            # get the filtered list of Songs, ordered by title 
            songs = SongFilter(request.GET, queryset=Song.objects.exclude(spotify_track_id__isnull=True).order_by('title')) 
            page_title = "Songs added from Spotify"
            logger.info("Displaying " + page_title)
        else:
            songs = SongFilter(request.GET, queryset=Song.objects.filter(pk=song_id));
            page_title="Track already added from Spotify"  
            logger.warning(songs[0].title + " " + page_title)

        # get all playlists of streaming songs owned by the current user
        playlists = Playlist.objects.filter(owner=request.user, streaming=True).order_by('title')
        logger.info(request.user.username + " has " + str(len(playlists)) + " streaming playlists.")
        
    else:
        songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=True).order_by('title')) 
        page_title = "Songs on this Device"
        streaming = False
        logger.info("Displaying " + page_title)
        
        # get all local playlists owned by the current user
        playlists = Playlist.objects.filter(owner=request.user, streaming=False).order_by('title') 
        logger.info(request.user.username + " has " + str(len(playlists)) + " local playlists.")
        
    # render the template
    return render(request, 'show_songs.html', 
                  {'filter': songs,
                   'songs': songs.qs,
                   'playlists': playlists,
                   'streaming': streaming,
                   'page_title': page_title
                  })


def show_songs_no_cover_art(request):
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')    
    
    playlists = None
    streaming = False
    page_title = "Songs without Cover Art"
    songs = Song.objects.filter(spotify_track_id__isnull=True)
    no_art_songs = list()
    for s in songs:
        if not s.image:
            no_art_songs.append(s)
    
    # render the template
    return render(request, 'show_songs.html', 
                  {'songs': no_art_songs,
                   'playlists': playlists,
                   'streaming': streaming,
                   'showing_no_art': True,
                   'page_title': page_title
                  })
     