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

def exit(request):
    logout(request)
    logger.info(request.user.username + " exited the application")
    os.abort()
    sys.exit("Operator terminated program")
    