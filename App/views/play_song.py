from django.shortcuts import render, get_object_or_404
from django.conf import settings

# imported our models
from App.models.song import Song
from App.views.spotify_views import spotify_token 

import logging
logger = logging.getLogger("django")


def play_song(request, song_id):
    ''' Play the selected song.'''
    
    # only admin users or teachers can play songs
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning("User not authorized to play songs")
        return render(request, 'permission_denied.html')  
    
    # get the requested song or show "not found" page
    song = get_object_or_404(Song, pk=song_id)
    
    # pass the path to the default cover art
    default_url = settings.STATIC_URL + "img/default.png"
    
    if song.spotify_track_id is not None:
        
        token_dict = spotify_token(request.user)
        if token_dict is None:
            logger.warning("Cannot stream song, user not signed into spotify")
            return render(request, 'not_signed_in_spotify.html')
        
        spotify_uris = list()
        spotify_uris.append(song.spotify_uri())
        logger.info("Streaming spotify song " + song.title)
                
        return render(request, "play_spotify_song.html", 
                  {'spotify_uris': spotify_uris,
                   'user_token': token_dict['access_token'],
                   'title': song.title,
                   'artist': song.artist,
                   'song_id': song.id,
                   'cover_art': song.image_link,
                   'wifi_enabled': settings.WIFI_ENABLED,
                   'dance_type': song.get_dance_type_display}
                  )    
    else:
        logger.info("playing local song " + song.title)
        # render the template
        return render(request, "play_song.html", 
                      {'song':song, 
                       'wifi_enabled': settings.WIFI_ENABLED,
                       'default_url': default_url}
                      )   
