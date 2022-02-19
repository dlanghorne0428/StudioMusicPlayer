from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = "App"

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),   
    path("songs/", views.all_songs, name="all_songs"),
    path("addSong/", views.add_song, name="add_song"),
    path('playSong/<int:song_id>', views.play_song, name="play_song"),
    path('updateSong/<int:song_id>', views.update_song, name="update_song"),
    path('deleteSong/<int:song_id>', views.delete_song, name="delete_song"),
    path("playlists/", views.all_playlists, name="all_playlists"),
    path("playlists/<int:user_id>", views.all_playlists, name="all_playlists"),
    path("playlists/create/", views.create_playlist, name="create_playlist"),
    path("playlists/create/random", views.create_random_playlist, name="create_random_playlist"),    
    path("playlists/edit/<int:playlist_id>", views.edit_playlist, name="edit_playlist"),
    path("playlists/edit/<int:playlist_id>/addsong/<int:song_id>", views.add_to_playlist, name="add_to_playlist"),
    path('playSongList/<int:playlist_id>', views.play_song_list, name="play_song_list"),
    path("playlists/edit-title/<int:playlist_id>", views.edit_playlist_title, name="edit_playlist_title"),    
]