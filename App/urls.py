from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = "App"

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path('login/', views.loginuser, name="loginuser"),
    path('logout/', views.logoutuser, name="logoutuser"),      
    path("songs", views.all_songs, name="all_songs"),
    path("addSong", views.add_song, name="add_song"),
    path('playSong/<int:song_id>', views.play_song, name="play_song"),
    path('updateSong/<int:song_id>', views.update_song, name="update_song"),
    path('deleteSong/<int:song_id>', views.delete_song, name="delete_song"),
    path('playSongList/', views.play_song_list, name="play_song_list"),
]