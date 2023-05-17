from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = "App"

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("exit/", views.about, name="about"),
    path("exit/", views.exit, name="exit"),
    path("songs/", views.show_songs, name="show_songs"),
    path("songs/no-art", views.show_songs_no_cover_art, name="show_songs_no_cover_art"),
    path("songs/<int:song_id>", views.show_songs, name="show_songs"),
    path("replace-song/<int:playlist_id>/<int:index>/<str:dance_type>", views.replace_song, name="replace_song"),
    path("replace-song/<int:playlist_id>/<int:index>/<str:dance_type>/<int:song_id>", views.replace_song, name="replace_song"),
    path("addSong/", views.add_song, name="add_song"),
    path("accounts/profile/", views.user_profile, name='user_profile'),
    path('playSong/<int:song_id>', views.play_song, name="play_song"),
    path('updateSong/<int:song_id>', views.update_song, name="update_song"),
    path('deleteSong/<int:song_id>', views.delete_song, name="delete_song"),
    path("playlists/", views.all_playlists, name="all_playlists"),
    path("user-playlists", views.user_playlists, name="user_playlists"),
    path("playlists/create/", views.create_playlist, name="create_playlist"), 
    path("playlists/create/<int:random>", views.create_playlist, name="create_playlist"), 
    path("playlists/create-from-json", views.create_playlist_from_json, name="create_playlist_from_json"),
    path("playlists/build-random/<int:playlist_id>", views.build_random_playlist, name="build_random_playlist"),
    path("playlists/copy/<int:playlist_id>", views.copy_playlist, name="copy_playlist"),
    path("playlists/delete/<int:playlist_id>", views.delete_playlist, name="delete_playlist"),
    path("playlists/edit/<int:playlist_id>", views.edit_playlist, name="edit_playlist"),
    path("playlists/edit/<int:playlist_id>/>=<int:start_index>", views.edit_playlist, name="edit_playlist"),
    path("playlists/edit/<int:playlist_id>/addrandomsong/<str:dance_type>", views.add_random_song_to_playlist, name="add_random_song_to_playlist"),
    path("playlists/edit/<int:playlist_id>/addsong/<int:song_id>", views.add_to_playlist, name="add_to_playlist"),
    path("playlists/replace/<int:playlist_id>", views.replace_playlist_songs, name="replace_playlist"),
    path("playlists/shuffle/<int:playlist_id>", views.shuffle_playlist, name="shuffle_playlist"), 
    path('playSongList/<int:playlist_id>', views.play_song_list, name="play_song_list"),
    path('playSongList/<int:playlist_id>/<int:start_index>', views.play_song_list, name="play_song_list"),    
    path("preferences/", views.user_preferences, name="user_preferences"),    
    path("spotify/sign_in", views.spotify_sign_in, name="spotify_sign_in"),  
    path("spotify/sign_out", views.spotify_sign_out, name="spotify_sign_out"),
    path('spotify/liked-songs', views.spotify_liked_songs, name="spotify_liked_songs"),
    path('spotify/followed-artists', views.spotify_followed_artists, name="spotify_followed_artists"),
    path('spotify/recently-played', views.spotify_recently_played, name="spotify_recently_played"),
    path('spotify/saved-albums', views.spotify_saved_albums, name="spotify_saved_albums"),
    path('spotify/saved-playlists', views.spotify_saved_playlists, name="spotify_saved_playlists"),
    path('spotify/search', views.spotify_search, name="spotify_search"),
    path('spotify/search-albums/<str:search_term>', views.spotify_search_albums, name="spotify_search_albums"),
    path('spotify/search-artists/<str:search_term>', views.spotify_search_artists, name="spotify_search_artists"),
    path('spotify/search-playlists/<str:search_term>', views.spotify_search_playlists, name="spotify_search_playlists"),
    path('spotify/search-tracks/<str:search_term>', views.spotify_search_tracks, name="spotify_search_tracks"),
    path("spotify/artist-albums/<str:artist_id>", views.spotify_artist_albums, name="spotify_artist_albums"),
    path("spotify/artist-tracks/<str:artist_id>", views.spotify_artist_tracks, name="spotify_artist_tracks"),
    path("spotify/album-tracks/<str:album_id>", views.spotify_album_tracks, name="spotify_album_tracks"),
    path("spotify/playlist-tracks/<str:playlist_id>", views.spotify_playlist_tracks, name="spotify_playlist_tracks"),
    path("spotify/import-track/<str:track_id>", views.add_spotify_track, name="add_spotify_track"),
    path("spotify/import-track/<str:track_id>/<int:replace_song_id>", views.add_spotify_track, name="add_spotify_track"),
    path("spotify/import-playlist/<str:spotify_playlist_id>/<int:dance_type_index>", views.add_spotify_playlist, name="add_spotify_playlist"), 
    path("spotify/find-clean-track/<str:track_id>", views.spotify_find_clean_track, name="spotify_find_clean_track"), 
    path("spotify/find-clean-track/<str:track_id>/<int:replace_song_id>", views.spotify_find_clean_track, name="spotify_find_clean_track"), 
    path("spotify/find-song-bpms", views.spotify_find_song_bpms, name="spotify_find_song_bpms"),
    path("spotify/fix_non_US", views.fix_non_US_spotify_tracks, name = 'fix_non_US_spotify_tracks'),
]