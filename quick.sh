#!/usr/bin/env bash

raspi-gpio get 26 | grep "level=0" &> /dev/null
if [ $? -eq 0 ]; then
	# Battery is low, so don't take a picture
	exit 42
fi


fn=$(date +%s).jpeg
file=/dev/shm/$fn
raspistill -t 2000 -o $file
scp -q -i /home/trick/station/ssh/id_rsa_station_phonehome $file station@hg.v9n.us:$fn
