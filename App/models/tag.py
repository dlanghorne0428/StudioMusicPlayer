from django.db import models
from django.utils.text import get_valid_filename


class Tag(models.Model):
    '''A category that can be used to classify songs.
       This could be date (e.g. 1980s) or genre (e.g. Christmas)'''
    
    # a  title for the tag
    title = models.CharField(max_length=50) 
    


