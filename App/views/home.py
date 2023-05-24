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


def exit(request):
    logout(request)
    logger.info(request.user.username + " exited the application")
    os.abort()
    sys.exit("Operator terminated program")
    