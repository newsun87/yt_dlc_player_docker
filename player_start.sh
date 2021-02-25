#!/bin/bash
rm -rf /root/.config/mps-youtube
#mpsyt 'set api_key AIzaSyCT3hmNwumjahnryO90JdvwKZPv9oej4Ug, q'
mpsyt 'set api_key AIzaSyDzuIv9FHQM3YcOSjIqvvHcEYH9M0PHVPM, q'
python3 music_led.py& #音樂播放時LED閃爍
python3 app.py

