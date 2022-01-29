from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

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
