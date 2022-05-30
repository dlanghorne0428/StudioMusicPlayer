from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.text import slugify

import os

# imported our models
from App.models.song import Song
from App.models.playlist import SongInPlaylist
from App.forms import SongFileInputForm, SongEditForm

# Create your views here.
###################################################
# Song CRUD, add, update, and delete Song objects #
###################################################

def authorized(user):
    return user.is_authenticated and (user.is_superuser or user.is_teacher)
        

def add_song(request):
    ''' allows the superuser to enter a song into the database. '''
    
    import mutagen
    from io import BytesIO
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3
    from PIL import Image
    from get_cover_art import CoverFinder
    
    # must be an administrator or teacher to add songs
    if not authorized(request.user):
        return render(request, 'permission_denied.html')
    
    if request.method == "GET":   # display empty form
        return render(request, 'add_song.html', {'form':SongFileInputForm()})
    
    else:  # process data submitted from the form
        form = SongFileInputForm(request.POST, request.FILES)
        
        # if form data invalid, display an error on the form
        if not form.is_valid():
            return render(request, 'add_song.html', {'form':SongInputForm(), 'error': "Invalid data submitted."})
        
        # save the song instance into the database and get the path to the audio file uploaded by the form
        song_instance = form.save()  
        audio_file_path = song_instance.audio_file.path
    
        # process file with mutagen and determine file type
        metadata = mutagen.File(audio_file_path)
        print(metadata.mime)
        
        if ("audio/mp4" in metadata.mime):
            mp4_data = MP4(audio_file_path)
            info = mp4_data.info
            tags = mp4_data.tags

            # get the artist, title, duration and picture from MP4 tags
            artist = tags.get("\xa9ART")[0]
            title = tags.get("\xa9nam")[0]
            duration = info.length # seconds.
            if tags.get("covr") is None:
                pict = None
            else:
                pict = tags.get("covr")[0]
            
        elif ("audio/mp3" in metadata.mime):
            id3_data = EasyID3(audio_file_path)
            
            # get the artist, title, duration and picture from MP3 tags
            artist = id3_data["artist"][0]
            title = id3_data["title"][0]
            info = metadata.info
            duration =  info.length #seconds
            tags = ID3(audio_file_path)
            apic_list = tags.getall("APIC")
            if len(apic_list) == 0:
                pict = None
            else:
                pict = apic_list[0].data 
                
        else:  # if some other file type, return an error. 
            return render(request, 'add_song.html', {'form':SongInputForm(), 'error': "Invalid data submitted."})
        
        # create a new Song object
        new_song = Song()
        
        # save the audio file, metadata, dance_type, and holiday/theme
        new_song.audio_file = song_instance.audio_file
        new_song.title = title
        new_song.artist = artist
        new_song.dance_type = song_instance.dance_type
        new_song.holiday = song_instance.holiday
        
        # determine name for the image file based on the name of the audio file
        print(new_song.audio_file.url)
        basename = os.path.basename(new_song.audio_file.url)
        filename, ext = os.path.splitext(basename)
        new_basename = filename + '.jpg'
        relative_pathname = 'img/' + new_basename
        print(relative_pathname)
        
        if pict is None:
            # download cover art and save into "img" subfolder under MEDIA_ROOT
            folder = os.path.join(settings.MEDIA_ROOT, 'img')
            finder = CoverFinder({'art-dest': folder, 
                                  'art-dest-filename': new_basename,
                                  })
            finder.scan_file(audio_file_path)
            # if cover art not found online, use default image
            if len(finder.files_skipped) > 0 or len(finder.files_failed) > 0:
                relative_pathname = None
            
        else:
            # extract cover art from file and save in an "img" subfolder under MEDIA_ROOT
            im = Image.open(BytesIO(pict))
            print('Picture size : ' + str(im.size))
            print('Format:' + im.format)
            # assume JPEG cover art
            if im.format == "JPEG":
                path = os.path.join(settings.MEDIA_ROOT, relative_pathname)
                im.save(path)
            else:
                print (im.format)
                return render(request, 'add_song.html', {'form':SongInputForm(), 'error': "Cover art was not JPEG."})                

        # save the path to the image file and save the Song object
        new_song.image = relative_pathname
        new_song.save()
        
        # if bad metadata, redirect to update_song, allowing user to edit
        if new_song.title.lower() == "unknown title" or \
           new_song.artist.lower() in ("unknown artist", "soundtrack"):
            return redirect('App:update_song', new_song.id)
        else:
            # return to list of songs
            return redirect('App:show_songs')
    

def update_song(request, song_id):
    ''' allows the superuser to update information for a song into the database. 
       This does not change the metadata in the music file, only the model fields
       for the selected Song object''' 
    
    # must be an admin user or teacher to edit songs
    if not (request.user.is_superuser or request.user.is_teacher):
        return render(request, 'permission_denied.html')   
    
    # get the specific song object from the database
    song = get_object_or_404(Song, pk=song_id)
    
    if request.method == "GET":
        # display form with current data
        form = SongEditForm(instance=song)
        return render(request, 'update_song.html', {'form':form})
    else:
        # obtain information from the submitted form
        form = SongEditForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            # save the updated info and return to song list
            form.save() 
            return redirect('App:show_songs')
        else:
            # display error on form
            return render(request, 'update_song.html', {'form':SongEditForm(), 'error': "Invalid data submitted."})
    

def delete_song(request, song_id):
    ''' allows the superuser to remove a song from the database. 
        the music file and cover art are also deleted .'''
    
    # must be an admin user to delete songs
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')   
    
    # find the specific song object
    song = get_object_or_404(Song, pk=song_id) 
    
    # find the playlists that use this song
    playlists = SongInPlaylist.objects.filter(song=song)
    
    # delete that song from the playlist
    for p in playlists:
        p.playlist.delete_song(song)
        
    # delete the audio and image files related to this Song
    if song.image is not None:
        if song.image == "":
            pass
        elif os.path.isfile(song.image.path):
            os.remove(song.image.path)
            
    if song.audio_file is not None:
        if song.audio_file == "":
            pass
        elif os.path.isfile(song.audio_file.path):
            os.remove(song.audio_file.path)    
    
    # remove Song from database and redirect to song list. 
    print("Deleting " +  str(song))
    song.delete()    
    return redirect('App:show_songs')