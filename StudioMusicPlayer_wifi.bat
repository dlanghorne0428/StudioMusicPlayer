REM docker run --name=my_redis -p 6379:6379 -d redis
docker start my_redis
start firefox.exe http://localhost:8000
py manage.py runserver --noreload --settings=StudioMusicPlayer.settings_wifi 0.0.0.0:8000
taskkill /im firefox.exe