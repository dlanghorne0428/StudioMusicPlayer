from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator

import os
import math
import random
from datetime import time

# imported our models
from App.models.song import Song, DANCE_TYPE_DEFAULT_PERCENTAGES, DANCE_TYPE_TEMPOS
from App.models.user import User
from App.models.playlist import Playlist, SongInPlaylist
from App.forms import PlaylistInfoForm, RandomPlaylistForm


#########################################################
# Paylist CRUD, add, update, and delete Paylist objects #
#########################################################

def create_playlist(request, random=None):
    ''' allows the superuser or teacher to create a new playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    
    # create new playlist
    new_playlist = Playlist()
    # set playlist owner to current user
    user = request.user
    new_playlist.owner = user 
    
    if request.method == "GET":
        # set variables differently for random playlists
        if random is not None:
            separator = '-random-'
            page_title = 'Create Random Playlist'
            submit_title = 'Continue'
        else:
            separator = '-'
            page_title = 'Create Empty Playlist'
            submit_title = 'Save'
            
        # use a default title based on number of playlists currently owned by this user
        playlist_count = Playlist.objects.filter(owner=user).count()
        new_playlist.title = user.username + separator + str(playlist_count + 1)
            
        # empty description
        new_playlist.description = ""
        
        # display form with current data
        form = PlaylistInfoForm(instance=new_playlist)
        return render(request, 'edit_playlist_info.html', {
                                'page_title': page_title, 
                                'submit_title': submit_title,
                                'form':form})        

    else:  # POST
        # obtain information from the submitted form
        form = PlaylistInfoForm(request.POST, instance=new_playlist) 
        if form.is_valid():                
            form.save() 
            
            # check for special value indicated no time limit
            if new_playlist.max_song_duration == time(minute=30):
                new_playlist.max_song_duration = None
                form.save()
            
            if random:
                # redirect to populate with random songs
                return redirect('App:build_random_playlist', new_playlist.id)
            else:
                # return to list of user's playlists   
                return redirect('App:all_playlists', user.id)
        else: 
            # display error on form
            return render(request, 'edit_playlist_info.html', {
                                    'page_title': page_title, 
                                    'form':PlaylistInfoForm(), 
                                    'error': "Invalid data submitted."})            
    


def build_random_playlist(request, playlist_id):
    ''' generates a random list of songs and adds them to the playlist '''
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    user = request.user
    
    # redirect if playlist is not empty
    if playlist.songs.all().count() > 0:
        print("Playlist Not Empty")
        return redirect('App:all_playlists', user.id)
    
    # if user has percentage preferences, use those, otherwise use defaults
    if user.percentage_preferences is None:
        percentage_preferences = DANCE_TYPE_DEFAULT_PERCENTAGES
    else:
        percentage_preferences = user.percentage_preferences
    
    if request.method == "GET":
        # build and render the random playlist form
        form = RandomPlaylistForm(prefs= percentage_preferences)
        return render(request, 'build_random_playlist.html', {
            'form': form, 
            'playlist': playlist,
        })
    
    else:  # POST
        submit = request.POST.get("submit")
        # if user hit cancel button during build random, delete playlist that was in process of being created. 
        if submit == "Cancel": 
            playlist.delete()
            return redirect('App:all_playlists', user.id) 
        
        # obtain data from form and make sure it is valid.
        form = RandomPlaylistForm(request.POST,prefs=percentage_preferences)
        if form.is_valid():
            form_data = form.cleaned_data
        else:
            # TODO: handle this error 
            print('invalid');
        
        # set variables based on form data    
        playlist_length = form_data['number_of_songs']
        prevent_back_to_back_styles = form_data['prevent_back_to_back_styles']
        prevent_back_to_back_tempos = form_data['prevent_back_to_back_tempos']

        # get percentages entered by the user from the form
        starting_percentages = dict()
        for key in DANCE_TYPE_DEFAULT_PERCENTAGES:
            form_field = '%s_pct' % (key, )
            starting_percentages[key] = form_data[form_field]
            
        # determine if the inputs should be saved as user's new default percentages
        if form_data['save_preferences']:
            user.percentage_preferences = starting_percentages
            user.save()
    
        # initialize the random number generator
        random.seed()

        # calculate number of songs remaining for each style based on percentages and playlist length -- round up!
        songs_remaining = dict()
        for style in starting_percentages:
            songs_remaining[style] = math.ceil(starting_percentages[style] * playlist_length / 100)
            
        last_song_style = None
        
        # loop until the correct number of songs have been picked
        for index in range(playlist_length):
            
            # population is the list of dance styles, which are the keys of this songs_remaining dictionary 
            population = list(songs_remaining)
        
            # build the weights for the random choice function that will pick the style of the next song
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
        
            if relative_weights.count(0) == len(relative_weights):
                # if all the weights are zero, random.choices will pick a style at equal probability
                print("All weights are zero")
                random_choice = random.choices(population)
            else:
                # random choices will pick a style based on the weighted probability 
                random_choice = random.choices(population, relative_weights)
                
            # save the dance style selected
            dance_style = random_choice[0]
            
            # now find the songs in the database of this dance style
            available_songs = list()
            for s in Song.objects.filter(dance_type=dance_style):
                # prevent songs from taking two spots in the same playlist
                if s.playlist_set.filter(id=playlist.id).count() == 0:
                    available_songs.append(s)
            
            # pick a random song of this style - all equal probability and add it to the playlist
            random_song = available_songs[random.randrange(len(available_songs))]
            playlist.add_song(random_song)
            
            # decrement the number of remaining songs for that style and remember which style was chosen for next iteration
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
   
   
def delete_playlist(request, playlist_id):
    ''' allows the superuser to edit an existing playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        if not (request.user.is_superuser or playlist.owner == request.user):
            return render(request, 'permission_denied.html')           
        
        playlist.delete()
                    
        # return to list of all playlists        
        return redirect('App:all_playlists')          

 
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
    
    
def edit_playlist_info (request, playlist_id):
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
            form = PlaylistInfoForm(instance=playlist)
            return render(request, 'edit_playlist_info.html', {'form':form})
        else:
            # obtain information from the submitted form
            form = PlaylistInfoForm(request.POST, instance=playlist)
            if form.is_valid():
                # save the updated info and return to song list
                form.save() 
                if playlist.max_song_duration == time(minute=30):
                    playlist.max_song_duration = None
                form.save()
                return redirect('App:all_playlists')
            else: 
                # display error on form
                return render(request, 'edit_playlist_info.html', {'form':PlaylistInfoForm(), 'error': "Invalid data submitted."})            
            
            
        