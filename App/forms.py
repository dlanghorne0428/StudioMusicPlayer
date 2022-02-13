from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm

from .models.song import Song, SongFileInput
from .models.user import User
from .models.playlist import Playlist


class SongFileInputForm(ModelForm):
    class Meta:
        model = SongFileInput
        fields = ['audio_file', 'dance_type', 'special', 'holiday']


class SongEditForm(ModelForm):
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