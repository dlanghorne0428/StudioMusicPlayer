from django.contrib import admin
from . models.song import Song, SongFileInput
from . models.playlist import Playlist, SongInPlaylist

# Register your models here.

class SongInPlaylistInline(admin.TabularInline):
    model = SongInPlaylist
    extra = 1

class PlaylistAdmin(admin.ModelAdmin):
    inlines = (SongInPlaylistInline,)
    

admin.site.register(Song)
admin.site.register(SongFileInput)


admin.site.register(Playlist, PlaylistAdmin)