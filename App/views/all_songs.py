from django.shortcuts import render
from django.core.paginator import Paginator

# imported our models
from App.models import Song
from App.filters import SongFilter

def all_songs(request):
    ''' shows all the Songs in the database. '''
    
    show_admin_buttons = request.user.is_superuser

    songs = SongFilter(request.GET, queryset=Song.objects.all().order_by('title'))   
    #songs = Song.objects.all().order_by('title')
    paginator = Paginator(songs.qs, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_songs.html', {'page_obj': page_obj, 'filter': songs, 'show_admin_buttons': show_admin_buttons })
