from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models.functions import Lower

# imported our models
from App.models.song import Song, Tagged_Song
from App.models.tag import Tag
from App.forms import TagEntryForm

import logging
logger = logging.getLogger("django")


def show_tags(request):
    ''' shows all the Tags in the database. '''

    if not request.user.is_authenticated:
        logger.warning("User is not authenticated - redirect to login page")
        return redirect('login')
 
    tags = Tag.objects.all().order_by('title')
    button_title = "Add"
    
    if request.method == "GET":
        f = TagEntryForm()       
        
    else: 
        f = TagEntryForm(request.POST)
        if f.is_valid():
            tag_instance = f.save(commit=False)
            logger.info(tag_instance.title)
            if Tag.objects.filter(title=tag_instance.title).exists():  
                pass
            else:
                tag_instance.save()
        
    # render the template
    return render(request, 'show_tags.html', {
        'tags': tags, 
        'form': f, 
        'form_title': 'Create Tag',
        'button_title': 'Add',
    })       


def delete_tag(request, tag_id):
    ''' allows the superuser to remove a tag from the database.'''
    
    # must be an admin user to delete songs
    if not request.user.is_superuser:
        logger.warning(request.user.username + " not authorized to delete tags")
        return render(request, 'permission_denied.html')   
    
    # find the specific song object
    tag = get_object_or_404(Tag, pk=tag_id) 
    logger.info("Deleting " +  str(tag))  
    
    # remove Tag from database and redirect to tag list. 
    tag.delete()    
    return redirect('App:show_tags')


def edit_tag(request, tag_id):
    ''' allows the superuser to remove a tag from the database.'''
    
    # must be a valid user to delete songs
    if not request.user.is_authenticated:
        logger.warning(request.user.username + " not authorized to edit tags")
        return render(request, 'permission_denied.html')   
    
    # find the specific song object
    tag = get_object_or_404(Tag, pk=tag_id) 
    logger.info("Editing " +  str(tag))  
    
    tags = Tag.objects.all().order_by('title')
    
    if request.method == "GET":
        f = TagEntryForm(instance=tag)  
        form_title = 'Edit Tag'
        button_title = "Save"
        
    else: 
        f = TagEntryForm(request.POST)
        if f.is_valid():
            tag_instance = f.save(commit=False)
            logger.info(tag_instance.title)
            tag.title = tag_instance.title
            tag.save()
            form_title = 'Create Tag'
            button_title = "Add"
        
    # render the template
    return render(request, 'show_tags.html', {
        'tags': tags, 
        'form': f, 
        'form_title': form_title,
        'button_title': button_title,
        })       


def show_tags_for_song(request, song_id):
    ''' shows the current tags applied to a song and all other available tags'''    
    # must be a valid user to view tags
    if not request.user.is_authenticated:
        logger.warning(request.user.username + " not authorized to view song tags")
        return render(request, 'permission_denied.html')   
    
    # find the specific song object
    song = get_object_or_404(Song, pk=song_id) 
    logger.info("Showing tags for " +  str(song))  
    
    if song.image_link is None:
        print('Song image: ' + str(song.image))
        if song.image:
            cover_art = song.image.url
        else:
            cover_art = settings.STATIC_URL + 'img/default.png'
    else:
        cover_art = song.image_link 
        
    current_tags = Tagged_Song.objects.filter(song=song).order_by('-tag')
    print(current_tags)
    
    all_tags = Tag.objects.all().order_by(Lower('title'))
    avail_tags = list()
    for t in all_tags:
        found = False
        for ct in current_tags:
            if ct.tag == t:
                found = True
                break;
        if not found:
            avail_tags.append(t)
    
    for t in avail_tags:
        print(t.title)
    
    # render the template
    return render(request, 'update_song_tags.html', {
        'song': song, 
        'cover_art': cover_art,
        'available_tags': avail_tags,
        'current_tags': current_tags,
        })          


def add_tag_to_song(request, tag_id, song_id):
    ''' adds a tag to a song ''' 
    if not request.user.is_authenticated:
        logger.warning(request.user.username + " not authorized to add song tags")
        return render(request, 'permission_denied.html')   
    
    # find the specific song object and tag object
    song = get_object_or_404(Song, pk=song_id) 
    tag = get_object_or_404(Tag, pk=tag_id) 
    logger.info("Adding tag " + str(tag) + " to " +  str(song)) 
    
    ts = Tagged_Song()
    ts.song = song
    ts.tag = tag
    ts.save()
    
    return redirect('App:show_tags_for_song', song_id)

def remove_tag_from_song(request, tagged_song_id):
    ''' adds a tag to a song ''' 
    if not request.user.is_authenticated:
        logger.warning(request.user.username + " not authorized to add song tags")
        return render(request, 'permission_denied.html')   
    
    # find the specific song object and tag object
    tagged_song = get_object_or_404(Tagged_Song, pk=tagged_song_id)
    
    # save song id for redirect
    song_id = tagged_song.song.id
    
    logger.info("Removing tag " + str(tagged_song.tag.title) + " from " +  str(tagged_song.song.title)) 
    tagged_song.delete()
    
    return redirect('App:show_tags_for_song', song_id)