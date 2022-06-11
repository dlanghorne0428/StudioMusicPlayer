from django.shortcuts import render, redirect
from django.conf import settings

from App.models import User
from App.models.playlist import Playlist
from App.models.song import Song, SpotifyTrackInput, DANCE_TYPE_CHOICES
from App.forms import SpotifyTrackInputForm, SpotifySearchForm

import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from decouple import config

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

# declare the spotify_api at the module level 
this.spotify_api = None

# define the folder to cache spotify tokens
CACHE_FOLDER = os.path.join(settings.MEDIA_ROOT, '.spotify_caches')

                  
            
class Spotify_Api():
    ''' This class is a wrapper around the Spotipy library to access Spotify content'''
    
    def __init__(self, auth_manager, cache_handler, user):
        '''This app supports one spotify user at a time. 
           The auth_manager and cache_handler are passed in along with the Django user object
        '''
        self.auth_manager = auth_manager
        self.cache_handler = cache_handler
        self.user = user
        # initialize the API
        self.spotify = spotipy.Spotify(auth_manager = self.auth_manager)
        # this object caches the Spotify display name of the current user
        self.user_display_name = None

    #################################################################
    # CONVERSION METHODS FOR SPOTIFY CONTENT TO DJANGO MODELS 
    #################################################################
    def track_info_subset (self, spotify_track, album_name=None, cover_art=None):
        '''This function saves the information about a Spotify track needed by our app'''    
        new_track = dict()
        
        # populate main fields
        new_track['id'] = spotify_track['id']
        new_track['name'] = spotify_track['name']
        new_track['explicit'] = spotify_track['explicit']
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
            
        if spotify_track['id'] is None:
            new_track['tempo'] = "Unknown"
        else:
            features = self.spotify.audio_features(spotify_track['id'])
            new_track['tempo'] = round(features[0]['tempo'])
    
        # build a duration string
        seconds = round(spotify_track['duration_ms']/1000)
        minutes = seconds // 60
        seconds = seconds - (minutes * 60)
        new_track['duration'] = str(minutes) + ":" + "{:02d}".format(seconds)
        
        return new_track
    
    def track_list_info(self, tracks): 
        '''This method processes a list of spotify tracks and returns the required information 
           for each track. It also returns the offset, last, and total index fields, which
           can be used to get another page of tracks.'''
        track_list = list()
        for track in tracks['items']:
            if 'track' in track:
                track_list.append(self.track_info_subset(track['track']))
            else:
                track_list.append(self.track_info_subset(track))
        
        print('track filtering completed')
                
        return {'track_list': track_list,
                'first': tracks['offset'] + 1,
                'last' : tracks['offset'] + len(tracks['items']),
                'total': tracks['total']}
    
    
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
    
    def album_list_info(self, albums):
        '''This method processes a list of spotify albums and returns the required information 
           for each album. It also returns the offset, last, and total index fields, which
           can be used to get another page of albums.'''        
        album_list = list()
        for i in albums['items']:
            if 'album' in i:
                album_list.append(self.album_info_subset(i['album']))
            else:
                album_list.append(self.album_info_subset(i))
                
        print('album filtering completed')
        
        return {'album_list': album_list, 
                'first': albums['offset'] + 1, 
                'last' : albums['offset'] + len(albums['items']),
                'total': albums['total']}
    
    
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
    
    def artist_list_info (self, artists):
        '''This method processes a list of spotify artists and returns the required information 
           for each artist. It also returns the offset, last, and total index fields, which
           can be used to get another page of artists.'''        
        artist_list = list()
        for i in artists['items']:
            artist_list.append(self.artist_info_subset(i))
        
        print('Artist filtering completed')
        
        if 'offset' in artists: 
            return {'artist_list': artist_list,
                    'first': artists['offset'] + 1,
                    'last' : artists['offset'] + len(artists['items']),
                    'total': artists['total']}
        else:
            return {'artist_list': artist_list,                   
                    'first': 1,
                    'last' : len(artists['items']),
                    'total': artists['total']}
                                                 
    
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
        
        
    def info_for_playlists (self, playlists):
        '''This method processes a list of spotify playlists and returns the required information 
           for each playlist. It also returns the offset, last, and total index fields, which
           can be used to get another page of playlists.'''        
        list_of_playlists = list()
        for i in playlists['items']:
            list_of_playlists.append(self.playlist_info_subset(i)) 
            
        print ('playlist filtering complete')
        
        return {'list_of_playlists': list_of_playlists,
                'first': playlists['offset'] + 1,
                'last' : playlists['offset'] + len(playlists['items']),
                'total': playlists['total']}
    
        
    def current_username(self):
        '''This method returns the display name of the Spotify user.'''
        # if na name is saved, call Spotify to get the name
        if self.user_display_name is None:
            self.user_display_name = self.spotify.current_user()["display_name"]
        return self.user_display_name
    
    def recently_played_tracks(self, limit=16):
        '''This method returns the last 16 unique tracks played by the current user.'''
        items = self.spotify.current_user_recently_played(limit=25)['items']
        unique_tracks = list()
        for item in items:
            # check if this item is already in the list
            for t in unique_tracks:
                if item['track']['id'] == t['id']:
                    break;
            else:  # this item is not in the track list
                new_track = self.track_info_subset(item['track'])
                unique_tracks.append(new_track)
            # stop when track limit is readhed
            if len(unique_tracks) >= limit:
                break
            
        return unique_tracks

    def album_collection(self, offset=0):
        '''This method returns a list of albums saved in the current user's spotify library.'''
        albums = self.spotify.current_user_saved_albums(offset=offset, limit=16)
        return self.album_list_info(albums)
    
    def artists_followed(self):
        '''This method returns a list of the first 16 artists follwed by the current user.
           Note: the spotify API doesn't provide an offset or total fields for this oepration.'''        
        artists = self.spotify.current_user_followed_artists(limit=16)['artists']
        return self.artist_list_info(artists)    

    def playlist_collection(self):
        '''This method returns a list of playlists saved in the current user's spotify library.'''        
        playlists = self.spotify.current_user_playlists(limit=16)
        return self.info_for_playlists(playlists)
    
    def playlist_info(self, playlist_id):
        '''This method returns the information for a single spotify playlist.'''
        playlist = self.spotify.playlist(playlist_id)
        return self.playlist_info_subset(playlist)

    def saved_tracks(self, offset):        
        '''This method returns a list of tracks liked on Spotify the current user.'''               
        tracks = self.spotify.current_user_saved_tracks(offset=offset, limit=16)
        return self.track_list_info(tracks)

    def artist_albums(self, artist_id, offset=0):
        '''This method returns a list of up to 16 albums by a given artist.
           The offset parameter is used to get a different set of albums.''' 
        albums = self.spotify.artist_albums(artist_id, limit=16, offset=offset)
        return self.album_list_info(albums)
    
    def album_tracks(self, album_id):
        '''This method returns a list of all tracks on a given album.'''
        album = self.spotify.album(album_id)  # get the album
        tracks = album['tracks']['items']     # get the tracks from that album
        track_list = list()
        for track in tracks:
            # pass in the album name and cover art, as that info is not stored with each track
            track_list.append(self.track_info_subset(track, album['name'], album['images'][0]['url']))
        return {'track_list': track_list,
                'first': album['tracks']['offset'] + 1,
                'last' : album['tracks']['offset'] + len(album['tracks']['items']),
                'total': album['tracks']['total'] 
                }

    def artist_tracks(self, artist_id):
        '''This method returns a list of the top 10 tracks for a given artist.'''
        tracks = self.spotify.artist_top_tracks(artist_id)['tracks']
        track_list = list()
        for track in tracks:
            track_list.append(self.track_info_subset(track))
        return track_list     
    
    def playlist_tracks(self, playlist_id, offset):
        '''This method returns a list of up to 16 tracks from a given playlist.
           The offset parameter is used to get a different set of tracks.'''         
        tracks = self.spotify.playlist_tracks(playlist_id, offset=offset, limit=16)
        return self.track_list_info(tracks)   
    
    def track_info(self, track_id):
        '''This method returns the information for a single spotify track.'''
        track = self.spotify.track(track_id)
        return self.track_info_subset(track)
    
    def search(self, search_term, content_type, offset=0):
        '''This method searches spotify for items matching the given search term.
           The content_type can be 'album', 'artist', 'playlist', or 'track'.
           The offset parameter can be used to get additional pages of matching items.'''
        
        results = self.spotify.search(q=search_term, limit=16, offset=offset, type=content_type, market='US')
        print("spotify search returned")
        
        if content_type == 'artist':
            return self.artist_list_info(results['artists'])
        
        if content_type == 'album':        
            return self.album_list_info(results['albums'])
        
        if content_type == 'playlist':
            return self.info_for_playlists(results['playlists']) 

        if content_type == 'track':
            return self.track_list_info(results['tracks']) 
        
        return None
