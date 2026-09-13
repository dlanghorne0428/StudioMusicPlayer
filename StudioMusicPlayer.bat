@echo off
start firefox.exe http://localhost:8000
py manage.py migrate
py manage.py runserver --noreload
taskkill /im firefox.exe