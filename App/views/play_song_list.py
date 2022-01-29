from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models.song import Song
from App.models.playlist import Playlist

# Create your views here

def play_song_list(request, playlist_id):
    ''' Play the selected song.'''
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')  
    
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    song_list = playlist.songs.all()
    
    # build list of indices for the playlist
    playlist_indices = []
    for i in range(len(song_list)):
        playlist_indices.append(i)
    
    return render(request, "play_song_list.html", {
        'playlist_title': playlist.title, 
        'song_list':song_list, 
        "playlist_indices": playlist_indices})   
