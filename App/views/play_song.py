from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models.song import Song
from App.views.spotify_views import spotify_token 

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
        
        token_dict = spotify_token(request.user)
        if token_dict is None:
            return render(request, 'not_signed_in_spotify.html')
        
        spotify_uris = list()
        spotify_uris.append(song.spotify_uri())
                
        return render(request, "play_spotify_song.html", 
                  {'spotify_uris': spotify_uris,
                   'user_token': token_dict['access_token'],
                   'title': song.title,
                   'artist': song.artist,
                   'cover_art': song.image_link,
                   'dance_type': song.get_dance_type_display}
                  )    
    else:
        # render the template
        return render(request, "play_song.html", 
                      {'song':song, 
                       'default_url': default_url}
                      )   
