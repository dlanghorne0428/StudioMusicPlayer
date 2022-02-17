from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML, Layout, Row, Submit
from crispy_forms.bootstrap import FormActions

from .models.song import Song, SongFileInput
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
        
        
class PlaylistEditForm(ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'auto_continue', 'max_song_duration']
        
        
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