from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator

import os
import math
import random
from datetime import time

# imported our models
from App.models.song import Song, DANCE_TYPE_CHOICES, DANCE_TYPE_DEFAULT_PERCENTAGES, DANCE_TYPE_TEMPOS, HOLIDAY_DEFAULT_USAGE
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
    new_playlist.streaming = user.has_spotify_token
    
    # initialize submit_title
    submit_title = None
    
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
        
        # display form with current data, passing in submit_title
        form = PlaylistInfoForm(instance=new_playlist, submit_title=submit_title)
        return render(request, 'create_playlist.html', {
                                'page_title': page_title, 
                                'submit_title': submit_title,
                                'form':form})        

    else:  # POST
        # obtain information from the submitted form
        form = PlaylistInfoForm(request.POST, instance=new_playlist, submit_title=submit_title) 
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
                return redirect('App:user_playlists')
        else: 
            # display error on form
            return render(request, 'create_playlist.html', {
                                    'page_title': page_title, 
                                    'form':PlaylistInfoForm(), 
                                    'error': "Invalid data submitted."})            
    

def pick_random_song(playlist, dance_type, focus_holiday=None):
    '''pick a random song of this dance type and add it to the playlist.
      if focus_holiday is set, limit the choices to holiday songs of that type, if any.'''
    # initialize return variable
    missed_a_holiday_song = None
    
    # first find either the streaming songs or local songs iin the database 
    if playlist.streaming:
        candidate_songs = Song.objects.exclude(spotify_track_id__isnull=True)
    else:
        candidate_songs = Song.objects.filter(spotify_track_id__isnull=True)  
    
    # filter by dance type if necessary    
    if dance_type is not None:
        candidate_songs = candidate_songs.filter(dance_type=dance_type)
    
    # create a list for songs that match     
    available_songs = list()
    
    # if there is a focus holiday
    if focus_holiday:
        # apply another filter for only holiday songs
        holiday_candidates = candidate_songs.filter(holiday=focus_holiday)
        # add the holiday songs to the available songs list
        for s in holiday_candidates:
            # prevent songs that are already in this playlist
            if s.playlist_set.filter(id=playlist.id).count() == 0:
                available_songs.append(s)
        # if no holiday songs of this type, set missed flag to inform calling routine
        if len(available_songs) == 0:
            if dance_type is None:
                warn_msg = "No %s songs" % (focus_holiday, )
            else:
                warn_msg = "No %s songs for %s" % (dance_type, focus_holiday)
                print(warn_msg)                            
            missed_a_holiday_song = True
        else:
            missed_a_holiday_song = False
     
    # if we didn't add any holiday songs, consider all candidate songs            
    if len(available_songs) == 0:
        for s in candidate_songs:
            # don't allow songs from holidays that are excluded
            if s.holiday: 
                if playlist.preferences is None:
                    if HOLIDAY_DEFAULT_USAGE[s.holiday] == "Ex":
                        print("Excluding song: " + s.get_holiday_display())
                        continue
                elif playlist.preferences['holiday_usage'][s.holiday] == "Ex":
                    print("Excluding song: " + s.get_holiday_display())
                    continue
            # prevent songs from taking two spots in the same playlist
            if s.playlist_set.filter(id=playlist.id).count() == 0:
                available_songs.append(s)
    
    # pick a random song from the available list - all equal probability and add it to the playlist
    random_song = available_songs[random.randrange(len(available_songs))]
    playlist.add_song(random_song)
    
    # return indication that a requested holiday song was not selected
    return missed_a_holiday_song


