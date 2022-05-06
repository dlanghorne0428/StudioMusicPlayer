from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models.song import Song

# Create your views here

def play_song(request, song_id):
    ''' Play the selected song.'''
    
    # only admin users or teachers can play songs
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')  
    
    # get the requested song or show "not found" page
    song = get_object_or_404(Song, pk=song_id)
    
    # pass the path to the default cover art
    default_url = settings.STATIC_URL + "img/default.png"
    
    if song.spotify_track_id is not None:
        return render(request, "play_spotify_song.html", 
                  {'song':song, 
                   'default_url': default_url}
                  )    
    else:
        # render the template
        return render(request, "play_song.html", 
                      {'song':song, 
                       'default_url': default_url}
                      )   
