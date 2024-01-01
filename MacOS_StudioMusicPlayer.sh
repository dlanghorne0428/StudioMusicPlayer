#!/bin/zsh

open -a "firefox" http://localhost:8000
python manage.py runserver --noreload 
killall firefox

