#!/bin/bash
gpio mode 7 out
gpio write 7 0
while true
do
   process=`ps -ef| grep mpsyt | grep -v grep`; #�d?mysqld?�{�Agrep -v grep�h��grep?�{
  if [ "$process" != "" ]; then
     gpio write 7 0
     sleep 1
     gpio write 7 1
     sleep 1    
  fi
done
