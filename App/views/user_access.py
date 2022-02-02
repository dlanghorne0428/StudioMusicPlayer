from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

###########################################
# views for user login and logout
###########################################
def loginuser(request):
    ''' allows an existing user to login.
        currently new users must be added by the command line.'''
    if request.method == "GET":
        # display the built-in form to authenticate a user 
        return render(request, 'login.html', {'form':AuthenticationForm()})
    else:
        # login an existing user, based on data obtained from the form
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            # authentication was unsuccessful, display error message on form
            return render(request, 'login.html', {'form':AuthenticationForm(), 'error': "Invalid username or password"})
        else:
            # user found, log them in and return to the home page
            login(request, user)
            return redirect('App:home')


def logoutuser(request):
    ''' simply logout the current user and redirect to home page'''
    logout(request)
    return redirect('App:home') 