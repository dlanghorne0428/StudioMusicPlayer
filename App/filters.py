import django_filters
from django import forms
from .models.song import Song, DANCE_TYPE_CHOICES, HOLIDAY_CHOICES

class SongFilter(django_filters.FilterSet):

    artist = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    title = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    dance_type = django_filters.ChoiceFilter(choices=DANCE_TYPE_CHOICES[:-1], empty_label="Any") 
    holiday = django_filters.ChoiceFilter(choices=HOLIDAY_CHOICES, empty_label="Any") 
    
    class Meta:
        model = Song
        fields = ['artist', 'title', 'dance_type', 'holiday']
                  
