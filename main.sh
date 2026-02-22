#!/usr/bin/env bash

# Build the site
python3 src/main.py

# Kill any old server on port 8888 (silent, ignore if none)
fuser -k 8888/tcp 2>/dev/null || true

# Start fresh server in background
cd docs && python3 -m http.server 8888 &