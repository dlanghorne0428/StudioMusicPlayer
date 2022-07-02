from django.shortcuts import render
import sys
import os

# Create your views here.
def home(request):
    ''' The current home page for this app.'''
    return render(request,"home.html", {'user': request.user})

def exit(request):
    os.abort()
    sys.exit("Operator terminated program")
    