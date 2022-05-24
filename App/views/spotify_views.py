from django.shortcuts import render, redirect
from django.conf import settings

from App.models import User
from App.models.song import Song, SpotifyTrackInput
from App.forms import SpotifyTrackInputForm, SpotifySearchForm

import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotify_cred as cred 

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

# declare the spotify_api at the module level 
this.spotify_api = None

# define the folder to cache spotify tokens
CACHE_FOLDER = os.path.join(settings.MEDIA_ROOT, '.spotify_caches')

                  
            
class Spotify_Api():
    ''' This class is a wrapper around the Spotipy library to access Spotify content'''
    
    def __init__(self, auth_manager, cache_handler, user):
        self.auth_manager = auth_manager
        self.cache_handler = cache_handler
        self.user = user
        self.spotify = spotipy.Spotify(auth_manager = self.auth_manager)
        
    def track_info_subset (self, spotify_track, album_name=None, cover_art=None):
        '''This function saves the information about a Spotify track needed by our app'''    
        new_track = dict()
        
        # populate main fields
        new_track['id'] = spotify_track['id']
        new_track['name'] = spotify_track['name']
        new_track['artist_name'] = spotify_track['artists'][0]['name']
        if 'album' in spotify_track: 
            new_track['album_name'] = spotify_track['album']['name']
            if len(spotify_track['album']['images']) > 0:
                new_track['cover_art'] = spotify_track['album']['images'][0]['url']
            else:
                new_track['cover_art'] = None
        else:
            new_track['album_name'] = album_name
            new_track['cover_art'] = cover_art
            
        features = self.spotify.audio_features(spotify_track['id'])
        new_track['tempo'] = round(features[0]['tempo'])
    
        # build a duration string
        seconds = round(spotify_track['duration_ms']/1000)
        minutes = seconds // 60
        seconds = seconds - (minutes * 60)
        new_track['duration'] = str(minutes) + ":" + "{:02d}".format(seconds)
        
        return new_track
    
    
    def album_info_subset (self, spotify_album):
        '''This function saves the information about a Spotify album needed by our app'''
        new_album = dict()
        new_album['id'] = spotify_album['id']
        new_album['album_name'] = spotify_album['name']
        new_album['artist_name'] = spotify_album['artists'][0]['name']
        if len(spotify_album['images']) > 0:
            new_album['cover_art'] = spotify_album['images'][0]['url']
        else:
            new_album['cover_art'] = settings.STATIC_URL + "img/default.png"
        return new_album
    
    
    def artist_info_subset (self, spotify_artist):
        '''This function saves the information about a Spotify artist needed by our app'''
        new_artist = dict()
        new_artist['id'] = spotify_artist['id']
        new_artist['artist_name'] = spotify_artist['name']
        if len(spotify_artist['images']) > 0:
            new_artist['artist_image'] = spotify_artist['images'][0]['url']
        else:
            new_artist['artist_image'] = settings.STATIC_URL + "img/default.png"
        return new_artist
    
    
    def playlist_info_subset (self, spotify_playlist):
        '''This function saves the information about a Spotify artist needed by our app'''
        new_playlist = dict()
        new_playlist['id'] = spotify_playlist['id']
        new_playlist['name'] = spotify_playlist['name']
        new_playlist['owner'] = spotify_playlist['owner']['display_name']   
        if len(spotify_playlist['images']) > 0:
            new_playlist['image'] = spotify_playlist['images'][0]['url']
        else:
            new_playlist['image'] = settings.STATIC_URL + "img/default.png"      
        return new_playlist        
        
    def current_username(self):
        return self.spotify.current_user()["display_name"]
    
    def recently_played_tracks(self, limit=16):
        items = self.spotify.current_user_recently_played()['items']
        unique_tracks = list()
        for item in items:
            for t in unique_tracks:
                if item['track']['id'] == t['id']:
                    break;
            else:  # this item is not in the track list
                new_track = self.track_info_subset(item['track'])
                unique_tracks.append(new_track)
            if len(unique_tracks) >= limit:
                break
            
        return unique_tracks

    def album_collection(self):
        items = self.spotify.current_user_saved_albums(limit=16)['items']
        album_list = list()
        for i in items:
            album_list.append(self.album_info_subset(i['album']))
        return album_list

    def playlist_collection(self):
        items = self.spotify.current_user_playlists(limit=16)['items']
        playlists = list()
        for i in items:
            playlists.append(self.playlist_info_subset(i))
        return playlists

    def artist_albums(self, artist_id):
        items = self.spotify.artist_albums(artist_id, limit=16)['items']
        album_list = list()
        for i in items:
            album_list.append(self.album_info_subset(i))
        return album_list  
    
    def album_tracks(self, album_id):
        album = self.spotify.album(album_id)
        tracks = album['tracks']['items']
        track_list = list()
        for track in tracks:
            track_list.append(self.track_info_subset(track, album['name'], album['images'][0]['url']))
        return track_list        
    
    def artists_followed(self):
        items = self.spotify.current_user_followed_artists(limit=16)['artists']['items']
        artist_list = list()
        for i in items:
            artist_list.append(self.artist_info_subset(i))
        return artist_list

    def artist_tracks(self, artist_id):
        tracks = self.spotify.artist_top_tracks(artist_id)['tracks']
        track_list = list()
        for track in tracks:
            track_list.append(self.track_info_subset(track))
        return track_list     
    
    def playlist_tracks(self, playlist_id):
        playlist = self.spotify.playlist(playlist_id)
        tracks = playlist['tracks']['items']
        track_list = list()
        for track in tracks:
            track_list.append(self.track_info_subset(track['track']))
        return track_list        
    
    def saved_tracks(self):        
        tracks = self.spotify.current_user_saved_tracks()['items']
        track_list = list()
        for track in tracks:
            track_list.append(self.track_info_subset(track['track']))
        return track_list  
    
    def track_info(self, track_id):
        track = self.spotify.track(track_id)
        return self.track_info_subset(track)
    
    def search(self, search_term, content_type):
        results = self.spotify.search(q=search_term, type=[content_type], limit = 16)
        
        if content_type == 'artist':
            artist_list = list()
            for artist in results['artists']['items']:
                artist_list.append(self.artist_info_subset(artist))
            return artist_list
        
        if content_type == 'album':
            album_list = list()
            for album in results['albums']['items']:
                album_list.append(self.album_info_subset(album))
            return album_list   
        
        if content_type == 'playlist':
            list_of_playlists = list()
            for playlist in results['playlists']['items']:
                list_of_playlists.append(self.playlist_info_subset(playlist))
            return list_of_playlists  

        if content_type == 'track':
            track_list = list()
            for track in results['tracks']['items']:
                track_list.append(self.track_info_subset(track))
            return track_list  
        
        return None
        
    
