from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.text import slugify

import os
import logging
logger = logging.getLogger("django")

# imported our models
from App.models.song import Song
from App.models.playlist import Playlist, SongInPlaylist
from App.forms import SongFileInputForm, SongEditForm

# Create your views here.
###################################################
# Song CRUD, add, update, and delete Song objects #
###################################################

def authorized(user):
    return user.is_authenticated and (user.is_superuser or user.is_teacher)


def image_filename(audio_filename):
    # determine name for the image file based on the name of the audio file
    basename = os.path.basename(audio_filename)
    filename, ext = os.path.splitext(basename)
    return filename + '.jpg'


def find_cover_art(audio_file, image_file_basename):
    from get_cover_art import CoverFinder
    
    folder = os.path.join(settings.MEDIA_ROOT, 'img')
    logger.info("Attempting to download cover art")
    finder = CoverFinder({'art-dest': folder, 
                          'art-dest-filename': image_file_basename,
                          'force': True,
                          'verbose': True,
                          'no-skip': True,
                          })
    finder.scan_file(audio_file)
    print('skipped: ' + str(finder.files_skipped))
    print('failed: ' + str(finder.files_failed))
    # if cover art not found online, use default image
    if len(finder.files_skipped) > 0 or len(finder.files_failed) > 0:
        logger.warning("Could not download cover art for " + image_file_basename)
        return None
    else:
        return 'img/' + image_file_basename
    

def add_song(request):
    ''' allows the superuser to enter a song into the database. '''
    
    import mutagen
    from io import BytesIO
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3
    from PIL import Image
    
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
            tempo = -1
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
                if tags.get("tmpo") is None:
                    logger.info("No tempo value in file")
                else:
                    temp = tags.get("tmpo")                
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
            tempo_list = tags.getall("TBPM")
            if len(tempo_list) == 0:
                logger.info("No tempo value in file")
            else:
                frame = tempo_list[0]
                tempo = +frame
                
        elif content_type == 'audio/x-wav':
            logger.debug("WAV metadata " + str(metadata))
        
            # get the artist, title, duration from ID3 tags, WAV files have no cover art
            if 'TPE1' in metadata:
                artist_frame = metadata['TPE1']
                artist = artist_frame.text[0]

            if 'TIT2' in metadata:
                title_frame = metadata['TIT2']
                title = title_frame.text[0]
                
            if 'TBPM' in metadata:
                tempo_frame = metadata['TBPM']
                tempo = tempo_frame.text[0]            
            
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
        
        # save the audio file, metadata, and dance_type
        new_song.audio_file = song_instance.audio_file
        new_song.title = title
        new_song.artist = artist
        new_song.dance_type = song_instance.dance_type
        new_song.tempo = tempo
        
        # determine name for the image file based on the name of the audio file
        image_basename = image_filename(new_song.audio_file.url)
        relative_pathname = 'img/' + image_basename
        logger.debug("Image file is " + relative_pathname)
        
        if pict is None:
            # download cover art and save into "img" subfolder under MEDIA_ROOT
            relative_pathname = find_cover_art(audio_file_path, image_basename)
            
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
            return redirect('App:show_songs', new_song.id)
    

def update_song(request, song_id):
    ''' allows the superuser to update information for a song into the database. 
       This does not change the metadata in the music file, only the model fields
       for the selected Song object''' 
    
    import webbrowser
    
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
        logger.info(log_msg)
        if song.image_link is None:
            print('Song image: ' + str(song.image))
            if song.image:
                cover_art = song.image.url
            else:
                cover_art = settings.STATIC_URL + 'img/default.png'
        else:
            cover_art = song.image_link
        return render(request, 'update_song.html', {'form':form, 'cover_art': cover_art, 'song_id': song.id})
    else:
        # obtain information from the submitted form
        form = SongEditForm(request.POST, request.FILES, instance=song)
        action = request.POST.get("find_artwork")
            
        if form.is_valid():
            logger.info(form.cleaned_data)
            # save the updated info and return to song list
            form.save() 
            
            if action == "Find Cover Art Online":
                image_basename = image_filename(song.audio_file.url)
                audio_path = os.path.join(settings.BASE_DIR, song.audio_file.url[1:])
                print(audio_path, image_basename)
                if find_cover_art(audio_path, image_basename) == None:
                    url = 'https://duckduckgo.com/?q='+ song.artist + ' '+ song.title + '&ia=web&iax=images&ia=images'
                    webbrowser.open(url)
                    # display error on form
                    return render(request, 'update_song.html', {
                        'form':form, 'cover_art': settings.STATIC_URL + 'img/default.png', 
                        'song_id': song.id, 'error': "Could not find cover art."})
                
            return redirect('App:show_songs', song.id)
        
        else:
            # display error on form
            return render(request, 'update_song.html', {
                'form':SongEditForm(), 'cover_art': settings.STATIC_URL + 'img/default.png', 'song_id': song.id,
                'error': "Invalid data submitted."})
    

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


