from django.shortcuts import render
from django.core.paginator import Paginator

# imported our models
from App.models.song import Song
from App.filters import SongFilter

def all_songs(request):
    ''' shows all the Songs in the database. '''
    
    # determine if the user is admin, pass that to template
    show_admin_buttons = request.user.is_superuser

    # get the filtered list of Songs, ordered by title 
    songs = SongFilter(request.GET, queryset=Song.objects.all().order_by('title'))   
    
    # split the songs into pages and get the requested page
    paginator = Paginator(songs.qs, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # render the template
    return render(request, 'all_songs.html', 
                  {'page_obj': page_obj, 
                   'filter': songs, 
                   'show_admin_buttons': show_admin_buttons })
