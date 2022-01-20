from django.contrib import admin
from . models import Song, SongFileInput

# Register your models here.
admin.site.register(Song)
admin.site.register(SongFileInput)