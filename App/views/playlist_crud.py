from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator

import os

# imported our models
from App.models.song import Song
from App.models.playlist import Playlist, SongInPlaylist

# Create your views here.
#########################################################
# Paylist CRUD, add, update, and delete Paylist objects #
#########################################################

def create_playlist(request, sort_type):
    ''' allows the superuser to create a test playlist into the database. '''
    
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')
    else:
        new_playlist = Playlist()
        if sort_type == 0:
            all_songs = Song.objects.all().order_by('title')
            new_playlist.title = "Test - All in Title Order 1/28"
            new_playlist.description = "This paylist contains all songs in the database, ordered by Title"
        else:
            all_songs = Song.objects.all().order_by('artist')  
            new_playlist.title = "Test - All Songs - Artist Order 1/28"
            new_playlist.description = "This paylist contains all songs in the database, ordered by Artist"            
        new_playlist.save()
        
        # get all the songs and add them one at a time    
        index = 0
        for song in all_songs:
            new_playlist_entry = SongInPlaylist(
                song = song,
                playlist = new_playlist,
                order = index)
            new_playlist_entry.save()
            print(new_playlist.songs.all())
            index += 1
            
        return redirect('App:all_playlists')


def edit_playlist(request, playlist_id):
    ''' allows the superuser to edit an existing playlist. 
       TODO: there should be a playlist owner, who can edit their own playlists.'''
    
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')
    else:
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id )
        
        # obtain list of songs in this playlist
        song_list = playlist.songs.all().order_by('songinplaylist__order')
        
        # split the songs into pages and get the requested page
        paginator = Paginator(song_list, 16)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)        
        
        return render(request, 'edit_playlist.html', {
            'playlist': playlist,
            'page_obj': page_obj
        })  
    
def edit_playlist_move_up(request, playlist_id, index):
    ''' allows the superuser to edit an existing playlist. 
       The song at index is moved up one spot.
       TODO: there should be a playlist owner, who can edit their own playlists.'''
    
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    # obtain list of songs in this playlist
    song_list = playlist.songs.all
    
    print("index is: " + str(index))
    
    selected = SongInPlaylist.objects.get(playlist=playlist_id, order=index)
    print(selected.song)
    
    previous = SongInPlaylist.objects.get(playlist=playlist_id, order=index - 1)
    print(previous.song)
    
    selected.order = index - 1
    selected.save()    
    previous.order = index
    previous.save()
        
    return redirect('App:edit_playlist', playlist_id)


def edit_playlist_move_down(request, playlist_id, index):
    ''' allows the superuser to edit an existing playlist.
    The song at index is moved down one spot.
       TODO: there should be a playlist owner, who can edit their own playlists.'''
    
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    # obtain list of songs in this playlist
    song_list = playlist.songs.all
    
    print("index is: " + str(index))
    
    selected = SongInPlaylist.objects.get(playlist=playlist_id, order=index)
    print(selected.song)
    
    next = SongInPlaylist.objects.get(playlist=playlist_id, order=index + 1)
    print(next.song)
    
    selected.order = index + 1
    selected.save()    
    next.order = index
    next.save()
        
    return redirect('App:edit_playlist', playlist_id)


def edit_playlist_delsong(request, playlist_id, index):
    ''' allows the superuser to edit an existing playlist. 
    The song at index is deleted, all songs below move up one
       TODO: there should be a playlist owner, who can edit their own playlists.'''
    
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    # obtain list of songs in this playlist
    song_list = playlist.songs.all()
    
    print("index is: " + str(index))
    
    selected = SongInPlaylist.objects.get(playlist=playlist_id, order=index)
    print("deleting: " + str(selected.song))
    selected.delete()     
    
    for higher_index in range (index+1,len(song_list)):
        next = SongInPlaylist.objects.get(playlist=playlist_id, order=higher_index)
        next.order = higher_index - 1
        print(next.song, next.order)
        next.save()
        
    return redirect('App:edit_playlist', playlist_id)