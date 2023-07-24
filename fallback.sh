#!/usr/bin/env bash

notify=/home/trick/station/notify-hass-online

sudo pppd call gprs &
sleep 60
$notify
sleep 5m
$notify
sleep 5m
$notify
sleep 5m
$notify
sleep 45m
sudo killall pppd
