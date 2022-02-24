from datetime import time

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, HTML, Layout, Row, Submit
from crispy_forms.bootstrap import FormActions

from .models.song import Song, SongFileInput, DANCE_TYPE_CHOICES, DANCE_TYPE_DEFAULT_PERCENTAGES
from .models.user import User
from .models.playlist import Playlist


class SongFileInputForm(ModelForm):
    '''form for uploading new music from a file.'''
    class Meta:
        model = SongFileInput
        # allow user to specify file, dance_type, and select special or holiday if any
        fields = ['audio_file', 'dance_type', 'special', 'holiday']


class SongEditForm(ModelForm):
    '''form to edit info for an existing song.'''
    title = forms.CharField(
        label = "Title",
        max_length = 80,     # ensure the field is wide enough to show the title
        required = True,
    )
    
    artist = forms.CharField(
        label = "Artist",
        max_length = 80,
        required = True,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-songEditForm'
        self.helper.form_method = 'post'
        self.helper.label_class='mt-2'      # allow some top margin for the form
        
        self.helper.layout = Layout(
            # show the fields in this order
            'title', 
            'artist', 
            'dance_type', 
            'holiday',
            'special',
            FormActions(
                # submit button and cancel link in the form of a button
                Submit('save', 'Save changes'),
                HTML("""<a href="{% url 'App:all_songs' %}" class="btn btn-secondary">Cancel</a>"""),
                # add some y-margin around the buttons.
                css_class="my-3"
            )
        )
        
    class Meta:
        model = Song
        fields = ['title', 'artist', 'dance_type', 'special', 'holiday']
        
        
class PlaylistInfoForm(ModelForm):
    ''' form to enter information for a playlist '''
    max_song_duration = forms.ChoiceField(
        label = "Song Time Limit",
        required = False,
        # use a dropdown field for the song time limit
        choices = (
            (time(minute=30), "------"),
            (time(minute=1, second=15), "1:15"),
            (time(minute=1, second=30), "1:30"),
            (time(minute=1, second=45), "1:45"),
            (time(minute=2, second= 0), "2:00"),
            (time(minute=2, second=15), "2:15"),
            (time(minute=2, second=30), "2:30"),
            (time(minute=2, second=45), "2:45"),
            (time(minute=3, second= 0), "3:00")
        )
    )

    class Meta:
        model = Playlist
        # include these fields in the form
        fields = ['title', 'description', 'auto_continue', 'max_song_duration']
        


class RandomPlaylistForm(Form):
    '''form to specify parameters when populating a random playlist.'''
    number_of_songs = forms.IntegerField(
        label     = "Number of Songs",
        min_value = 1, 
        max_value = 100,
        initial   = 10,
        required  = True)
    
    prevent_back_to_back_styles = forms.BooleanField(
        label     = "Prevent Same Dance Back-to-Back",
        initial   = True,
        help_text = "Checking this box prevents the playlist from having two consecutive songs of the same dance.",
        required  = False)
   
    prevent_back_to_back_tempos = forms.BooleanField(
        label     = "Prevent Same Tempo Back-to-Back",
        initial   = True,
        help_text = "Checking this box prevents the playlist from having two consecutive fast songs or two consecutive slow songs.",         
        required  = False)  
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        field_names = list()
        
        # these fields allow the user to enter percentages for each dance style
        # add them to the form using a loop
        for dance_type_tuple in DANCE_TYPE_CHOICES: 
            
            # constuct field name based on dance type abbreviation (e.g. 'Cha')
            field_name = '%s_pct' % (dance_type_tuple[0], )
            
            self.fields[field_name] = forms.IntegerField(
                # field label is the readable name for this dance type
                label = dance_type_tuple[1],
                min_value = 0,
                max_value = 100,
                # TODO: get user's previous percentages as their defaults?  
                initial = DANCE_TYPE_DEFAULT_PERCENTAGES[dance_type_tuple[0]],
                required = True)  
            
            # build a list of field names for use in column layout
            field_names.append(field_name)
        
        # see django-crispy-forms example
        self.helper = FormHelper()
        self.helper.form_id = 'id-random-playlist-Form'
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            # first row has two columns
            Row(
                Column('number_of_songs', css_class="col-3 offset-3"),
                Column('prevent_back_to_back_styles', 'prevent_back_to_back_tempos',css_class='text-start px-4 col-6'),
            ),
            # second row has one column for informative text
            Row(
                Column(
                    HTML("<h4 class='text-center'>Select Percentages for each dance style</h4>"),
                    HTML("<h6 class='text-center'>Values must add up to 100 percent</h6>"),
                    css_class='col-12 text-center')
            ),
            # next row has four columns to set percentages for each dance type
            Row(
                Column(field_names[0], field_names[1], field_names[2], field_names[3], field_names[4], css_class="col-3"),
                Column(field_names[5], field_names[6], field_names[7], field_names[8], field_names[9], css_class="col-3"),
                Column(field_names[10], field_names[11], field_names[12], field_names[13], field_names[14], css_class="col-3"),
                Column(field_names[15], field_names[16], field_names[17], field_names[18], field_names[19], css_class="col-3"),
                css_class='pt-4 border border-dark',
                css_id='enter-percentages'
            ),
            # submit and cancel buttons
            FormActions(
                Submit('continue', 'Continue'),
                HTML("""<a href="{% url 'App:all_playlists' request.user.id %}" class="btn btn-secondary">Cancel</a>"""),
                css_class="my-3"
            )
        )    
    
        
# based on example at: https://github.com/sibtc/django-multiple-user-types-example        
class TeacherSignUpForm(UserCreationForm):
    '''
    Create a signup form for teachers based on Django's User Creation Form.
    '''
    class Meta(UserCreationForm.Meta):
        model = User    # specify the model

    def save(self, commit=True):
        user = super().save(commit=False)  # get the object saved by the Django form
        user.is_teacher = True             # set is_teacher flag
        if commit:                         # save user object if everything ok
            user.save()
        return user