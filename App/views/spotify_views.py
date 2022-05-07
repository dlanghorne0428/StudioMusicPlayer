from django.shortcuts import render, redirect
from django.conf import settings

from App.models import User
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotify_cred as cred 

CACHE_FOLDER = os.path.join(settings.MEDIA_ROOT, '.spotify_caches')


def spotify_root(request):
    '''This view coordinates spotify authorization for the user'''
    user = request.user
    cache_path = os.path.join(CACHE_FOLDER, user.username)
    
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=cache_path)
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=cred.client_ID, 
                                               client_secret= cred.client_SECRET, 
                                               redirect_uri=cred.redirect_url, 
                                               scope='user-read-currently-playing user-read-recently-played playlist-modify-private',
                                               cache_handler=cache_handler, 
                                               show_dialog=True)    
    
    if request.GET.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.GET.get("code"))
        return redirect('App:spotify_root')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)    

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not user.has_spotify_token:
        user.has_spotify_token = True
        user.save()
        
    return render(request, "spotify_home.html", {
        "spotify_user": spotify.me()["display_name"],
        })
        
    #return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           #f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           #f'<a href="/playlists">my playlists</a> | ' \
           #f'<a href="/currently_playing">currently playing</a> | ' \
           #f'<a href="/current_user">me</a>' \    


def spotify_sign_out(request):
    user = request.user
    cache_path = os.path.join(CACHE_FOLDER, user.username)
    
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(cache_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    
    if user.has_spotify_token:
        user.has_spotify_token = False
        user.save()
        
    return redirect('App:home')    
      
