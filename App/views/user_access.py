from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm


###########################################
# views for user login and logout
###########################################
def loginuser(request):
    if request.method == "GET":
        return render(request, 'login.html', {'form':AuthenticationForm()})
    else:
        # login an existing user
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, 'login.html', {'form':AuthenticationForm(), 'error': "Invalid username or password"})
        else:
            login(request, user)
            return redirect('App:home')


def logoutuser(request):
    logout(request)
    return redirect('App:home') 