from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView, TemplateView

from App.forms import RandomPlaylistForm, TeacherSignUpForm
from App.models import User
from App.models.song import DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS

import logging
logger = logging.getLogger("django")


def user_profile(request):
    '''This view redirects to the list of playlists for the current user.'''
    user = request.user
    logger.info(user.username +  " logged in.")
    return redirect('App:home')

      
def user_preferences(request):
    '''This view displays the random playlist preferences of the current user.'''
    user = request.user
    playlist = None
    
    # if user has preferences, use those, otherwise use defaults
    if user.preferences is None:
        logger.info("Using default preferences for " + user.username)
        preferences = {
            'prevent_back_to_back_styles': True,
            'prevent_back_to_back_tempos': True,
            'counts'                     : DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS,
            'playlist_length'            : 25,
        }
    else:
        preferences = user.preferences
        if 'counts' not in preferences:
            logger.warning("Adding default count fields to " + user.username + " preferences")
            preferences['counts'] = DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS
            preferences['playlist_length'] = 25
        if 'percentages' in preferences:
            del preferences['percentages']
        
    if request.method == "GET":
        # build and render the random playlist form
        form = RandomPlaylistForm(prefs=preferences)
        return render(request, 'build_random_playlist.html', {
            'form': form, 
            'playlist': playlist,
            'user': user
        })
    else:  # POST
        cancel = request.POST.get("cancel")
        if cancel == "Cancel": 
            return redirect('App:user_preferences') 
        
        # obtain data from form and make sure it is valid.
        form = RandomPlaylistForm(request.POST,prefs=preferences)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info("Random playlist form data: " + str(form_data))
        else:
            # TODO: handle this error 
            logger.warning("Random playlist form returned invalid data")
        
        # determine if the inputs should be saved as user's new default preferences
        if form_data['save_preferences']:        
        
            # set variables based on form data    
            playlist_length = form_data['number_of_songs']
            prevent_back_to_back_styles = form_data['prevent_back_to_back_styles']
            prevent_back_to_back_tempos = form_data['prevent_back_to_back_tempos']
    
            # get song counts entered by the user from the form
            starting_counts = dict()
            for key in DANCE_TYPE_DEFAULT_PLAYLIST_COUNTS:
                # skip general dances 
                if key != 'gen':
                    form_field = '%s_songs' % (key, )
                    starting_counts[key] = form_data[form_field]
            
            # update the preferences dictionary
            preferences['playlist_length'] = playlist_length
            preferences['prevent_back_to_back_styles'] = prevent_back_to_back_styles
            preferences['prevent_back_to_back_tempos'] = prevent_back_to_back_tempos
            preferences['counts'] = starting_counts
            user.preferences = preferences
            user.save()
            logger.info("Saved new playlist preferences for " + user.username)
            
            # TODO: need to indicate data was saved somehow     
            return redirect('App:user_playlists') 
        
        else:  # save box was not checked
            return redirect('App:user_preferences') 

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
        logger.info("New teacher account created for " + user.username)
        
        # login the user that just signed up
        login(self.request, user)
        
        # return to the home page
        return redirect("App:home")