def playlists_with_song(request, song_id):
    ''' allows a user to find all of their playlists containing a specific song.
        a superuser can look at all playlists for that song.'''
        
    
    # must be an admin user or teacher to find song in playlists
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to lookup song in playlists")
        return render(request, 'permission_denied.html')  
    
    # find this song
    song = get_object_or_404(Song, pk=song_id) 
    
    # find the playlists that use this song
    matches = SongInPlaylist.objects.filter(song=song)
    
    # build a list of matching playlists owned by the user or all if superuser
    playlists = list()
    indices = list()
    for m in matches:
        if (request.user == m.playlist.owner) or (request.user.is_superuser):
            playlists.append(m.playlist)
            indices.append(m.order)
            print(m.playlist, m.order)

    error = None
    
    # if song is only in one playlist, go to that playlist immediately
    if len(playlists) == 1:
        return redirect('App:edit_playlist', playlists[0].id, indices[0])
    
    # if song isn't in any playlists, include an error message
    elif len(playlists) == 0:
        error = "This song does not appear in any playlist"
    
    # combine the lists in a tuple for template rendering
    playlists_and_indices = zip(playlists, indices)
    
    # display the list of playlists containing the song
    return render(request, 'show_song_and_playlists.html', {
                'song': song, 'playlists_and_indices': playlists_and_indices,
                'page_title': "Find song in playlist",
                'finding': True,
                'error': error})

            
def playlists_without_song(request, song_id):    
    ''' allows a user to add a song to the end of any of their playlists that don't already have that song.
        a superuser add to any playlist.'''
    
    # must be an admin user or teacher to access playlists
    if not (request.user.is_superuser or request.user.is_teacher):
        logger.warning(request.user.username + " not authorized to access playlists")
        return render(request, 'permission_denied.html')  
    
    # find this song
    song = get_object_or_404(Song, pk=song_id)
    logger.debug('Selected Song: ' + str(song))
    
    # build a list of playlists owned by the user or all if superuser
    if request.user.is_superuser:
        playlists = Playlist.objects.all()
    else:
        playlists = Playlist.objects.filter(owner=request.user)        
    
    # look at either local or streaming playlists, not both
    if request.user.has_spotify_token:
        playlists = playlists.filter(streaming=True)
    else:
        playlists = playlists.filter(streaming=False)        
    
    # build a list of matching playlists that don't have this song
    matching_playlists = list()
    # the indices list is maintain compatibility with the playlists_with_song view
    indices = list()
    
    for p in playlists:
        if SongInPlaylist.objects.filter(song=song, playlist=p).count() == 0:
            matching_playlists.append(p)
            indices.append(p.songs.all().count())
            logger.debug("Playlist without song: " + str(p))
    
    # if there are no playlists that don't have this song, create an error message        
    error = None
    if len(matching_playlists) == 0:
        error = "There are no available playlists for this song"
  
    # combine the lists in a tuple for template rendering      
    playlists_and_indices = zip(matching_playlists, indices)
   
    # display the list of playlists that don't have this song
    return render(request, 'show_song_and_playlists.html', {
                'song': song, 'playlists_and_indices': playlists_and_indices, 
                'page_title': "Add song to end of playlist",
                'error': error})