from datetime import time

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm, CheckboxInput, NumberInput, Textarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Field, HTML, Layout, Row, Submit
from crispy_forms.bootstrap import FormActions

from .models.song import Song, SongFileInput, SpotifyTrackInput, DANCE_TYPE_CHOICES, HOLIDAY_CHOICES, HOLIDAY_USE_OPTIONS, HOLIDAY_DEFAULT_USAGE #StreamingSongInput, 
from .models.user import User
from .models.playlist import Playlist, CATEGORY_CHOICES


class SongFileInputForm(ModelForm):
    '''form for uploading new music from a file.'''
    class Meta:
        model = SongFileInput
        # allow user to specify file, dance_type, and select holiday if any
        fields = ['audio_file', 'dance_type', 'holiday']

        
class SpotifyTrackInputForm(ModelForm):
    '''form for uploading new music from a file.'''
    class Meta:
        model = SpotifyTrackInput
        # allow user to specify file, dance_type, and select holiday if any
        fields = ['track_id', 'title', 'artist', 'dance_type', 'holiday']


class SpotifySearchForm(Form):
    
    search_term = forms.CharField(
            label='Keywords', 
            max_length=100,
            required  = True)
        
    content_type = forms.ChoiceField(
            choices   = [("album", "Album"), 
                         ("artist", "Artist"),
                         ("playlist", "Playlist"),
                         ("track", "Track")],
            widget    = forms.RadioSelect,
            required  = True)
         

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
        # this is needed to return files from the form
        self.helper.attrs = {'enctype': 'multipart/form-data'}
        self.helper.label_class='fw-bold mt-2'      # allow some top margin for the form
        
        self.helper.layout = Layout(
            # show the fields in this order
            'title', 
            'artist', 
            'image',
            'dance_type', 
            'holiday',
            FormActions(
                # submit button and cancel link in the form of a button
                Submit('save', 'Save changes'),
                HTML("""<a href="{% url 'App:show_songs' %}" class="btn btn-secondary">Cancel</a>"""),
                # add some y-margin around the buttons.
                css_class="my-3"
            )
        )
        
    class Meta:
        # obtain data from these fields of the song model
        model = Song
        fields = ['title', 'artist', 'image', 'dance_type', 'holiday']
        
        