###########################################
# end of the Spotify_API class
###########################################
    
def spotify_token(user):
    '''This routine returns the user's spotify token for use by the audio player.
       If the user does not have a token, this function returns None.'''
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
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config('client_ID'), 
                                               client_secret= config('client_SECRET'), 
                                               redirect_uri=config('redirect_url'), 
                                               scope="streaming, user-modify-playback-state, user-read-playback-state, user-read-currently-playing, user-read-recently-played, user-library-read user-follow-read playlist-modify-private",
                                               cache_handler=cache_handler, 
                                               show_dialog=True)    
    
    #print("auth manager created")
    if request.GET.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.GET.get("code"))
        print("code obtained")
        return redirect('App:spotify_sign_in')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        #print("requesting authorization")
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)    

    # Step 4. Signed in, display list of user's recently played tracks
    this.spotify_api = Spotify_Api(auth_manager, cache_handler, user)
    #print("API initialized")
    if not user.has_spotify_token:
        user.has_spotify_token = True
        #print("saving token")
        user.save()
    
    #print("obtaining liked songs")
    tracks = this.spotify_api.saved_tracks(offset=0)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Your Liked Songs",
        "tracks": tracks['track_list'],
        "first" : tracks['first'],
        "last"  : tracks['last'],
        "total" : tracks['total']        
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
        "first" : 1,
        "last"  : 16,
        "total" : 16             
        })      


