import django_filters
from django import forms
from .models.song import Song, DANCE_TYPE_CHOICES

class SongFilter(django_filters.FilterSet):

    artist = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    title = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    dance_type = django_filters.ChoiceFilter(choices=DANCE_TYPE_CHOICES, empty_label="Any") 
    
    class Meta:
        model = Song
        fields = ['artist', 'title', 'dance_type']
                  
