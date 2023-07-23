#!/usr/bin/env bash

tmux new -d "python3 -u gps.py > gps-$(date -u +%Y%m%d-%H%M%S).log"
