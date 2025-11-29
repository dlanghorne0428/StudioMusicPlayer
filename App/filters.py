import django_filters
from django import forms
from django.db.models import Q
from .models.song import Song, DANCE_TYPE_CHOICES

class SongFilter(django_filters.FilterSet):

    artist = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))
    title = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'size':20}))

    # define custom filter to cover both dance type and alternate dance type
    q = django_filters.ChoiceFilter(method='custom_dance_type_filter', choices=DANCE_TYPE_CHOICES, empty_label="Any") 
    
    class Meta:
        model = Song
        fields = ['artist', 'title', 'q']
        
    # custom filter allows either dance type field to match
    def custom_dance_type_filter(self, queryset, name, value):
        return queryset.filter (
            Q(dance_type=value) | Q (alt_dance_type=value)
        )
                  
