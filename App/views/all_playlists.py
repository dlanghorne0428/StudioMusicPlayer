from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

# imported our models
from App.models.playlist import Playlist
from App.models.user import User

def all_playlists(request, user_id=None):
    ''' shows all the Playlists in the database. '''
    
    # assume there are no playlists
    page_obj = None
    
    # if there are any playlists
    if Playlist.objects.count() > 0:
        
        if user_id is None:
            # get all the playlists, ordered by title
            playlists = Playlist.objects.all().order_by('title')
        
        else:
            # find user based on id
            user = get_object_or_404(User, pk=user_id)
        
            # get the playlists owned by that user
            playlists = Playlist.objects.filter(owner=user).order_by('title')
        
        if len(playlists) > 0:
            # split the playlists into pages and get the requested page
            paginator = Paginator(playlists, 16)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
    
    # render the template
    return render(request, 'all_playlists.html', 
                  {'page_obj': page_obj})

