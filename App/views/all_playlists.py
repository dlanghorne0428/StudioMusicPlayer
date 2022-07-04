from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models.functions import Lower

# imported our models
from App.models.playlist import Playlist
from App.models.user import User

import logging
logger = logging.getLogger("django")

def show_playlists(user, owner_only=False):
    
    # assume there are no playlists
    playlists = None
    owner = None
    page_title = "No Playlists Found"
    
    # if there are any playlists
    if Playlist.objects.count() > 0:
        
        if owner_only:
            owner = user.username
            if user.has_spotify_token:
                # get the streaming playlists owned by that user and change the page title 
                playlists = Playlist.objects.filter(owner=user, streaming=True).order_by(Lower('title'))
                page_title = 'Playlists of Spotify tracks'
                logger.info("Listing the streaming playlists for " + user.username)
            else:
                # get the local playlists owned by that user and change the page title 
                playlists = Playlist.objects.filter(owner=user, streaming=False).order_by(Lower('title'))
                page_title = 'Playlists of Songs on this Device' 
                logger.info("Listing the local playlists for " + user.username)
                    
        else:
            if user.has_spotify_token:
                # get all the playlists, ordered by owner's username then title
                playlists = Playlist.objects.filter(streaming=True).order_by(Lower('owner__username'), Lower('title'))
                page_title = 'Playlists of Spotify tracks'
                logger.info("Listing the streaming playlists for all users")
            else:
                playlists = Playlist.objects.filter(streaming=False).order_by(Lower('owner__username'), Lower('title'))
                page_title = 'Playlists of Songs on this Device'              
                logger.info("Listing the local playlists for all users")
                
        return {'playlists': playlists,
            'page_title': page_title, 
            'owner': owner}


def all_playlists(request):
    ''' shows all the Playlists in the database. '''
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    else:
        playlist_data = show_playlists(request.user)
        # render the template
        return render(request, 'show_playlists.html', playlist_data)      
        

def user_playlists(request):
    ''' shows all the Playlists in the database. '''
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
    else:
        playlist_data = show_playlists(request.user, owner_only=True)
        # render the template
        return render(request, 'show_playlists.html', playlist_data)   