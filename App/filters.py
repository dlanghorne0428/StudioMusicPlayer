import django_filters
from django import forms
from .models import Song

class SongFilter(django_filters.FilterSet):

    artist = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    title = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    
    class Meta:
        model = Song
        fields = ['dance_type']
