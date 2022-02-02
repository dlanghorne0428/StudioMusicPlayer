from django.shortcuts import render
from django.core.paginator import Paginator

# imported our models
from App.models.playlist import Playlist

def all_playlists(request):
    ''' shows all the Playlists in the database. '''
    
    # determine if the user is admin, pass that to template
    show_admin_buttons = request.user.is_superuser
    
    # if there are any playlists
    if Playlist.objects.count() > 0:
        
        # get all the playlists, ordered by title
        playlists = Playlist.objects.all().order_by('title')
        
        # split the playlists into pages and get the requested page
        paginator = Paginator(playlists, 16)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
    else:  # no playlists
        page_obj = None
    
    # render the template
    return render(request, 'all_playlists.html', 
                  {'page_obj': page_obj, 
                   'show_admin_buttons': show_admin_buttons })

