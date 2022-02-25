from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView, TemplateView

from App.forms import TeacherSignUpForm
from App.models import User


def user_profile(request):
    '''This view redirects to the list of playlists for the current user.'''
    user = request.user
    return redirect('App:all_playlists', user.id)
    


# based on example from https://github.com/sibtc/django-multiple-user-types-example
class SignUpView(TemplateView):
    template_name = 'registration/signup.html'
    

class TeacherSignUpView(CreateView):
    '''
    This is a signup view for a teacher.
    See https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html
    '''
    
    # define the model, form, and template
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        # add user_type = 'teacher' to the data being passed to the template
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # save the user object returned by the form
        user = form.save()
        
        # login the user that just signed up
        login(self.request, user)
        
        # new users have no playlists, so redirect to show all the p;aylists in the database
        return redirect("App:all_playlists")