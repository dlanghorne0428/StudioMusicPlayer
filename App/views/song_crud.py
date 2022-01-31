from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.text import slugify

import os

# imported our models
from App.models.song import Song
from App.forms import SongFileInputForm, SongEditForm

# Create your views here.
###################################################
# Song CRUD, add, update, and delete Song objects #
###################################################

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
    
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')

    if request.method == "GET":
        return render(request, 'add_song.html', {'form':SongFileInputForm()})
    else:
        form = SongFileInputForm(request.POST, request.FILES)
        if form.is_valid():
            pass; #print("Form is OK")
        else:
            return render(request, 'add_song.html', {'form':SongInputForm(), 'error': "Invalid data submitted."})
        
        song_instance = form.save()  
        audio_file_path = song_instance.audio_file.path
    
        metadata = mutagen.File(audio_file_path)
        print(metadata.mime)
        
        if ("audio/mp4" in metadata.mime):
            mp4_data = MP4(audio_file_path)
            info = mp4_data.info
            tags = mp4_data.tags

            artist = tags.get("\xa9ART")[0]
            title = tags.get("\xa9nam")[0]
            duration = info.length # seconds.
            if tags.get("covr") is None:
                pict = None
            else:
                pict = tags.get("covr")[0]
            
        elif ("audio/mp3" in metadata.mime):
            id3_data = EasyID3(audio_file_path)
            artist = id3_data["artist"][0]
            title = id3_data["title"][0]
            info = metadata.info
            duration =  info.length #seconds
            tags = ID3(audio_file_path)
            if tags.get("APIC:") is None:
                pict = None
            else:
                pict = tags.get("APIC:").data 
        else:
            return render(request, 'add_song.html', {'form':SongInputForm(), 'error': "Invalid data submitted."})
        
        new_song = Song()
        new_song.audio_file = song_instance.audio_file
        new_song.title = title
        new_song.artist = artist
        new_song.dance_type = song_instance.dance_type
        
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
            # save cover art in an "img" subfolder under MEDIA_ROOT
            im = Image.open(BytesIO(pict))
            print('Picture size : ' + str(im.size))
            print('Format:' + im.format)
            if im.format == "JPEG":
                path = os.path.join(settings.MEDIA_ROOT, relative_pathname)
                im.save(path)

        new_song.image = relative_pathname
        new_song.save()
        if new_song.title.lower() == "unknown title" or \
           new_song.artist.lower() in ("unknown artist", "soundtrack"):
            return redirect('App:update_song', new_song.id)
        else:
            return redirect('App:all_songs')
    

def update_song(request, song_id):
    ''' allows the superuser to update information for a song into the database. 
       This does not change the metadata in the music file, only the model fields
       for the selected Song object''' 
    
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')   
    
    song = get_object_or_404(Song, pk=song_id)
    
    if request.method == "GET":
        form = SongEditForm(instance=song)
        return render(request, 'update_song.html', {'form':form})
    else:
        form = SongEditForm(request.POST, instance=song)
        if form.is_valid():
            form.save() #print("Form is OK")
            return redirect('App:all_songs')
        else:
            return render(request, 'update_song.html', {'form':SongEditForm(), 'error': "Invalid data submitted."})
    

def delete_song(request, song_id):
    ''' allows the superuser to remove a song from the database. 
        the music file and cover art are also deleted .'''
    
    if not request.user.is_superuser:
        return render(request, 'permission_denied.html')   
    
    song = get_object_or_404(Song, pk=song_id) 
    if os.path.isfile(song.audio_file.path):
        os.remove(song.audio_file.path)
    if os.path.isfile(song.image.path):
        os.remove(song.image.path)
    print("Deleting " +  str(song))
    song.delete()    
    return redirect('App:all_songs')