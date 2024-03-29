from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.conf import settings

# imported our models
from App.models.song import Song
from App.filters import SongFilter
from App.models.playlist import Playlist, SongInPlaylist

import logging
logger = logging.getLogger("django")

import random

def show_song_stats(request, sort_field=0):
    ''' shows all the Songs in the database and their popularity stats. '''

    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    
    playlists = None
    
    if request.user.has_spotify_token:              
        # get the filtered list of Songs
        songs = Song.objects.exclude(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('title')            
        streaming = True
        page_title = "Popularity of Songs added from Spotify"
        logger.info("Displaying " + page_title)         
    else:
        # get the filtered list of Songs
        songs = Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('title')    
        page_title = "Popularity of Songs on this Device"
        streaming = False
        logger.info("Displaying " + page_title)   
    
    # calculate how many playlists each song is in
    playlist_counts = list()    
    for s in songs: 
        the_count = SongInPlaylist.objects.filter(song=s).count()
        playlist_counts.append(the_count)
        if the_count != s.num_playlists:
            s.num_playlists = the_count
            s.save()
             
    if sort_field == 1:         # NUM HATES
        songs = songs.order_by('-num_hates')
    elif sort_field == 2:       # NUM PLAYS
            songs = songs.order_by('-num_plays')    
    elif sort_field == 3:       # NUM PLAYLISTS
        songs = songs.order_by('-num_playlists')
    else:                       # NUM LIKES (Default)
        songs = songs.order_by('-num_likes')
            
    # render the template
    return render(request, 'show_song_stats.html', 
                  {'songs': songs,
                   'streaming': streaming,
                   'sort_field' : sort_field,
                   'page_title': page_title
                  })


def reset_song_stats(request):
    ''' resets the popularity stats for all songs in the database '''
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    
    if not (request.user.is_superuser):
        logger.warning(request.user.username + " not authorized to create playlists")
        return render(request, 'permission_denied.html') 
  
    if request.user.has_spotify_token:  
        streaming = True
        page_title = "Popularity of Songs added from Spotify"
        songs = Song.objects.exclude(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('title') 
        
    else:
        streaming = False
        page_title = "Popularity of Songs on local device"
        songs = Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('title')    
        
    logger.info("Resetting " + page_title) 
    playlist_counts = list()
    for s in songs:
        s.num_plays = 0
        s.num_likes = 0
        s.num_hates = 0
        s.save()
        playlist_counts.append(SongInPlaylist.objects.filter(song=s).count())

    # combine the lists in a tuple for template rendering      
    songs_and_pl_counts = zip(songs, playlist_counts)         
        
    # render the template
    return render(request, 'show_song_stats.html', 
                  {'songs_and_pl_counts': songs_and_pl_counts,
                   'streaming': streaming,
                   'sort_field' : 1,
                   'page_title': page_title
                  })    