def spotify_followed_artists(request):
    '''This view displays the Spotify artists followed by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    artists = this.spotify_api.artists_followed()
    
    return render(request, "spotify_artist_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'artist_list_description': "Your Followed Artists",
        'artist_list': artists['artist_list'],
        'first': artists['first'],
        'last' : artists['last'],
        'total': artists['total']
        })      


def spotify_liked_songs(request):
    '''This view displays the Spotify songs liked by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0        
    
    tracks = this.spotify_api.saved_tracks(offset)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Your Liked Songs",
        "tracks": tracks['track_list'],
        "first" : tracks['first'],
        "last"  : tracks['last'],
        "total" : tracks['total']
        })  


def spotify_saved_albums(request):
    '''This view displays the Spotify albums saved by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0    
    
    albums = this.spotify_api.album_collection(offset)
    
    return render(request, "spotify_album_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'album_list_description': "Your Saved Albums",
        "album_list": albums['album_list'],
        "first": albums['first'],
        "last": albums['last'],
        "total": albums['total'],
        })     


def spotify_saved_playlists(request):
    '''This view displays the Spotify albums saved by the user'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    playlists = this.spotify_api.playlist_collection()
    
    return render(request, "spotify_playlists.html", {
        "spotify_user": this.spotify_api.current_username(),
        'playlists_description': "Your Saved Playlists on Spotify",
        "playlists": playlists['list_of_playlists'],
        "first": playlists['first'],
        "last" : playlists['last'],
        "total": playlists['total']        
        })      


def spotify_search(request):
    '''This view allows the user to search for Spotify content'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    if request.method == "GET":
        # display the form for the user to enter search options
        form = SpotifySearchForm()
        return render(request, "spotify_search.html", {'form': form})
        
    else:
        form = SpotifySearchForm(request.POST)
        if form.is_valid():
            # get data from the form
            st = form.cleaned_data['search_term']
            ct = form.cleaned_data['content_type']
            
            # redirect to the appropriate view. 
            # This redirect step allows the offset parameter to search for additional data 
            if ct == 'artist':
                return redirect('App:spotify_search_artists', st)
            
            if ct == 'album':
                return redirect('App:spotify_search_albums', st)
            
            if ct == 'playlist':
                return redirect('App:spotify_search_playlists', st)                    
            
            if ct == 'track':
                return redirect('App:spotify_search_tracks', st)                             
            
        else: 
            # display error on form
            return render(request, 'spotify_search.html', {
                'form': form,
                'error': "Invalid data submitted."})
        
        
def spotify_search_albums(request, search_term):
    '''This view obtains spotify albums that match the search term'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    # get the offset query parameter from the URL
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0      
    
    # get results using the spotify API    
    results = this.spotify_api.search(search_term, 'album', offset)
    
    # render those results
    return render(request, "spotify_album_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'album_list_description': "Albums Matching - " + search_term,
        "album_list": results['album_list'],
        "first": results['first'],
        "last":  results['last'],
        "total": results['total']})   

def spotify_search_artists(request, search_term):
    '''This view obtains spotify artists that match the search term'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    # get the offset query parameter from the URL    
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0      
    
    # get results using the spotify API           
    results = this.spotify_api.search(search_term, 'artist', offset)
    
    # render those results
    return render(request, "spotify_artist_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'artist_list_description': "Artists Matching - " + search_term,
        "artist_list": results['artist_list'],
        "first": results['first'],
        "last" : results['last'],
        "total": results['total']})     

def spotify_search_playlists(request, search_term):
    '''This view obtains spotify playlists that match the search term'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')

    # get the offset query parameter from the URL     
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0      
       
    # get results using the spotify API    
    results = this.spotify_api.search(search_term, 'playlist', offset)

    # render those results
    return render(request, "spotify_playlists.html", {
        "spotify_user": this.spotify_api.current_username(),
        'playlists_description': "Spotify Playlists Matching - " + search_term,
        "playlists": results['list_of_playlists'],
        "first": results['first'],
        "last":  results['last'],
        "total": results['total']})            

