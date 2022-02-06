from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ''' 
    Create a custom user authenication model by deriving from AbstractUser
    '''
    
    # This field indicates whether this user is a teacher.
    # Teachers will be able to add and play songs, create and edit playlists, etc. 
    is_teacher = models.BooleanField(default=False)
