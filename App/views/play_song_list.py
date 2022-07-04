from django.shortcuts import render, get_object_or_404
from django.conf import settings

import os

# imported our models
from App.models.song import Song
from App.models.playlist import Playlist, SongInPlaylist
from App.views.spotify_views import spotify_token 

import logging
logger = logging.getLogger("django")


def play_song_list(request, playlist_id, start_index=0):
    ''' Play the selected playlist.'''
    
    # only admin users or teachers can play songs
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning("User not authorized to play song lists")
        return render(request, 'permission_denied.html')  
    
    # get the requested playlist or show "not found" page
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    logger.info("Preparing " + playlist.get_category_display() + " playlist: " + playlist.title)
    
    # obtain list of songs in this playlist
    song_list = playlist.songs.all().order_by('songinplaylist__order')
    
    # build list of indices for the playlist
    playlist_indices = []
    for i in range(len(song_list)):
        playlist_indices.append(i)
    
    # build a list that indicates if a song is featured in this playlist    
    is_feature_list = list()
    for song in song_list:
        song_in_playlist = SongInPlaylist.objects.get(song=song, playlist=playlist)
        if song_in_playlist.feature:
            logger.info(song_in_playlist.song.title + " is a feature song")
            is_feature_list.append(True)
        else:
            is_feature_list.append(False)
    
    # convert max_duration to seconds for javascript player
    if playlist.category == 'Norm':
        logger.info("No time limit on songs")
        max_song_duration_in_sec = None
    else:
        max_song_duration_in_sec = playlist.max_song_duration.minute * 60 + \
                                   playlist.max_song_duration.second
        logger.info("Song time limit is " + str(max_song_duration_in_sec))
    
    # pass the path to the default cover art for any songs that don't have art 
    default_url = settings.STATIC_URL + "img/default.png"
    
    if song_list[0].spotify_track_id:
        
        token_dict = spotify_token(request.user)
        if token_dict is None:
            logger.warning("Cannot stream playlist, user not signed into spotify")
            return render(request, 'not_signed_in_spotify.html')
        
        spotify_uris = list()
        for song in song_list:
            if song.spotify_track_id is not None:
                spotify_uris.append(song.spotify_uri())
                
            
        # render the template
        logger.info("Streaming spotify playlist " + playlist.title)
        return render(request, "play_list_spotify_songs.html", {
            'playlist_info': playlist, 
            'song_list': song_list, 
            "spotify_uris": spotify_uris,
            'start_index': start_index,
            'max_song_duration_in_sec': max_song_duration_in_sec,
            'default_url': default_url,
            'user_token': token_dict['access_token'],
            'is_feature_list': is_feature_list
        })          
    else:
        # render the template
        logger.info("Streaming local playlist " + playlist.title)
        return render(request, "play_song_list.html", {
            'playlist_info': playlist, 
            'song_list':song_list, 
            'start_index': start_index,
            'max_song_duration_in_sec': max_song_duration_in_sec,
            'default_url': default_url,
            "playlist_indices": playlist_indices,
            'is_feature_list': is_feature_list
        })   
