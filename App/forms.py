from datetime import time

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm, Textarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, HTML, Layout, Row, Submit
from crispy_forms.bootstrap import FormActions

from .models.song import Song, SongFileInput, DANCE_TYPE_CHOICES, HOLIDAY_CHOICES, HOLIDAY_USE_OPTIONS, HOLIDAY_DEFAULT_USAGE
from .models.user import User
from .models.playlist import Playlist


class SongFileInputForm(ModelForm):
    '''form for uploading new music from a file.'''
    class Meta:
        model = SongFileInput
        # allow user to specify file, dance_type, and select holiday if any
        fields = ['audio_file', 'dance_type', 'holiday']


class SongEditForm(ModelForm):
    '''form to edit info for an existing song.'''
    title = forms.CharField(
        label = "Title",
        max_length = 80,     # ensure the field is wide enough to show the title
        required = True,
    )
    
    artist = forms.CharField(
        label = "Artist",
        max_length = 80,    # ensure the field is wide enough to show the artist
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
            FormActions(
                # submit button and cancel link in the form of a button
                Submit('save', 'Save changes'),
                HTML("""<a href="{% url 'App:all_songs' %}" class="btn btn-secondary">Cancel</a>"""),
                # add some y-margin around the buttons.
                css_class="my-3"
            )
        )
        
    class Meta:
        # obtain data from these fields of the song model
        model = Song
        fields = ['title', 'artist', 'dance_type', 'holiday']
        
        
class PlaylistInfoForm(ModelForm):
    ''' form to enter information for a playlist '''
    title = forms.CharField(
        label = "",
        max_length = 50,     # ensure the field is wide enough to show the title
        required = True)
    
    description = forms.CharField(
        label  = "Description",
        required = False,
        # limit height of this field to 3 rows
        widget = Textarea(attrs={'rows': 3}))
    
    auto_continue = forms.BooleanField(
        label = "Autoplay Next Song",
        required = False)   # this field must not be required in order to set it to false
    
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
    
    def __init__(self, *args, **kwargs):
        # this form is used for playlist creation and editing. 
        # submit_title argument tells us which it is. 
        self.submit_title = kwargs.pop('submit_title')
        super(PlaylistInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-PlaylistEditForm'
        self.helper.form_method = 'post'
        # Form labels will be bold text
        self.helper.label_class = 'fw-bold'
        
        if self.submit_title is not None:
            self.helper.layout = Layout(
                # first row has one column for the title
                Row(
                    Column(
                        Field('title', css_class='fs-3 px-0 text-center'),
                        css_class="col-8 offset-2"),
                ),
                # next row has two columns: description field in the right column is 3 rows tall
                Row(
                    Column('max_song_duration', 'auto_continue', css_class="col-2 offset-2"),
                    Column('description',css_class='text-start col-8 lh-sm'),
                ),
                # submit and cancel buttons are included, button text comes from submit_title
                FormActions(
                    Submit('submit', self.submit_title),
                    HTML("""<a href="{% url 'App:all_playlists' %}" class="btn btn-secondary">Cancel</a>"""),
                    css_class="my-2"
                )                
            )   
        else: # same layout as above without submit/cancel buttons as javascript is used to submit the form
            self.helper.layout = Layout(
                Row(
                    Column(
                        Field('title', css_class='fs-3 px-0 text-center'),
                        css_class="col-8 offset-2"),
                ),
                Row(
                    Column('max_song_duration', 'auto_continue', css_class="col-2 offset-2"),
                    Column('description',css_class='text-start col-8 lh-sm'),
                ),
            )                

    class Meta:
        model = Playlist
        # include these fields in the form
        fields = ['title', 'description', 'auto_continue', 'max_song_duration']
        


class RandomPlaylistForm(Form):
    '''form to specify parameters when populating a random playlist.'''
    
    save_preferences = forms.BooleanField(
        label     = "Save these settings as the default for your future playlists?",
        initial   = False,
        required  = False)
    
    def __init__(self, *args, **kwargs):
        # get the preferences in this dictionary argument
        self.prefs = kwargs.pop('prefs')
        super(RandomPlaylistForm, self).__init__(*args, **kwargs)
        
        self.fields['number_of_songs'] = forms.IntegerField(
            label     = "Number of Songs",
            min_value = 1, 
            max_value = 100,
            initial   = self.prefs['playlist_length'],
            required  = True)
        
        self.fields['prevent_back_to_back_styles'] = forms.BooleanField(
            label     = "Prevent Same Dance Back-to-Back",
            initial   = self.prefs['prevent_back_to_back_styles'],
            help_text = "Checking this box prevents the playlist from having two consecutive songs of the same dance.",
            required  = False)
        
        self.fields['prevent_back_to_back_tempos'] = forms.BooleanField(
            label     = "Prevent Same Tempo Back-to-Back",
            initial   = self.prefs['prevent_back_to_back_tempos'],
            help_text = "Checking this box prevents the playlist from having two consecutive fast songs or two consecutive slow songs.",         
            required  = False)        
        
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
                initial = self.prefs['percentages'][dance_type_tuple[0]],
                required = True)  
            
            # build a list of field names for use in column layout
            field_names.append(field_name)
        
        # these fields allow the user to enter preferences for each holiday
        # add them to the form using a loop            
        for holiday_tuple in HOLIDAY_CHOICES:
            
            field_name = "%s_use" % (holiday_tuple[0], )
            
            self.fields[field_name] = forms.ChoiceField(
                label = holiday_tuple[1],
                choices = HOLIDAY_USE_OPTIONS,
                initial = self.prefs['holiday_usage'][holiday_tuple[0]],
                required = True
                )      
            
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
                css_class='pt-2 border border-dark',
                css_id='enter-percentages'
            ),
            # next row has one column for more informative text
            Row(
                Column(
                    HTML("<h4 class='text-center'>Include Holiday-Themed Songs?</h4>"),
                    css_class='col-12 text-center mt-4')
            ),
            # next row has four columns, one for each holiday
            Row(
                Column(field_names[20], css_class="col-3"),
                Column(field_names[21], css_class="col-3"),
                Column(field_names[22], css_class="col-3"),
                Column(field_names[23], css_class="col-3"),
                css_class='pt-2 border border-danger',
                css_id='enter-holidays'
                ),
            # this row has a save checkbox
            Row(
                Column('save_preferences'),
                css_class = 'col-12 text-center mt-2'
            ),
            # submit and cancel buttons
            FormActions(
                Submit('continue', 'Continue'),
                Submit('cancel', 'Cancel'),
                css_class="my-2"
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