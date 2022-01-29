from django.shortcuts import render
from django.core.paginator import Paginator

# imported our models
from App.models.playlist import Playlist

def all_playlists(request):
    ''' shows all the Playlists in the database. '''
    
    show_admin_buttons = request.user.is_superuser
  
    if Playlist.objects.count() > 0:
        playlists = Playlist.objects.all().order_by('title')
        paginator = Paginator(playlists, 16)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    return render(request, 'all_playlists.html', {'page_obj': page_obj, 'show_admin_buttons': show_admin_buttons })

