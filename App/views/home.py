from django.contrib.auth import logout 
from django.shortcuts import render
import sys
import os

import logging
logger = logging.getLogger("django")

# Create your views here.
def home(request):
    ''' The current home page for this app.'''
    return render(request,"home.html", {'user': request.user})

def about(request):
    ''' The current about page for this app.'''    
    return render(request,"about.html", {'version': '1.4', 'date': '23 May 2023'})

def playing(request):
    return render(request,"playing.html", {'user': request.user, 'studio_name': "Dancin' Dance Studio"})


def exit(request):
    if request.user.is_authenticated: 
        # only admin users or teachers can exit the application
        if request.user.is_superuser or request.user.is_teacher:    
            logger.info(request.user.get_username() + " exited the application")
            logout(request)
            os.abort()
            sys.exit("Operator terminated program")
    
    return render(request,"home.html", {'user': request.user}) 