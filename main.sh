#!/usr/bin/env bash

# Build the site (copies static + generates pages)
python3 src/main.py

# Start the server in the background so the script can exit
cd public && python3 -m http.server 8888 &