def spotify_token(user):
    '''
    This routine returns the user's spotify token for use by the audio player.
    If the user does not have a token, this function returns None
    '''
    if this.spotify_api is None:
        return None
    if user == this.spotify_api.user:    
        return this.spotify_api.cache_handler.get_cached_token()
    else:
        return None    

#################################################################
# DJANGO VIEWS TO ACCESS SPOTIFY RESORUCES                      #
#################################################################
def spotify_sign_in(request):
    '''This view coordinates spotify authorization for the user'''
    user = request.user
    
    # Step 1: initialize cache and authorization managers
    cache_path = os.path.join(CACHE_FOLDER, user.username)
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=cache_path)
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=cred.client_ID, 
                                               client_secret= cred.client_SECRET, 
                                               redirect_uri=cred.redirect_url, 
                                               scope="streaming, user-modify-playback-state, user-read-playback-state, user-read-currently-playing, user-read-recently-played, user-library-read user-follow-read playlist-modify-private",
                                               cache_handler=cache_handler, 
                                               show_dialog=True)    
    
    if request.GET.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.GET.get("code"))
        return redirect('App:spotify_sign_in')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)    

    # Step 4. Signed in, display list of user's recently played tracks
    this.spotify_api = Spotify_Api(auth_manager, cache_handler, user)
    if not user.has_spotify_token:
        user.has_spotify_token = True
        user.save()
        
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Your Recently Played Songs",
        "tracks": this.spotify_api.recently_played_tracks(),
        })  


def spotify_sign_out(request):
    '''This view signs a user out of Spotify'''
    user = request.user
    
    if this.spotify_api is not None:
        if user == this.spotify_api.user:
            # force the next user to start a new API
            this.spotify_api = None
            
    cache_path = os.path.join(CACHE_FOLDER, user.username)
    
    try:
        # Remove the CACHE file with the token so that a new user can authorize.
        os.remove(cache_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    
    if user.has_spotify_token:
        # clear the flag indicating that the user has a token
        user.has_spotify_token = False
        user.save()
        
    return redirect('App:home')    


def spotify_recently_played(request):
    '''This view displays a list of user's recently played tracks'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Your Recently Played Songs",
        "tracks": this.spotify_api.recently_played_tracks(),
        })      


def spotify_followed_artists(request):
    '''This view displays the Spotify artists followed by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    artists = this.spotify_api.artists_followed()
    
    return render(request, "spotify_artist_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'artist_list_description': "Your Followed Artists",
        "artist_list": artists,
        })      


