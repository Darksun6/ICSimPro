#!/bin/bash
for i in 1 2 3 4 5 6
do 
  canplayer -I door1_lock
  sleep 2
  canplayer -I door1_unlock
  sleep 2
done
