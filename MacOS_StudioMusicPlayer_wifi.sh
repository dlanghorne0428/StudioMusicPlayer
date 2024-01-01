#!/bin/zsh

#docker run --name=my_redis -p 6379:6379 -d redis
docker start my_redis
open -a "firefox" -u http://localhost:8000
python manage.py runserver --noreload --settings=StudioMusicPlayer.settings_wifi 0.0.0.0:8000
killall firefox
