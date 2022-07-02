from django.shortcuts import render
import sys

# Create your views here.
def home(request):
    ''' The current home page for this app.'''
    return render(request,"home.html", {'user': request.user})

def exit(request):
    sys.exit("Operator terminated program")
    