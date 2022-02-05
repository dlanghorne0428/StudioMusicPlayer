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
        
        # obtain list of songs in this playlist and its length
        song_list = playlist.songs.all().order_by('songinplaylist__order')
        playlist_length = len(song_list)
        
        # get the URL parameters for command and index in string format
        command = request.GET.get('cmd')
        index_str = request.GET.get('index')
        print(request.GET)
    
        # if there are URL parameters
        if index_str is not None and command is not None:
            print('index is: ' + index_str)
            # get the index, convert to integer
            index = int(index_str)
            # get the song in the playlist and the requested info
            selected = SongInPlaylist.objects.get(playlist=playlist_id, order=index)
            print(selected.song)
            
            print('command is: ' + command)       
            if command == 'up':
                # moving the selected song up one slot, so get song currently in that slot
                previous = SongInPlaylist.objects.get(playlist=playlist_id, order=index - 1)
                print(previous.song)
                
                # swap slots for selected and previous songs.
                selected.order = index - 1
                selected.save()    
                previous.order = index
                previous.save() 
                
            elif command == 'down':
                # moving the selected song down one slot, so get song currently in that slot
                next = SongInPlaylist.objects.get(playlist=playlist_id, order=index + 1)
                print(next.song)
                
                # swap slots for selected and next songs.
                selected.order = index + 1
                selected.save()    
                next.order = index
                next.save()    
                
            elif command == 'delsong':
                # remove the selected song from the list
                selected.delete()
                
                # move all songs after the selected index up one slot
                for higher_index in range(index+1, playlist_length):
                    next = SongInPlaylist.objects.get(playlist=playlist_id, order=higher_index)
                    next.order = higher_index - 1
                    print(next.song, next.order)
                    next.save()
                    
            # redirect to this same view in order to remove the URL parameters 
            return redirect('App:edit_playlist', playlist_id)             
        
        # no URL parameters, render the template as is
        return render(request, 'edit_playlist.html', {
            'playlist': playlist,
            'songs': song_list
        })  
    