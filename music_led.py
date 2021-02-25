#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
ledPin = 7
GPIO.setup(ledPin, GPIO.OUT)
def process():
    stream = os.popen('ps aux | grep mpv | grep -v grep')
    output = stream.read()
    #print(output)
    return output
while True:
    process_state = process()
    if (process_state !=""):
        GPIO.output(ledPin, False)
        #print("LED OFF")
        time.sleep(1)
        GPIO.output(ledPin, True)
        #print("LED ON")
        time.sleep(1)
