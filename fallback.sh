#!/usr/bin/env bash

sudo pppd call gprs &
sleep 60
/home/trick/station/notify-hass-online
sleep 5m
/home/trick/station/notify-hass-online
sleep 5m
/home/trick/station/notify-hass-online
sleep 5m
/home/trick/station/notify-hass-online
sleep 45m
sudo killall pppd
