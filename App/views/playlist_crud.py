from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator

import os
import json
import math
from base64 import b64encode
import random
from datetime import time

# imported our models
from App.models.song import Song, DANCE_TYPE_CHOICES, DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS, DANCE_TYPE_TEMPOS
from App.models.user import User
from App.models.playlist import Playlist, SongInPlaylist
from App.forms import PlaylistInfoForm, RandomPlaylistForm, PlaylistUploadForm


import logging
logger = logging.getLogger("django")

#########################################################
# Paylist CRUD, add, update, and delete Paylist objects #
#########################################################

def create_playlist(request, random=None):
    ''' allows the superuser or teacher to create a new playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to create playlists")
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
        new_playlist.category = 'Party'
        new_playlist.max_song_duration = time(minute=2, second=30)
        logger.info('Preparing to ' + page_title + ": " + new_playlist.title)
            
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
            logger.info(form.cleaned_data)
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
        

def create_playlist_from_json(request, json_filename="../../../Desktop/spring_showcase.json"):
    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to create playlists")
        return render(request, 'permission_denied.html')
    
    if request.method == "POST":
        form = PlaylistUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['file']

            json_data = ''
            for line in uploaded_file:
                json_data = json_data + line.decode()  # "str_text" will be of `str` type
        
            # create new playlist
            new_playlist = Playlist()
            # set playlist owner to current user
            user = request.user
            new_playlist.owner = user 
            new_playlist.title = form.cleaned_data['title'] 
            new_playlist.category = 'Show'
            new_playlist.max_song_duration = time(minute=1, second=15)
            new_playlist.streaming = False   # for now     
            new_playlist.save()
            
            logger.info("Converting JSON encoded data into Python dictionary")
            developer = json.loads(json_data) #json.load(read_file)    
            
            for h in developer['heats']:
                if h['dance_style'] in ['Mambo', 'Salsa']:
                    the_style = DANCE_TYPE_CHOICES[8][0]               
                else:
                    for d in DANCE_TYPE_CHOICES:
                        if h['dance_style'] == d[1]:
                            the_style = d[0]
                            break
                
                placeholder_song = Song.objects.get(title="{Placeholder}", dance_type=the_style)
                new_playlist.add_song(placeholder_song)          
                
                if 'feature' in h:
                    current_song = SongInPlaylist.objects.get(playlist=new_playlist, order=h['heat']-1)
                    current_song.feature = True
                    current_song.save()
            
            return redirect("App:edit_playlist", new_playlist.id)
        else:
            error = "Form data not valid"
            return render(request, "create_playlist_from_json.html", {'page_title': page_title, 'form': form, 'error': error})            
        
    else:  #GET
        form = PlaylistUploadForm()
        page_title = 'Specify title and select JSON file for new playlist'
        return render(request, "create_playlist_from_json.html", {'page_title': page_title, 'form': form})
    

def pick_random_song(playlist, dance_type=None, index=None):
    '''pick a random song of this dance type and add it to the playlist.'''
    
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
     
    for s in candidate_songs:
        # don't allow placeholder songs
        if s.title.startswith("{Place"):
            continue
        # prevent songs from taking two spots in the same playlist
        if s.playlist_set.filter(id=playlist.id).count() == 0:
            available_songs.append(s)
    
    if len(available_songs) == 0:
        logger.warning(dance_type + ": No more songs available")
        return False
    else:
        # pick a random song from the available list - all equal probability and add it to the playlist
        random_song = available_songs[random.randrange(len(available_songs))]
        if index is None:
            playlist.add_song(random_song)
            logger.info("Added " + str(random_song) + " to playlist " + str(playlist))
        else:
            playlist.replace_song(index, random_song)
            logger.info("Replace index " + str(index) + " with " + str(random_song) + " in playlist " + str(playlist))
        return True
    

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
            'playlist_length'            : 25,
            'prevent_back_to_back_styles': True,
            'prevent_back_to_back_tempos': True,
            'counts'                     : DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS,
        }
        
    if 'counts' not in preferences:
        preferences['counts'] = dict()
        for key in DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS:
            preferences['counts'][key] = DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS[key]
        preferences['playlist_length'] = 25
        del preferences['percentages']
    
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

        # get song_counts entered by the user from the form
        songs_remaining = dict()
        for key in DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS:
            if key in ("Sho", "gen"):
                songs_remaining[key] = 0
            else:
                form_field = '%s_songs' % (key, )
                songs_remaining[key] = form_data[form_field]
            
        # save the form inputs into the playlist            
        preferences['playlist_length'] = playlist_length
        preferences['prevent_back_to_back_styles'] = prevent_back_to_back_styles
        preferences['prevent_back_to_back_tempos'] = prevent_back_to_back_tempos
        preferences['counts'] = songs_remaining
        playlist.preferences = preferences
        playlist.save()
        
        # determine if the inputs should be saved as user's new default preferences
        if form_data['save_preferences']:
            user.preferences = preferences
            user.save()
    
        # initialize the random number generator
        random.seed()
        
        # initialize control variables    
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
                logger.warning("All weights are zero")
                random_choice = random.choices(population)
            else:
                # random choices will pick a style based on the weighted probability 
                random_choice = random.choices(population, relative_weights)
                
            # save the dance style selected and pick a random song of that style
            dance_style = random_choice[0]
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
    last_index = playlist.number_of_songs()
    
    # get the specific song object from the database
    song = get_object_or_404(Song, pk=song_id)    
    
    # add the song to the end of the playlist
    playlist.add_song(song)
    logger.info("Added " + str(song) + " to playlist " + str(playlist))
    
    # redirect to edit playlist page, showing new song at end of list
    return redirect('App:edit_playlist', playlist.id, last_index)


def add_random_song_to_playlist(request, playlist_id, dance_type):
    ''' add a song to the end of a playlist '''
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id) 
    last_index = playlist.number_of_songs()
    
    if dance_type == "Any" or dance_type in ("Sho", "gen"):
        dance_type = None
        
    # pick a random song of the requested type and add it to playlist
    pick_random_song(playlist, dance_type)
    
    # redirect to edit playlist page, showing new song at end of list
    return redirect('App:edit_playlist', playlist.id, last_index)


def copy_playlist(request, playlist_id):
    ''' allows the superuser to edit an existing playlist. '''    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to copy playlists")
        return render(request, 'permission_denied.html')    
    
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        # only owner or superuser is allowed to copy playlist
        if not (request.user.is_superuser or playlist.owner == request.user):
            logger.warning(request.user.username + " not authorized to copy playlist " + str(playlist))
            return render(request, 'permission_denied.html') 
        
        # create new playlist object and copy fields from existing playlist
        new_playlist = Playlist()
        new_playlist.title = "copy-" + playlist.title
        new_playlist.description = "Copy of " + playlist.description
        new_playlist.owner = playlist.owner
        new_playlist.streaming = playlist.streaming
        new_playlist.category = playlist.category
        new_playlist.max_song_duration = playlist.max_song_duration
        new_playlist.preferences = playlist.preferences
        new_playlist.save()
        
        # obtain list of songs in the playlist being copied
        song_list = playlist.songs.all().order_by('songinplaylist__order')
        
        # copy them to the new playlist in the same order
        for s in song_list:    
            new_playlist.add_song(s)
        
        return redirect('App:user_playlists')


def replace_playlist_songs(request, playlist_id):
    ''' allows the superuser to replace all songs in existing playlist. 
        the dance type order will remain the same.'''    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to copy playlists")
        return render(request, 'permission_denied.html')    
    
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        # only owner or superuser is allowed to replace the playlist songs
        if not (request.user.is_superuser or playlist.owner == request.user):
            logger.warning(request.user.username + " not authorized to replace playlist " + str(playlist))
            return render(request, 'permission_denied.html') 
                
        # obtain list of songs in the playlist
        song_list = playlist.songs.all().order_by('songinplaylist__order')
        
        # copy them to the new playlist in the same order
        index = 0
        for s in song_list:
            dance_type = s.dance_type
            pick_random_song(playlist, dance_type, index)
            index += 1
        
        return redirect('App:edit_playlist', playlist_id)


def shuffle_playlist(request, playlist_id):
    ''' allows the superuser to replace all songs in existing playlist. 
        the dance type order will remain the same.'''    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to copy playlists")
        return render(request, 'permission_denied.html')    
    
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        # only owner or superuser is allowed to replace the playlist songs
        if not (request.user.is_superuser or playlist.owner == request.user):
            logger.warning(request.user.username + " not authorized to replace playlist " + str(playlist))
            return render(request, 'permission_denied.html') 

        # obtain list of songs in the playlist
        song_list = playlist.songs.all().order_by('songinplaylist__order')
        
        for index in range(len(song_list)):
            dance_type = song_list[index].dance_type
            matches = list()
            for new_index in range(index+1,len(song_list)):
                if song_list[new_index].dance_type == dance_type:
                    matches.append(new_index)
            if len(matches) > 0:
                random_index = matches[random.randrange(len(matches))]
                logger.info("Swapping: " + str(index) + " with " + str(random_index))
                playlist.swap_songs(index, random_index)
                

        return redirect('App:edit_playlist', playlist_id)        
    

def pause_playlist(request, playlist_id, resume_index):
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to pause playlists")
        return render(request, 'permission_denied.html')
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        logger.info("Pausing playlist " + str(playlist) + " at index " + str(resume_index))
        playlist.resume_index = resume_index
        playlist.save()
                    
        # return to list of user playlists        
        return redirect('App:user_playlists')           
    

def delete_playlist(request, playlist_id):
    ''' allows the superuser to edit an existing playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to delete playlists")
        return render(request, 'permission_denied.html')
    else:        
        # get the specific playlist object from the database
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        if not (request.user.is_superuser or playlist.owner == request.user):
            logger.warning(request.user.username + " not authorized to delete playlist " + str(playlist))
            return render(request, 'permission_denied.html')   
        
        logger.info("Deleting playlist " + str(playlist))
        playlist.delete()
                    
        # return to list of user playlists        
        return redirect('App:user_playlists')          

 
