from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models.functions import Lower

# imported our models
from App.models.playlist import Playlist
from App.models.user import User

def all_playlists(request, user_id=None):
    ''' shows all the Playlists in the database. '''
    
    # assume there are no playlists
    playlists = None
    page_title = "All Playlists"
    
    # if there are any playlists
    if Playlist.objects.count() > 0:
        
        if user_id is None:
            # get all the playlists, ordered by owner's username then title
            playlists = Playlist.objects.all().order_by(Lower('owner__username'), Lower('title'))
        
        else:
            # find user based on id
            user = get_object_or_404(User, pk=user_id)
        
            # get the playlists owned by that user and change the page title 
            playlists = Playlist.objects.filter(owner=user).order_by(Lower('title'))
            page_title = "My Playlists"
    
    # render the template
    return render(request, 'all_playlists.html', 
                  {'playlists': playlists,
                   'page_title': page_title})

