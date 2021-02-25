youtube_url=$1
youtube-dlc -f best -o - $youtube_url | mpv - >/dev/null&
