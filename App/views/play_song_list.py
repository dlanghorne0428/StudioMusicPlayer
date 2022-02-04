from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models.song import Song
from App.models.playlist import Playlist

# Create your views here

def play_song_list(request, playlist_id):
    ''' Play the selected playlist.'''
    
    # only admin users can play songs
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')  
    
    # get the requested playlist or show "not found" page
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    # obtain list of songs in this playlist
    song_list = playlist.songs.all().order_by('songinplaylist__order')
    
    # build list of indices for the playlist
    playlist_indices = []
    for i in range(len(song_list)):
        playlist_indices.append(i)
    
    # convert max_duration to seconds for javascript player
    if playlist.max_song_duration is not None:
        max_song_duration_in_sec = playlist.max_song_duration.minute * 60 + \
                                   playlist.max_song_duration.second
    else:
        max_song_duration_in_sec = None
    
    # pass the path to the default cover art for any songs that don't have art 
    default_url = settings.STATIC_URL + "img/default.png"
    
    # render the template
    return render(request, "play_song_list.html", {
        'playlist_info': playlist, 
        'song_list':song_list, 
        'max_song_duration_in_sec': max_song_duration_in_sec,
        'default_url': default_url,
        "playlist_indices": playlist_indices})   
