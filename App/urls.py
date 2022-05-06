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
    path("addSpotifyTrack/", views.add_spotify_track, name="add_spotify_track"),
    path("accounts/profile/", views.user_profile, name='user_profile'),
    path('playSong/<int:song_id>', views.play_song, name="play_song"),
    path('updateSong/<int:song_id>', views.update_song, name="update_song"),
    path('deleteSong/<int:song_id>', views.delete_song, name="delete_song"),
    path("playlists/", views.all_playlists, name="all_playlists"),
    path("playlists/<int:user_id>", views.all_playlists, name="all_playlists"),
    path("playlists/create/", views.create_playlist, name="create_playlist"), 
    path("playlists/create/<int:random>", views.create_playlist, name="create_playlist"), 
    path("playlists/build-random/<int:playlist_id>", views.build_random_playlist, name="build_random_playlist"),
    path("playlists/delete/<int:playlist_id>", views.delete_playlist, name="delete_playlist"),
    path("playlists/edit/<int:playlist_id>", views.edit_playlist, name="edit_playlist"),
    path("playlists/edit/<int:playlist_id>/addrandomsong/<str:dance_type>", views.add_random_song_to_playlist, name="add_random_song_to_playlist"),
    path("playlists/edit/<int:playlist_id>/addsong/<int:song_id>", views.add_to_playlist, name="add_to_playlist"),
    path('playSongList/<int:playlist_id>', views.play_song_list, name="play_song_list"),
    path('playSongList/<int:playlist_id>/<int:start_index>', views.play_song_list, name="play_song_list"),    
    path("preferences/", views.user_preferences, name="user_preferences"),    
]