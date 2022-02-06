from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . models.song import Song, SongFileInput
from . models.playlist import Playlist, SongInPlaylist
from . models.user import User

# Register your models here.

class SongInPlaylistInline(admin.TabularInline):
    model = SongInPlaylist
    extra = 1

class PlaylistAdmin(admin.ModelAdmin):
    inlines = (SongInPlaylistInline,)
    

admin.site.register(Song)
admin.site.register(SongFileInput)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(User, UserAdmin)