def edit_playlist(request, playlist_id, start_index = 0):
    ''' allows the superuser to edit an existing playlist. '''
    
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to edit playlists")
        return render(request, 'permission_denied.html')
          
    # get the specific playlist object from the database
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    if not (request.user.is_superuser or playlist.owner == request.user):
        logger.warning(request.user.username + " not authorized to edit playlist " + str(playlist))
        return render(request, 'permission_denied.html')    
    
    # obtain list of songs in this playlist and its length
    songs_in_playlist = SongInPlaylist.objects.filter(playlist=playlist).order_by('order')
    playlist_length = len(songs_in_playlist)    
        
    if request.method == "GET":
 
        # get the URL parameters for command and index in string format
        command = request.GET.get('cmd')
        index_str = request.GET.get('index')
        new_index = 0
    
        # if there are URL parameters
        if command is not None:
            if index_str is None:
                index = 0
            else:
                # get the index, convert to integer
                logger.info('Editing Playlist - index is: ' + index_str)
                index = int(index_str)
                
            # get the song in the playlist and the requested info
            selected = SongInPlaylist.objects.get(playlist=playlist_id, order=index)
            logger.info("Editing Playlist - song is: " + str(selected.song))
            
            logger.info('Playlist edit command is: ' + command)       
                
            if command == 'delsong':
                playlist.delete_song(selected.song)
                    
            elif command == "replace-random":
                # find the dance style of the selected song
                dance_style = selected.song.dance_type
                # replace with a random song and indicate it for highlighting
                if dance_style in ("Sho", "gen"):
                    pick_random_song(playlist, index=index)                     
                else:
                    pick_random_song(playlist, dance_style, index) 
                new_index = index
                
            elif command == 'replace-select':
                # find the dance style of the selected song
                dance_style = selected.song.dance_type  
                logger.info("Replacing " + str(selected.song))
                # redirect to select a song
                return redirect('App:replace_song', playlist_id, index, dance_style)  
            
            elif command == 'feature':
                # toggle the feature field
                selected.feature = not(selected.feature)
                selected.save()
                new_index = index
                
            elif command == 'dragsong': 
                # get the new index (dragged position) and convert to integer
                new_index_str = request.GET.get('newIndex')
                logger.info('Dragging: new index is: ' + new_index_str)
                new_index = int(new_index_str)     
                # call method in playlist model to rearrange song order
                playlist.move_song(selected.song, index, new_index)  
                
                # adjust highlight index after dragging down
                if new_index > index:
                    new_index -= 1;
                    
            # redirect to this same view in order to remove the URL parameters 
            return redirect('App:edit_playlist', playlist_id, new_index)             
        
        # no URL parameters, render the template as is
        form = PlaylistInfoForm(instance=playlist, submit_title=None)
        return render(request, 'edit_playlist.html', {
            'playlist': playlist,
            'songs': songs_in_playlist,
            'dance_types': DANCE_TYPE_CHOICES,
            'form': form,
            'start_index': start_index,
        })

    else: # POST
        # obtain information from the submitted form
        form = PlaylistInfoForm(request.POST, instance=playlist, submit_title=None)
        if form.is_valid():
            logger.info(form.cleaned_data)
            form.save()
            
            # ensure the max song duration is appropriate for the playlist category
            if playlist.max_song_duration == time(minute=30):
                playlist.max_song_duration = None
                form.save()
                
                if playlist.category == 'Party' or playlist.category == 'Show':
                    my_error = playlist.get_category_display() + " playlists must have a song time limit."
                    logger.warning(my_error)
                    # ask the user to set a time limit
                    return render(request, 'edit_playlist.html', {
                        'playlist': playlist,
                        'songs': songs_in_playlist,
                        'dance_types': DANCE_TYPE_CHOICES,
                        'form': form,
                        'error': my_error, 
                    })
                
            elif playlist.category == 'Norm':
                my_error = "Correcting " + playlist.get_category_display() + " playlists to not have a song time limit"
                logger.warning(my_error)                
                playlist.max_song_duration = None
                form.save()                
                           
            # redirect to this same view 
            return redirect('App:edit_playlist', playlist_id)
        
        else: 
            my_error = "Invalid data submitted."
            logger.warning(my_error)
            # display error on form
            return render(request, 'edit_playlist.html', {
            'playlist': playlist,
            'songs': songs_in_playlist,
            'dance_types': DANCE_TYPE_CHOICES,
            'form': form,
            'error': my_error
        })
               
            
        