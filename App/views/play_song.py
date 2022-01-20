from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models import Song

# Create your views here

def play_song(request, song_id):
    ''' Play the selected song.'''
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')  
    
    song = get_object_or_404(Song, pk=song_id)
    return render(request, "play_song.html", {'song':song })   
