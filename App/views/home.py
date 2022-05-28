from django.shortcuts import render

# Create your views here.
def home(request):
    ''' The current home page for this app.'''
    return render(request,"home.html", {'user': request.user})
