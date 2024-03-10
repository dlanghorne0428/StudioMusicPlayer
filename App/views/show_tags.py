from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings

# imported our models
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