def spotify_search_tracks(request, search_term):
    '''This view obtains spotify tracks that match the search term'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    # get the offset query parameter from the URL         
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0      
    
    # get the offset query parameter from the URL      
    results = this.spotify_api.search(search_term, 'track', offset)

    # render those results
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'artist_list_description': "Tracks Matching - " + search_term,
        "tracks": results['track_list'],
        "first": results['first'],
        "last":  results['last'],
        "total": results['total']})               

      
def spotify_playlist_tracks (request, playlist_id):
    '''This view displays a list of tracks on a specific Spotify album'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0    
    
    tracks = this.spotify_api.playlist_tracks(playlist_id, offset)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Spotify Playlist Contents",
        "tracks"                : tracks['track_list'],
        "first"                 : tracks['first'],
        "last"                  : tracks['last'],
        "total"                 : tracks['total'],
        "playlist_id"           : playlist_id,
        "dance_types"           : DANCE_TYPE_CHOICES
        })      


def spotify_album_tracks (request, album_id):
    '''This view displays a list of tracks on a specific Spotify album'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    tracks = this.spotify_api.album_tracks(album_id)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Album Contents",
        "tracks": tracks['track_list'],
        "first" : tracks['first'],
        "last"  : tracks['last'],
        "total" : tracks['total']
        })      


def spotify_artist_tracks (request, artist_id):
    '''This view displays a list of tracks on a specific Spotify album'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    track_list = this.spotify_api.artist_tracks(artist_id)
    
    return render(request, "spotify_track_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'track_list_description': "Top Ten Tracks by Artist",
        "tracks": track_list,
        "first" : 1,
        "last"  : 10,
        "total" : 10           
        })      


def spotify_artist_albums (request, artist_id):
    '''This view displays the albums by a specific Spotify artist'''
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')
    
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0
    
    artist_albums = this.spotify_api.artist_albums(artist_id, offset)
    
    return render(request, "spotify_album_list.html", {
        "spotify_user": this.spotify_api.current_username(),
        'album_list_description': "Albums by Artist",
        "album_list": artist_albums['album_list'],
        "first": artist_albums['first'],
        "last": artist_albums['last'],
        "total": artist_albums['total'],
        })      


def add_spotify_track(request, track_id):
    '''This view adds a Spotify track into the Studio song database'''    
    from App.views.song_crud import authorized
    
    matching_song = Song.objects.filter(spotify_track_id = track_id)
    if matching_song.count() > 0:
        return redirect('App:show_songs', matching_song[0].id)
    
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
        return render(request, 'add_song.html', {'form': form, 'warning': track['explicit'], 'cover_art': image_link})    
    
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
        return redirect('App:show_songs')   
    
    
def add_spotify_playlist(request, spotify_playlist_id, dance_type_index):
    '''This view adds all the tracks from a Spotify playlist into the database and then creates
       a Playlist in the database with all of those tracks'''    
    from App.views.song_crud import authorized
        
    # must be an administrator or teacher to add songs
    if not authorized(request.user):
        return render(request, 'permission_denied.html') 
    
    if this.spotify_api is None:
        return render(request, 'not_signed_in_spotify.html')    
    
    spotify_playlist = this.spotify_api.playlist_info(spotify_playlist_id) 

    # create an empty playlist and fill in data
    new_playlist = Playlist()
    new_playlist.owner = request.user
    new_playlist.title = spotify_playlist['name']
    new_playlist.description = DANCE_TYPE_CHOICES[dance_type_index][1] + " by Spotify user: " + spotify_playlist['owner']
    new_playlist.streaming = True
    new_playlist.save()
    
    # initalize variables for reading in tracks
    offset = 0
    total = 1
    song_list = list()
    
    # while more tracks to read
    while offset < total:
        
        # get the next set of tracks
        tracks = this.spotify_api.playlist_tracks(spotify_playlist_id, offset=offset)
        
        # update variables for next iterations        
        total = tracks['total']
        offset = tracks['last']

        # for each track obtained
        for t in tracks['track_list']:
            
            # if track already in database, get its id
            matching_song = Song.objects.filter(spotify_track_id = t['id'])
            if matching_song.count() > 0:             
                print("MATCH", t['id'], t['name'])
                song_list.append(matching_song[0])
            else:
                # add track        
                new_song = Song()
            
                # save the metadata, dance_type, and holiday/theme
                new_song.spotify_track_id = t['id']
                new_song.image_link = t['cover_art']
                new_song.title = t['name']
                new_song.artist = t['artist_name']
                new_song.dance_type = DANCE_TYPE_CHOICES[dance_type_index][0]
                new_song.save()
                song_list.append(new_song)
    
    # add all the songs to the new playlist
    for song in song_list:            
        new_playlist.add_song(song)
    
    # show all the user's playlists    
    return redirect('App:user_playlists')
    
    
