#!/bin/zsh

docker run --name=my_redis -p 6379:6379 -d redis
open -a "firefox" -u http://localhost:8000
python manage.py runserver --settings=StudioMusicPlayer.settings_wifi 0.0.0.0:8000
killall firefox