def spotify_saved_albums(request):
    '''This view displays the Spotify albums saved by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    albums = this.spotify_api.album_collection()
    
    return render(request, "spotify_album_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'album_list_description': "Your Saved Albums",
        "album_list": albums,
        })      


def spotify_saved_playlists(request):
    '''This view displays the Spotify albums saved by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    playlists = this.spotify_api.playlist_collection()
    
    return render(request, "spotify_playlists.html", {
        "spotify_user": this.spotify_api.current_username(),
        'playlists_description': "Your Saved Playlists",
        "playlists": playlists,
        })      


def spotify_liked_songs(request):
    '''This view displays the Spotify songs liked by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    tracks = this.spotify_api.saved_tracks()
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Your Liked Songs",
        "tracks": tracks,
        })  


def spotify_search(request):
    '''This view displays the Spotify songs liked by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    if request.method == "GET":
        form = SpotifySearchForm()
        return render(request, "spotify_search.html", {'form': form})
        
    else:
        form = SpotifySearchForm(request.POST)
        if form.is_valid():
            st = form.cleaned_data['search_term']
            ct = form.cleaned_data['content_type']
            results = this.spotify_api.search(st, ct)
            
            if ct == 'artist':
                return render(request, "spotify_artist_list.html", {
                    "spotify_user": this.spotify_api.current_username(),
                    'artist_list_description': "Artists Matching - " + st,
                    "artist_list": results}) 
            
            if ct == 'album':
                return render(request, "spotify_album_list.html", {
                    "spotify_user": this.spotify_api.current_username(),
                    'artist_list_description': "Albums Matching - " + st,
                    "album_list": results})  
            
            if ct == 'playlist':
                return render(request, "spotify_playlists.html", {
                    "spotify_user": this.spotify_api.current_username(),
                    'playlists_description': "Albums Matching - " + st,
                    "playlists": results})  
            
            if ct == 'track':
                return render(request, "spotify_track_list.html", {
                    "spotify_user": this.spotify_api.current_username(),
                    'artist_list_description': "Tracks Matching - " + st,
                    "tracks": results})              
            
        else: 
            # display error on form
            return render(request, 'spotify_search.html', {
                'form': form,
                'error': "Invalid data submitted."})
      
      
def spotify_playlist_tracks (request, playlist_id):
    '''This view displays a list of tracks on a specific Spotify album'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    track_list = this.spotify_api.playlist_tracks(playlist_id)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Playlist Contents",
        "tracks": track_list,
        })      


def spotify_album_tracks (request, album_id):
    '''This view displays a list of tracks on a specific Spotify album'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    track_list = this.spotify_api.album_tracks(album_id)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Album Contents",
        "tracks": track_list,
        })      


def spotify_artist_tracks (request, artist_id):
    '''This view displays a list of tracks on a specific Spotify album'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    track_list = this.spotify_api.artist_tracks(artist_id)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Top Tracks by Artist",
        "tracks": track_list,
        })      


def spotify_artist_albums (request, artist_id):
    '''This view displays the albums by a specific Spotify artist'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    album_list = this.spotify_api.artist_albums(artist_id)
    
    return render(request, "spotify_album_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'album_list_description': "Albums by Artist",
        "album_list": album_list,
        })      


def add_spotify_track(request, track_id):
    '''This view adds a Spotify track into the Studio song database'''    
    from App.views.song_crud import authorized
    
    # must be an administrator or teacher to add songs
    if not authorized(request.user):
        return render(request, 'permission_denied.html')
    
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    track = this.spotify_api.track_info(track_id)
    image_link = track['cover_art']
    
    if request.method == "GET":   
        track_input = SpotifyTrackInput(
            track_id = track['id'], 
            title = track['name'],
            artist = track['artist_name'])
        
        form = SpotifyTrackInputForm(instance=track_input)
        return render(request, 'add_song.html', {'form': form, 'cover_art': image_link})    
    
    else:  # process data submitted from the form
        form = SpotifyTrackInputForm(request.POST)
    
        # if form data invalid, display an error on the form
        if not form.is_valid():
            return render(request, 'add_song.html', {'form':SpotifyTrackInputForm(), 'error': "Invalid data submitted."})  
        
        song_instance = form.save(commit=False)  
        
        # create a new Song object
        new_song = Song()
        
        # save the audio file, metadata, dance_type, and holiday/theme
        new_song.spotify_track_id = song_instance.track_id
        new_song.image_link = image_link
        new_song.title = song_instance.title
        new_song.artist = song_instance.artist
        new_song.dance_type = song_instance.dance_type
        new_song.holiday = song_instance.holiday
        new_song.save()
        print(new_song)
    
        # return to list of songs
        return redirect('App:all_songs')   