def build_random_playlist(request, playlist_id):
    ''' generates a random list of songs and adds them to the playlist '''
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')
    
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    user = request.user
    
    # if playlist has preferences, use those
    if playlist.preferences is not None:
        preferences = playlist.preferences
    # if not, see if user has preferences
    elif user.preferences is not None:
        preferences = user.preferences
    else: # use system defaults as fallback
        preferences = {
            'playlist_length'            : 10,
            'prevent_back_to_back_styles': True,
            'prevent_back_to_back_tempos': True,
            'percentages'                : DANCE_TYPE_DEFAULT_PERCENTAGES,
            'holiday_usage'              : HOLIDAY_DEFAULT_USAGE,
        }
    
    if request.method == "GET":
        # build and render the random playlist form
        form = RandomPlaylistForm(prefs=preferences)
        return render(request, 'build_random_playlist.html', {
            'form': form, 
            'playlist': playlist,
            'user': user
        })
    
    else:  # POST
        cancel = request.POST.get("cancel")
        # if user hit cancel button during build random, delete playlist that was in process of being created. 
        if cancel == "Cancel":
            # if playlist is empty, delete it and redirect to user's playslist
            if playlist.songs.all().count() == 0:
                playlist.delete()
                return redirect('App:user_playlists')            
            else: # redirect to existing playlist
                return redirect('App:edit_playlist', playlist.id) 
        
        # obtain data from form and make sure it is valid.
        form = RandomPlaylistForm(request.POST,prefs=preferences)
        if form.is_valid():
            form_data = form.cleaned_data
        else:
            # TODO: handle this error 
            print('invalid');
        
        # if playlist is not empty, clear existing songs before re-generating
        if playlist.songs.all().count() > 0:
            songs_in_playlist = SongInPlaylist.objects.filter(playlist=playlist).order_by('order')
            for s in songs_in_playlist:
                s.delete()
            
        # set variables based on form data    
        playlist_length = form_data['number_of_songs']
        prevent_back_to_back_styles = form_data['prevent_back_to_back_styles']
        prevent_back_to_back_tempos = form_data['prevent_back_to_back_tempos']

        # get percentages entered by the user from the form
        starting_percentages = dict()
        for key in DANCE_TYPE_DEFAULT_PERCENTAGES:
            form_field = '%s_pct' % (key, )
            starting_percentages[key] = form_data[form_field]
            
        # get holiday usage data from the form and check if this is a holiday-focused playlist 
        focus_holiday = None
        focus_ratio = None
        holiday_usage = dict()
        for key in HOLIDAY_DEFAULT_USAGE:
            form_field = "%s_use" % (key, )
            holiday_usage[key] = form_data[form_field]  
            if holiday_usage[key].startswith("Ev"):
                focus_holiday = key
                focus_ratio = int(holiday_usage[key][-1])
            
        # save the form inputs into the playlist            
        preferences['playlist_length'] = playlist_length
        preferences['prevent_back_to_back_styles'] = prevent_back_to_back_styles
        preferences['prevent_back_to_back_tempos'] = prevent_back_to_back_tempos
        preferences['percentages'] = starting_percentages
        preferences['holiday_usage'] = holiday_usage
        playlist.preferences = preferences
        playlist.save()
        
        # determine if the inputs should be saved as user's new default preferences
        if form_data['save_preferences']:
            user.preferences = preferences
            user.save()
    
        # initialize the random number generator
        random.seed()

        # calculate number of songs remaining for each style based on percentages and playlist length -- round up!
        songs_remaining = dict()
        for style in starting_percentages:
            songs_remaining[style] = math.ceil(starting_percentages[style] * playlist_length / 100)
        
        # initialize control variables    
        last_song_style = None
        missed_a_holiday_song = False
        
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
            
            # if it is time for a holiday song, pass the holiday into the random song picker
            if focus_holiday and (index % focus_ratio == 0 or missed_a_holiday_song):
                missed_a_holiday_song = pick_random_song(playlist, dance_style, focus_holiday)
            else:  
                # pick any song of the required dance style
                missed_a_holiday_song == False
                pick_random_song(playlist, dance_style)
            
            # decrement the number of remaining songs for that style and remember which style was chosen for next iteration
            songs_remaining[dance_style] -= 1
            last_song_style = dance_style
        
        # redirect to show the playlist      
        return redirect('App:edit_playlist', playlist.id)


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


def add_random_song_to_playlist(request, playlist_id, dance_type):
    ''' add a song to the end of a playlist '''
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id) 
    
    if dance_type == "Any":
        dance_type = None
        
    # pick a random song of the requested type and add it to playlist
    pick_random_song(playlist, dance_type)
    
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
          
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    if not (request.user.is_superuser or playlist.owner == request.user):
        return render(request, 'permission_denied.html')    
    
    # obtain list of songs in this playlist and its length
    songs_in_playlist = SongInPlaylist.objects.filter(playlist=playlist).order_by('order')
    playlist_length = len(songs_in_playlist)    
        
    if request.method == "GET":
 
        # get the URL parameters for command and index in string format
        command = request.GET.get('cmd')
        index_str = request.GET.get('index')
    
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
                
            if command == 'delsong':
                playlist.delete_song(selected.song)
                    
            elif command == "replace-song":
                # find the dance style of the selected song
                dance_style = selected.song.dance_type
                
                # now find the songs in the database of this dance style
                candidate_songs = Song.objects.filter(dance_type=dance_style)
                available_songs = list()    
                
                for s in candidate_songs:
                    # TODO: consider holiday usage, when replacing a song
                    # prevent songs from taking two spots in the same playlist
                    if s.playlist_set.filter(id=playlist.id).count() == 0:
                        available_songs.append(s)  

                # pick a random song from the available list - all equal probability
                random_song = available_songs[random.randrange(len(available_songs))]
                # delete the original song, add the new one
                selected.delete()
                playlist.add_song(random_song, index)                
                
            elif command == 'feature':
                # toggle the feature field
                selected.feature = not(selected.feature)
                selected.save()
                
            elif command == 'dragsong': 
                # get the new index (dragged position) and convert to integer
                new_index_str = request.GET.get('newIndex')
                print('new index is: ' + new_index_str)
                new_index = int(new_index_str)     
                # call method in playlist model to rearrange song order
                playlist.move_song(selected.song, index, new_index)  
                
            # redirect to this same view in order to remove the URL parameters 
            return redirect('App:edit_playlist', playlist_id)             
        
        # no URL parameters, render the template as is
        form = PlaylistInfoForm(instance=playlist, submit_title=None)
        return render(request, 'edit_playlist.html', {
            'playlist': playlist,
            'songs': songs_in_playlist,
            'dance_types': DANCE_TYPE_CHOICES,
            'form': form,
        })

    else: # POST
        # obtain information from the submitted form
        form = PlaylistInfoForm(request.POST, instance=playlist, submit_title=None)
        if form.is_valid():
            form.save()
            
            # ensure the max song duration is appropriate for the playlist category
            if playlist.max_song_duration == time(minute=30):
                playlist.max_song_duration = None
                form.save()
                
                if playlist.category != 'Norm':
                    # ask the user to set a time limit
                    return render(request, 'edit_playlist.html', {
                        'playlist': playlist,
                        'songs': songs_in_playlist,
                        'dance_types': DANCE_TYPE_CHOICES,
                        'form': form,
                        'error': playlist.get_category_display() + " playlists must have a song time limit.", 
                    })
                           
            # redirect to show playlists
            return redirect('App:user_playlists')
        
        else: 
            # display error on form
            return render(request, 'edit_playlist.html', {
            'playlist': playlist,
            'songs': songs_in_playlist,
            'dance_types': DANCE_TYPE_CHOICES,
            'form': form,
            'error': "Invalid data submitted."
        })
               
            
        