class PlaylistInfoForm(ModelForm):
    ''' form to enter information for a playlist '''
    title = forms.CharField(
        label = "",
        max_length = 50,     # ensure the field is wide enough to show the title
        required = True)
    
    description = forms.CharField(
        label  = "Description",
        required = False,
        # limit height of this field to 2 rows
        widget = Textarea(attrs={'rows': 2}))
    
    category = forms.ChoiceField(
        label = "Cotegory",
        choices = CATEGORY_CHOICES,
        required = True)   
    
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
                # first row has title only
                Row(
                    Field('title', css_class='fs-3 px-0 text-center'),
                ),
                # next row has three columns: description field in the right column is 2 rows tall
                Row(
                    Column('category', css_class="col-2"),
                    Column('max_song_duration', css_class="col-2"),
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
                    Field('title', css_class='fs-3 px-0 text-center'),
                ),
                Row(
                    Column('category', css_class="col-2"),
                    Column('max_song_duration', css_class="col-2"),
                    Column('description',css_class='text-start col-8 lh-sm'),
                ),
            )                

    class Meta:
        model = Playlist
        # include these fields in the form
        fields = ['title', 'description', 'category', 'max_song_duration']
        


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
            label     = "Total Number of Songs",
            min_value = 1, 
            max_value = 100,
            initial   = self.prefs['playlist_length'],
            # center the text in this input box
            widget = NumberInput(attrs={'class': 'text-center'}),
            required  = True)
        
        self.fields['prevent_back_to_back_styles'] = forms.BooleanField(
            # add information icon to the end of the label
            label     = "Prevent Same Style Back-to-Back \u24d8"  ,
            initial   = self.prefs['prevent_back_to_back_styles'],
            required  = False)
        
        self.fields['prevent_back_to_back_tempos'] = forms.BooleanField(
            # add information icon to the end of the label
            label     = "Prevent Same Tempo Back-to-Back  \u24d8"  ,
            initial   = self.prefs['prevent_back_to_back_tempos'],
            required  = False)        
        
        field_names = list()
        
        # these fields allow the user to enter the nuber of songs for each dance style
        # add them to the form using a loop
        for dance_type_tuple in DANCE_TYPE_CHOICES: 
            
            if dance_type_type[0] != "gen":
                # constuct field name based on dance type abbreviation (e.g. 'Cha')
                field_name = '%s_songs' % (dance_type_tuple[0], )
                
                self.fields[field_name] = forms.IntegerField(
                    # field label is the readable name for this dance type
                    label = dance_type_tuple[1],
                    min_value = 0,
                    max_value = 100, 
                    initial = self.prefs['counts'][dance_type_tuple[0]],
                    # right-justify the text in these input boxes
                    widget = NumberInput(attrs={'class': 'text-end'}),
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
                # style the label with font weight bold and font size 5 
                Column('number_of_songs', css_class="fw-bold fs-5 col-3 offset-3"),
                Column(
                    # add tooltips to these fields. Using Div applies tooltip to combination of label and checkbox 
                    Div('prevent_back_to_back_styles', 
                        data_bs_toggle="tooltip", 
                        data_bs_placement="right",
                        title="Checking this box prevents the playlist from having two consecutive songs of the same dance style.",
                    ), 
                    Div('prevent_back_to_back_tempos',
                        data_bs_toggle="tooltip", 
                        data_bs_placement="right",
                        title="Checking this box prevents the playlist from having two consecutive fast songs or two consecutive slow songs.",                        
                    ), 
                    # left-justify the second column, keep it toward the middle of the form
                    css_class='text-start px-4 col-6'),
                # align the bottom of the two columns in this row
                css_class='align-items-end' 
            ),
            # second row has two column titles, one for songs per dance style, the other for holidays
            Row(
                Column(
                    HTML("<h4 class='text-center'>Select Number of Songs for each dance style</h4>"),
                    HTML("<h6 class='text-center'>Values must add up to the total.</h6>"),
                    # song count data should take 9/12 of the window
                    css_class='col-9 text-center',
                ),
                Column(
                    HTML("<h5 class='text-center'>Include Holiday-Themed Songs?</h5>"),
                    # holidays only need 3/12 of the windoe
                    css_class='col-3 text-center',
               ),
               # align the bottom of the two columns in this row
               css_class='align-items-end' 
            ),
            # next row has two columns, one for numeric inputs, the other for holiday selections
            Row(
                Column(
                    # first column is split into five sub-columns to set number of songs for each dance type
                    Row(
                        Column(Field(field_names[0], active=True, css_class='text-center'),
                               Field(field_names[1], active=True, css_class='text-center'),
                               Field(field_names[2], active=True, css_class='text-center'),
                               Field(field_names[3], active=True, css_class='text-center'), 
                               # each sub-column takes 2/12 of the enclosing column, first sub-column is offset 1/12
                               css_class="col-2 offset-1"),
                        Column(Field(field_names[4], active=True, css_class='text-center'),
                               Field(field_names[5], active=True, css_class='text-center'),
                               Field(field_names[6], active=True, css_class='text-center'),
                               Field(field_names[7], active=True, css_class='text-center'),
                               css_class='col-2'),     
                        Column(Field(field_names[8], active=True, css_class='text-center'),
                               Field(field_names[9], active=True, css_class='text-center'),
                               Field(field_names[10], active=True, css_class='text-center'),
                               Field(field_names[11], active=True, css_class='text-center'), 
                               css_class="col-2"), 
                        Column(Field(field_names[12], active=True, css_class='text-center'),
                               Field(field_names[13], active=True, css_class='text-center'),
                               Field(field_names[14], active=True, css_class='text-center'),
                               Field(field_names[15], active=True, css_class='text-center'), 
                               css_class="col-2"),    
                        Column(Field(field_names[16], active=True, css_class='text-center'),
                               Field(field_names[17], active=True, css_class='text-center'),
                               Field(field_names[18], active=True, css_class='text-center'),
                               Field(field_names[19], active=True, css_class='text-center'), 
                               css_class="col-2"), 
                        # put a dark border around the five subcolumns
                        css_class='pt-2 border border-dark',
                        # establish an ID for javascript to use
                        css_id='enter-songs-per-dance-style'
                    ),
                    # this row for an error message is centered under the five subcolumns
                    Row(
                        # establish an ID so Javascript can modify this error text
                        HTML("<p hidden id='count-error'>Current total is <span id='count-total'></span></p>"),
                    ),
                    css_class='text-center'
                ),
                Column(   
                    # second column determines if holiday songs will be used
                    Row(
                        field_names[20], field_names[21], field_names[22], field_names[23],
                        # put a border around these elements
                        css_class='pt-2 border border-danger',
                        # establish an ID for javascript to use
                        css_id='enter-holidays'
                        ),
                    # this column takes 3/12 of the window and data is centered within that allocaation
                    css_class='col-3 text-center'
                ),
            ),
            # this row has a save checkbox, it is centered in the entire window and has a top margin
            Row(
                Column('save_preferences'),
                css_class = 'col-12 text-center mt-3'
            ),
            
            # submit and cancel buttons
            FormActions(
                Submit('continue', 'Continue'),
                Submit('cancel', 'Cancel'),
                # provide a small margin in the y-direction, top and bottom
                css_class="my-1"
            )
        )    
    

class PlaylistUploadForm(forms.Form):
    ''' form to enter information for a playlist '''
    title = forms.CharField(
        label = "Playlist Title",
        max_length = 50,     # ensure the field is wide enough to show the title
        required = True)
    file = forms.FileField()

        
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