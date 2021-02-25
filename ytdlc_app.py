#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
import os
import time
import sys
import pyperclip
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import configparser
import subprocess
config = configparser.ConfigParser()
config.read('mpyst_play.conf')

#取得通行憑證
cred = credentials.Certificate("./serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://line-bot-test-77a80.firebaseio.com/'
})

line_url_token = config.get('line_notify', 'line_url_token')
volume_num = config.get('volume', 'volume')
volume_str = volume_num + "%"
print('volume...', volume_str)
line_url_token = ''
os.system("amixer -M set PCM %s > /dev/null &" % volume_str) #設定音量
ref = db.reference('/') # 參考路徑

def lineNotifyMessage(token, msg):
      headers = {
          "Authorization": "Bearer " + token,
          "Content-Type" : "application/x-www-form-urlencoded"
      }
      payload = {'message': msg}
      r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
      return r.status_code

def write_data_to_file():
  fo = open('mpyst_play.conf', 'w', encoding='UTF-8')  # 重新创建配置文件
  config.write(fo)  # 数据写入配置文件
  fo.close()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if rc == 0:
      if flags["session present"] == 0:
        print("subscribing", 0)
        client.subscribe("music/playsong", 2) # 訂閱用戶歌名
        client.subscribe("music/shutdown", 2)
        client.subscribe("music/volume", 0)# 訂閱用戶音量
        client.subscribe("music/pause_play",2)
        client.subscribe("music/youtubeurl", 2) # 訂閱用戶 youtube 歌取網址
    else:
        print("connection failed ", rc)

def on_message(client, userdata, msg):
    global music_source, ref, userId, line_url_token
    print(sys.getdefaultencoding()) # 打印出目前系統字符編碼
    mqttmsg = msg.payload.decode("utf-8") #取得MQTT訊息
    print("收到 MQTT訊息", msg.topic+" "+ mqttmsg)
    if msg.topic == 'music/youtubeurl' and mqttmsg.strip():
       os.system("ps aux | grep mpv | awk '{print $2}' | xargs kill -9")
       print("播放 youtube url 歌曲")
       mqttmsg = msg.payload.decode("utf-8") #取得MQTT訊息
       userId = mqttmsg.split("~", 1)[0] #取得目前播歌的資訊
       video_url = mqttmsg.split("~", 1)[1] #取得目前播歌的資訊
       print("video_url...",video_url) 
       os.system("youtube-dlc  -f best -o - {video_url} | mpv - & ".format(video_url=video_url))       
       users_userId_ref = ref.child('smarthome-bot/'+ userId +'/profile/LineNotify')
       line_url_token = users_userId_ref.get()
       lineNotifyMessage(line_url_token, video_url)
       config['youtube']['song_url']= video_url # 音樂 URL 寫入檔案
       write_data_to_file()

    elif msg.topic == 'music/volume':
      mqttmsg = msg.payload.decode("utf-8")
      userId = mqttmsg.split("~", 1)[0] #取得目前播歌的資
      volume_str = mqttmsg.split("~", 1)[1] #取得目前播歌的資訊
      print("volume....", volume_str)
      os.system("amixer -M set PCM %s > /dev/null& " % (volume_str+"%")) #預設音量為80%
      config['volume']['volume']= volume_str# 音量值寫入欄位
      write_data_to_file()
      ref.child('smarthome-bot/' + userId + '/youtube_music').update({
               'volume':volume_str}
      )

    elif msg.topic == 'music/pause_play':
      os.system("ps aux | grep mpv | awk '{print $2}' | xargs kill -9")

def firebase_save(songkind,video_url):
    global ref
    #ref = db.reference('/') # 參考路徑
    song_data = {"songkind": songkind, "videourl": video_url}
    users_userId_ref = ref.child('smarthome-bot/' + userId + '/youtube_music')  
    users_userId_ref.update({"songkind": songkind})
    users_userId_ref.update({"videourl": video_url})
    print("儲存完畢", video_url)

os.system("ps aux | grep mpv | awk '{print $2}' | xargs kill -9")

data_json = ref.child('smarthome-bot/').get()
for k, v in data_json.items():  
  line_url_token = data_json[k]['profile']['LineNotify']
  lineNotifyMessage(line_url_token, "youtube 播放器已啟動")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.mqttdashboard.com", 1883) # broker 連線
client.loop_forever()  

