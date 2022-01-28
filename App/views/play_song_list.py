from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models import Song

# Create your views here

def play_song_list(request):
    ''' Play the selected song.'''
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')  
    
    # our list has all the songs in the database for now
    song_list = Song.objects.all().order_by('artist') 
    
    # build list of indices for the playlist
    playlist_indices = []
    for i in range(len(song_list)):
        playlist_indices.append(i)
    
    return render(request, "play_song_list.html", {'song_list':song_list, "playlist_indices": playlist_indices})   
