@echo off
cd C:\realtime-weather-pipeline
call venv\Scripts\activate
python etl.py
