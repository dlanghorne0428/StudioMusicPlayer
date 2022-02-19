from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator

import os
import math
import random

# imported our models
from App.models.song import Song, DANCE_TYPE_DEFAULT_PERCENTAGES, DANCE_TYPE_TEMPOS
from App.models.user import User
from App.models.playlist import Playlist, SongInPlaylist
from App.forms import PlaylistEditForm


#########################################################
# Paylist CRUD, add, update, and delete Paylist objects #
#########################################################

def create_playlist(request):
    ''' allows the superuser or teacher to create a new playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    
    else:
        # create new playlist
        new_playlist = Playlist()
        
        # set playlist owner to current user
        user = request.user
        new_playlist.owner = user        
    

        # use a default title based on number of playlists currently owned by this user
        playlist_count = Playlist.objects.filter(owner=user).count()
        new_playlist.title = user.username + '-' + str(playlist_count + 1)
        print(new_playlist.title)
            
        # empty description
        new_playlist.description = ""

        # save playlist and return to list of user's playlists
        new_playlist.save()        
        return redirect('App:all_playlists', user.id)


def create_random_playlist(request):
    # user will able to enter their percentages and number of songs on a form
    # for now, use defaults
    starting_percentages = DANCE_TYPE_DEFAULT_PERCENTAGES
    songs_remaining = dict()
    playlist_length = 50
    random.seed()
    prevent_back_to_back_styles = True
    prevent_back_to_back_tempos = True
    
    # create new playlist
    new_playlist = Playlist()
    
    # set playlist owner to current user
    user = request.user
    new_playlist.owner = user  
    
    new_playlist.title = "Test Random 2"
    new_playlist.description = "first try of random list"
    new_playlist.save()
    
    for style in starting_percentages:
        songs_remaining[style] = math.ceil(starting_percentages[style] * playlist_length / 100)
        
    last_song_style = None
    
    for index in range(playlist_length):
        population = list(songs_remaining)
    
        relative_weights = list()
        for key in iter(songs_remaining):
            if last_song_style is None:
                # no restrictions on style
                relative_weights.append(songs_remaining[key])
            elif prevent_back_to_back_styles and key == last_song_style:
                # don't allow same dance twice in a row
                relative_weights.append(0)
            elif prevent_back_to_back_tempos and DANCE_TYPE_TEMPOS[last_song_style] == "Fast" and DANCE_TYPE_TEMPOS[key] == "Fast" :
                # don't allow two fast dances in a row
                relative_weights.append(0)
            elif prevent_back_to_back_tempos and DANCE_TYPE_TEMPOS[last_song_style] == "Slow" and DANCE_TYPE_TEMPOS[key] == "Slow" :
                # don't allow two slow dances in a row
                relative_weights.append(0)
            else:
                relative_weights.append(songs_remaining[key])
    
        print(relative_weights)
        if relative_weights.count(0) == len(relative_weights):
            print("All weights are zero")
            random_choice = random.choices(population)
        else:
            random_choice = random.choices(population, relative_weights)
        dance_style = random_choice[0]
        
        
        available_songs = list()
        for s in Song.objects.filter(dance_type=dance_style):
            # prevent songs from taking two spots in the same playlist
            if s.playlist_set.filter(id=new_playlist.id).count() == 0:
                available_songs.append(s)
        
        random_song = available_songs[random.randrange(len(available_songs))]
        
        print(index, dance_style, random_song)
        new_playlist.add_song(random_song)
        songs_remaining[dance_style] -= 1
        last_song_style = dance_style
    
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
            
            
        