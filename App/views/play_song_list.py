from django.shortcuts import render, get_object_or_404
from django.conf import settings

import os

# imported our models
from App.models.song import Song
from App.models.playlist import Playlist, SongInPlaylist
from App.views.spotify_views import spotify_token 

# Create your views here

def play_song_list(request, playlist_id, start_index=0):
    ''' Play the selected playlist.'''
    
    # only admin users or teachers can play songs
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')  
    
    # get the requested playlist or show "not found" page
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
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
            is_feature_list.append(True)
        else:
            is_feature_list.append(False)
    
    # convert max_duration to seconds for javascript player
    if playlist.max_song_duration is not None:
        max_song_duration_in_sec = playlist.max_song_duration.minute * 60 + \
                                   playlist.max_song_duration.second
    else:
        max_song_duration_in_sec = None
    
    # pass the path to the default cover art for any songs that don't have art 
    default_url = settings.STATIC_URL + "img/default.png"
    
    if song_list[0].spotify_track_id:
        
        token_dict = spotify_token(request.user)
        if token_dict is None:
            return render(request, 'not_signed_in_spotify.html')
        
        spotify_uris = list()
        for song in song_list:
            if song.spotify_track_id is not None:
                spotify_uris.append(song.spotify_uri())
                
            
        # render the template
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
        return render(request, "play_song_list.html", {
            'playlist_info': playlist, 
            'song_list':song_list, 
            'start_index': start_index,
            'max_song_duration_in_sec': max_song_duration_in_sec,
            'default_url': default_url,
            "playlist_indices": playlist_indices,
            'is_feature_list': is_feature_list
        })   
