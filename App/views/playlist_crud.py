from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator

import os

# imported our models
from App.models.song import Song
from App.models.user import User
from App.models.playlist import Playlist, SongInPlaylist
from App.forms import PlaylistEditForm


#########################################################
# Paylist CRUD, add, update, and delete Paylist objects #
#########################################################

def create_playlist(request, sort_type=None):
    ''' allows the superuser or teacher to create a new playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    
    else:
        # create new playlist
        new_playlist = Playlist()
        
        # set playlist owner to current user
        user = request.user
        new_playlist.owner = user        
    
        if sort_type is None:

            # use a default title based on number of playlists currently owned by this user
            playlist_count = Playlist.objects.filter(owner=user).count()
            new_playlist.title = user.username + '-' + str(playlist_count + 1)
            print(new_playlist.title)
            
            # empty description
            new_playlist.description = ""

            # save playlist and return to list of user's playlists
            new_playlist.save()        
            return redirect('App:all_playlists', user.id)
        
    if sort_type == 0:
        # add all songs ordered by title
        all_songs = Song.objects.all().order_by('title')
        new_playlist.title = "Test: All Songs in Title Order"
        new_playlist.description = "This paylist contains all songs in the database, ordered by Title"
    else:
        # add all songs orederd by artist
        all_songs = Song.objects.all().order_by('artist')  
        new_playlist.title = "Test: All Songs in Artist Order"
        new_playlist.description = "This paylist contains all songs in the database, ordered by Artist"            
    
    new_playlist.save()
        
    # get all the songs and add them to the playlist one at a time    
    for song in all_songs:
        new_playlist.add_song(song)
    
    # return to list of user's playlists        
    return redirect('App:all_playlists', user.id)


def add_to_playlist(request, playlist_id, song_id):
    ''' add a song to the end of a playlist '''
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id) 
    
    # get the specific song object from the database
    song = get_object_or_404(Song, pk=song_id)    
    
    # add the song to the end of the playlist
    playlist.add_song(song)
    
    # redirect to edit playlist page, showing new song at end of list
    return redirect('App:edit_playlist', playlist.id)
    
    
def edit_playlist(request, playlist_id):
    ''' allows the superuser to edit an existing playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        if not (request.user.is_superuser or playlist.owner == request.user):
            return render(request, 'permission_denied.html')           
        
        # obtain list of songs in this playlist and its length
        song_list = playlist.songs.all().order_by('songinplaylist__order')
        playlist_length = len(song_list)
        
        # get the URL parameters for command and index in string format
        command = request.GET.get('cmd')
        index_str = request.GET.get('index')
        print(request.GET)
    
        # if there are URL parameters
        if command is not None:
            if index_str is None:
                index = 0
            else:
                # get the index, convert to integer
                print('index is: ' + index_str)
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
    
    
def edit_playlist_title (request, playlist_id):
    ''' allows the superuser to edit an existing playlist title. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        if not (request.user.is_superuser or playlist.owner == request.user):
            return render(request, 'permission_denied.html')           
                    
        if request.method == "GET":
            # display form with current data
            form = PlaylistEditForm(instance=playlist)
            return render(request, 'edit_playlist_title.html', {'form':form})
        else:
            # obtain information from the submitted form
            form = PlaylistEditForm(request.POST, instance=playlist)
            if form.is_valid():
                # save the updated info and return to song list
                form.save() 
                return redirect('App:all_playlists')
            else: 
                # display error on form
                return render(request, 'edit_playlist_title.html', {'form':PlaylistEditForm(), 'error': "Invalid data submitted."})            
            
            
        