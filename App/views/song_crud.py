from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.text import slugify

import os
import logging
logger = logging.getLogger("django")

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
        logger.warning(request.user.username + " not authorized to add songs")
        return render(request, 'permission_denied.html')
    
    if request.method == "GET":   # display empty form
        return render(request, 'add_song.html', {'form':SongFileInputForm()})
    
    else:  # process data submitted from the form
        form = SongFileInputForm(request.POST, request.FILES)
        
        # if form data invalid, display an error on the form
        if not form.is_valid():
            my_error = "Invalid data submitted."
            logger.warning(my_error)
            return render(request, 'add_song.html', {'form': form, 'error': my_error})
        
        # save the song instance into the database and get the path to the audio file uploaded by the form
        content_type = request.FILES['audio_file'].content_type
        song_instance = form.save() 
        logger.debug("Saving " + str(form.cleaned_data))
        audio_file_path = song_instance.audio_file.path
    
        # process file with mutagen and determine file type
        metadata = mutagen.File(audio_file_path)
        if metadata is None:
            my_error = "Invalid file type."
            logger.warning(my_error)
            return render(request, 'add_song.html', {'form': form, 'error': my_error}) 
        else:
            logger.debug(str(metadata.mime))
            artist = 'Unknown Artist'
            title = 'Unknown Title'
            pict = None
        
        if ("audio/mp4" in metadata.mime):
            logger.debug("MP4 metadata")
            mp4_data = MP4(audio_file_path)
            info = mp4_data.info
            tags = mp4_data.tags

            # get the artist, title, duration and picture from MP4 tags
            if tags is not None:
                artist = tags.get("\xa9ART")[0]
                title = tags.get("\xa9nam")[0]
                if tags.get("covr") is None:
                    logger.info("No cover art in file")
                else:
                    pict = tags.get("covr")[0]
            
        elif ("audio/mp3" in metadata.mime):
            logger.debug("MP3 metadata")
            id3_data = EasyID3(audio_file_path)
            
            # get the artist, title, duration and picture from MP3 tags
            if 'artist' in id3_data:
                artist = id3_data["artist"][0]

            if 'title' in id3_data:
                title = id3_data["title"][0]

            info = metadata.info
            duration =  info.length #seconds
            tags = ID3(audio_file_path)
            apic_list = tags.getall("APIC")
            if len(apic_list) == 0:
                logger.info("No cover art in file")
            else:
                pict = apic_list[0].data 
                
        elif content_type == 'audio/x-wav':
            logger.debug("WAV metadata " + str(metadata))
        
            # get the artist, title, duration from ID3 tags, WAV files have no cover art
            if 'TPE1' in metadata:
                artist_frame = metadata['TPE1']
                artist = artist_frame.text[0]

            if 'TIT2' in metadata:
                title_frame = metadata['TIT2']
                title = title_frame.text[0]
            
            logger.debug(artist +  ' ' + str(title))   
        
        elif content_type == 'video/ogg' or content_type == 'audio/ogg':
            logger.debug("OGG metadata " + str(metadata))
            if 'artist' in metadata:
                artist = metadata['artist'][0]

            if 'title' in metadata:
                title = metadata['title'][0]
                
            logger.debug(artist +  ' ' + str(title))  
        
        elif content_type == 'audio/flac':
            my_error = "Debugging FLAC audio"
            logger.debug("FLAC metadata " + str(metadata))
            
            if 'artist' in metadata:
                artist = metadata['artist'][0]

            if 'title' in metadata:
                title = metadata['title'][0]            
            flac_data = mutagen.flac.FLAC(audio_file_path)

            pict = flac_data.pictures[0].data

            logger.debug(artist +  ' ' + str(title))            
            
        else:  # if some other file type, return an error. 
            my_error = "Unknown audio file type " + str(content_type)
            logger.info("Unknown audio " + str(metadata))
            logger.warning(my_error)
            return render(request, 'add_song.html', {'form': form, 'error': my_error})
        
        # create a new Song object
        new_song = Song()
        
        # save the audio file, metadata, dance_type, and holiday/theme
        new_song.audio_file = song_instance.audio_file
        new_song.title = title
        new_song.artist = artist
        new_song.dance_type = song_instance.dance_type
        new_song.holiday = song_instance.holiday
        
        # determine name for the image file based on the name of the audio file
        basename = os.path.basename(new_song.audio_file.url)
        filename, ext = os.path.splitext(basename)
        new_basename = filename + '.jpg'
        relative_pathname = 'img/' + new_basename
        logger.debug("Image file is " + relative_pathname)
        
        if pict is None:
            # download cover art and save into "img" subfolder under MEDIA_ROOT
            folder = os.path.join(settings.MEDIA_ROOT, 'img')
            logger.info("Attempting to download cover art")
            finder = CoverFinder({'art-dest': folder, 
                                  'art-dest-filename': new_basename,
                                  })
            finder.scan_file(audio_file_path)
            # if cover art not found online, use default image
            if len(finder.files_skipped) > 0 or len(finder.files_failed) > 0:
                logger.warning("Could not download cover art for " + new_basename)
                relative_pathname = None
            
        else:
            # extract cover art from file and save in an "img" subfolder under MEDIA_ROOT
            im = Image.open(BytesIO(pict))
            logger.debug('Picture size : ' + str(im.size))
            logger.debug('Format:' + im.format)
            # assume JPEG cover art
            if im.format == "JPEG":
                path = os.path.join(settings.MEDIA_ROOT, relative_pathname)
                im.save(path)
            else:
                my_error = "Cover art was not JPEG."
                logger.warning (my_error + " Format is " + im.format)
                return render(request, 'add_song.html', {'form': form, 'error': my_error})                

        # save the path to the image file and save the Song object
        if relative_pathname is None:
            new_song.image = None
        elif len(relative_pathname) > 0:
            new_song.image = relative_pathname
        else:
            new_song.image = None
        new_song.save()
        
        # if bad metadata, redirect to update_song, allowing user to edit
        if new_song.title.lower() == "unknown title" or \
           new_song.artist.lower() in ("unknown artist", "soundtrack"):
            logger.warning("Unknown title or artist - redirecting to edit page")
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
        logger.warning(request.user.username + " not authorized to update songs")
        return render(request, 'permission_denied.html')   
    
    # get the specific song object from the database
    song = get_object_or_404(Song, pk=song_id)
    
    if request.method == "GET":
        # display form with current data
        form = SongEditForm(instance=song)
        log_msg = "Updating "
        log_msg += "title: " + song.title + ' '
        log_msg += "artist: " + song.artist + ' '
        log_msg += "dance_type: " + song.dance_type + ' '
        log_msg += "holiday: " + song.holiday
        logger.info(log_msg)
        return render(request, 'update_song.html', {'form':form})
    else:
        # obtain information from the submitted form
        form = SongEditForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            logger.info(form.cleaned_data)
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
        logger.warning(request.user.username + " not authorized to delete songs")
        return render(request, 'permission_denied.html')   
    
    # find the specific song object
    song = get_object_or_404(Song, pk=song_id) 
    logger.info("Deleting " +  str(song))
    
    # find the playlists that use this song
    playlists = SongInPlaylist.objects.filter(song=song)
    
    # delete that song from the playlist
    for p in playlists:
        p.playlist.delete_song(song)
        logger.info("Removing song from " + p.playlist.title)
        
    # delete the audio and image files related to this Song
    if song.image is not None:
        if song.image == "":
            pass
        elif os.path.isfile(song.image.path):
            logger.info("Deleting image file :" + song.image.path)
            os.remove(song.image.path)
            
    if song.audio_file is not None:
        if song.audio_file == "":
            pass
        elif os.path.isfile(song.audio_file.path):
            logger.info("Deleting music file :" + song.audio_file.path)
            os.remove(song.audio_file.path)    
    
    # remove Song from database and redirect to song list. 
    song.delete()    
    return redirect('App:show_songs')