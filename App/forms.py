from datetime import time

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Fieldset, HTML, Layout, Row, Submit
from crispy_forms.bootstrap import FormActions

from .models.song import Song, SongFileInput, DANCE_TYPE_CHOICES, DANCE_TYPE_DEFAULT_PERCENTAGES
from .models.user import User
from .models.playlist import Playlist


class SongFileInputForm(ModelForm):
    class Meta:
        model = SongFileInput
        fields = ['audio_file', 'dance_type', 'special', 'holiday']


class SongEditForm(ModelForm):
    title = forms.CharField(
        label = "Title",
        max_length = 80,
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
        self.helper.label_class='mt-2'
        
        self.helper.layout = Layout(
            'title', 
            'artist', 
            'dance_type', 
            'holiday',
            'special',
            FormActions(
                Submit('save', 'Save changes'),
                HTML("""<a href="{% url 'App:all_songs' %}" class="btn btn-secondary">Cancel</a>"""),
                css_class="my-3"
            )
        )
        
    
    class Meta:
        model = Song
        fields = ['title', 'artist', 'dance_type', 'special', 'holiday']
        
        
class PlaylistInfoForm(ModelForm):
    max_song_duration = forms.ChoiceField(
        label = "Song Time Limit",
        required = False,
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
        fields = ['title', 'description', 'auto_continue', 'max_song_duration']
        

# form to specify parameters when populating a random playlist
class RandomPlaylistForm(Form):
    number_of_songs = forms.IntegerField(
        label     = "Number of Songs",
        min_value = 1, 
        max_value = 100,
        initial   = 10,
        required  = True)
    
    prevent_back_to_back_styles = forms.BooleanField(
        label     = "Prevent Same Dance Back-to-Back",
        initial   = True,
        help_text = "Checking this box prevents the playlist from having two consecutive songs of the same dance style.",
        required  = False)
   
    prevent_back_to_back_tempos = forms.BooleanField(
        label     = "Prevent Same Tempo Back-to-Back",
        initial   = True,
        help_text = "Checking this box prevents the playlist from having two consecutive fast songs or two consecutive slow songs.",         
        required  = False)  
    
    bachata_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[0][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[0][0]],
        required = True)
    
    bolero_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[1][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[1][0]],
        required = True)    
    
    cha_cha_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[2][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[2][0]],
        required = True) 
    
    country_2step_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[3][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[3][0]],
        required = True)    
    
    east_coast_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[4][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[4][0]],
        required = True) 
    
    foxtrot_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[5][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[5][0]],
        required = True)

    hustle_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[6][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[6][0]],
        required = True)   
    
    jive_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[7][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[7][0]],
        required = True)    
    
    mambo_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[8][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[8][0]],
        required = True)      
    
    merengue_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[9][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[9][0]],
        required = True)  
    
    nc2s_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[10][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[10][0]],
        required = True)    
    
    paso_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[11][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[11][0]],
        required = True)    
    
    peabody_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[12][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[12][0]],
        required = True)  
    
    quickstep_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[13][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[13][0]],
        required = True)  
    
    rumba_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[14][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[14][0]],
        required = True)
    
    samba_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[15][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[15][0]],
        required = True) 
    
    tango_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[16][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[16][0]],
        required = True) 
    
    v_waltz_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[17][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[17][0]],
        required = True)   
    
    waltz_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[18][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[18][0]],
        required = True)  
    
    west_coast_pct = forms.IntegerField(
        label = DANCE_TYPE_CHOICES[19][-1],
        min_value = 0,
        max_value = 100,
        initial = DANCE_TYPE_DEFAULT_PERCENTAGES[DANCE_TYPE_CHOICES[19][0]],
        required = True)     
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-random-playlist-Form'
        self.helper.form_method = 'post'
        self.helper.label_class='mt-2'
        
        self.helper.layout = Layout(
            Row(
                Column('number_of_songs', css_class="col-3 offset-3"),
                Column('prevent_back_to_back_styles', 'prevent_back_to_back_tempos',css_class='text-start px-4 col-6'),
            ),
            Row(
                Column(
                    HTML("<h4 class='text-center'>Select Percentages for each dance style</h4>"),
                    HTML("<h6 class='text-center'>Values must add up to 100 percent</h6>"),
                    css_class='col-12 text-center')
            ),
            Row(
                Column('bachata_pct', 'bolero_pct', 'cha_cha_pct', 'country_2step_pct', 'east_coast_pct', css_class="col-3"),
                Column('foxtrot_pct', 'hustle_pct', 'jive_pct', 'mambo_pct', 'merengue_pct', css_class="col-3"),
                Column('nc2s_pct', 'paso_pct', 'peabody_pct', 'quickstep_pct', 'rumba_pct', css_class="col-3"),
                Column('samba_pct', 'tango_pct', 'v_waltz_pct', 'waltz_pct', 'west_coast_pct', css_class="col-3"),
            ),
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