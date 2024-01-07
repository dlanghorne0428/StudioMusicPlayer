from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.conf import settings

# imported our models
from App.models.song import Song
from App.filters import SongFilter
from App.models.playlist import Playlist

import logging
logger = logging.getLogger("django")

import random

def show_song_stats(request, sort_field=1):
    ''' shows all the Songs in the database and their popularity stats. '''

    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    
    playlists = None
    
    if request.user.has_spotify_token:              
        # get the filtered list of Songs, ordered by the sort field selection
        if sort_field == 0:    # NUM PLAYS
            songs = Song.objects.exclude(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('-num_plays', 'title')
        elif sort_field == 2:  # NUM HATES
            songs = Song.objects.exclude(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('-num_hates', 'title')
        else:                  # NUM LIKES (Default)
            songs = Song.objects.exclude(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('-num_likes', 'title')            
        streaming = True
        page_title = "Popularity of Songs added from Spotify"
        logger.info("Displaying " + page_title)         
    else:
        # get the filtered list of Songs, ordered by the sort field selection
        if sort_field == 0:    # NUM PLAYS
            songs = Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('-num_plays', 'title')    
        elif sort_field == 2:  # NUM HATES
            songs = Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('-num_hates', 'title')            
        else:                  # NUM LIKES (Default)
            songs = Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('-num_likes', 'title')    
        page_title = "Popularity of Songs on this Device"
        streaming = False
        logger.info("Displaying " + page_title)            
            
    # render the template
    return render(request, 'show_song_stats.html', 
                  {'songs': songs,
                   'streaming': streaming,
                   'sort_field' : sort_field,
                   'page_title': page_title
                  })