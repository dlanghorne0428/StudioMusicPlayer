from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView, TemplateView

from App.forms import RandomPlaylistForm, TeacherSignUpForm
from App.models import User
from App.models.song import DANCE_TYPE_DEFAULT_PERCENTAGES


def user_profile(request):
    '''This view redirects to the list of playlists for the current user.'''
    user = request.user
    return redirect('App:all_playlists', user.id)

      
def user_preferences(request):
    '''This view displays the random playlist preferences of the current user.'''
    user = request.user
    playlist = None
    
    # if user has percentage preferences, use those, otherwise use defaults
    if user.percentage_preferences is None:
        percentage_preferences = DANCE_TYPE_DEFAULT_PERCENTAGES
    else:
        percentage_preferences = user.percentage_preferences
    if request.method == "GET":
        # build and render the random playlist form
        form = RandomPlaylistForm(prefs= percentage_preferences)
        return render(request, 'build_random_playlist.html', {
            'form': form, 
            'playlist': playlist,
        })
    else:  # POST
        submit = request.POST.get("submit")
        # if user hit cancel button during build random, delete playlist that was in process of being created. 
        if submit == "Cancel": 
            return redirect('App:all_playlists', user.id) 
        
        # obtain data from form and make sure it is valid.
        form = RandomPlaylistForm(request.POST,prefs=percentage_preferences)
        if form.is_valid():
            form_data = form.cleaned_data
        else:
            # TODO: handle this error 
            print('invalid');
        
        # set variables based on form data    
        #playlist_length = form_data['number_of_songs']
        #prevent_back_to_back_styles = form_data['prevent_back_to_back_styles']
        #prevent_back_to_back_tempos = form_data['prevent_back_to_back_tempos']

        # get percentages entered by the user from the form
        starting_percentages = dict()
        for key in DANCE_TYPE_DEFAULT_PERCENTAGES:
            form_field = '%s_pct' % (key, )
            starting_percentages[key] = form_data[form_field]
            
        # determine if the inputs should be saved as user's new default percentages
        if form_data['save_preferences']:
            user.percentage_preferences = starting_percentages
            user.save()
            
        # TODO: need to indicate data was saved somehow     
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