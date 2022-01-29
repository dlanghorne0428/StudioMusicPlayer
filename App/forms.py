from django import forms
from django.forms import Form, ModelForm
from .models.song import Song, SongFileInput


class SongFileInputForm(ModelForm):
    class Meta:
        model = SongFileInput
        fields = ['audio_file', 'dance_type']


class SongEditForm(ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'dance_type']