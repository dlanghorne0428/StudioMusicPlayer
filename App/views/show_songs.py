from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.conf import settings

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
        page_title = "Songs added from Spotify"
        logger.info("Displaying " + page_title)        
        
        if song_id is None:       
            # get the filtered list of Songs, ordered by title 
            songs = SongFilter(request.GET, queryset=Song.objects.exclude(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('title')) 
        else:
            songs = SongFilter(request.GET, queryset=Song.objects.filter(pk=song_id));

        # get all playlists of streaming songs owned by the current user
        playlists = Playlist.objects.filter(owner=request.user, streaming=True).order_by('title')
        logger.info(request.user.username + " has " + str(len(playlists)) + " streaming playlists.")
        
    else:
        if song_id is None:
            songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}').order_by('title')) 
        else:
            songs = SongFilter(request.GET, queryset=Song.objects.filter(pk=song_id)) 
            
        page_title = "Songs on this Device"
        streaming = False
        logger.info("Displaying " + page_title)
        
        # get all local playlists owned by the current user
        playlists = Playlist.objects.filter(owner=request.user, streaming=False).order_by('title') 
        logger.info(request.user.username + " has " + str(len(playlists)) + " local playlists.")
    
    logger.info(request.method)
    if request.method == "GET":
        if request.GET.get('btn_play_all') is not None:
            logger.info('Play All button clicked')
            
            playlist_indices = list()
            for i in range(len(songs.qs)):
                logger.info(songs.qs[i])
                playlist_indices.append(i)
                
            default_url = settings.STATIC_URL + "img/default.png"
            
            return render(request, "play_song_list.html", {
                'playlist_info': {'id': None, 'category': 'Norm'},
                'song_list':songs.qs, 
                'start_index': 0,
                'max_song_duration_in_sec': None,
                'default_url': default_url,
                "playlist_indices": playlist_indices,
        })              
            
    # render the template
    return render(request, 'show_songs.html', 
                  {'filter': songs,
                   'songs': songs.qs,
                   'playlists': playlists,
                   'streaming': streaming,
                   'page_title': page_title
                  })


def replace_song(request, playlist_id, index, dance_type, song_id=None):
    
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    
    playlists = Playlist.objects.filter(pk=playlist_id)
    
    if song_id is None:
        if playlists[0].streaming:
            if dance_type == "gen":
                songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=False).order_by('title')) 
            else:
                songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=False, dance_type=dance_type).order_by('title'))    
        else:
            if dance_type == "gen":
                songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=True).order_by('title')) 
            else:
                songs = SongFilter(request.GET, queryset=Song.objects.filter(spotify_track_id__isnull=True, dance_type=dance_type).order_by('title')) 
            
        page_title = "Playlist " + playlists[0].title + ": Select new song for item " + str(index + 1)
        streaming = False
    
        # render the template
        return render(request, 'show_songs.html', {
            'filter': songs,
            'songs': songs.qs,
            'playlists': playlists,
            'streaming': streaming,
            'index': index + 1,
            'page_title': page_title
            })    
    
    else:
        new_song = Song.objects.get(pk=song_id)
        playlists[0].replace_song(index - 1, new_song)
        return redirect ("App:edit_playlist", playlists[0].id, index-1)


def show_songs_no_cover_art(request):
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')    
    
    playlists = None
    streaming = False
    page_title = "Songs without Cover Art"
    songs = Song.objects.filter(spotify_track_id__isnull=True).exclude(title='{Placeholder}')
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
     