#!/bin/bash
set -e

# Setup persistent directory structure if /data disk is mounted (e.g. Render Persistent Disk)
if [ -d "/data" ]; then
    echo "Persistent /data volume found. Setting up symlinks..."
    
    # Initialize /data/config if empty
    if [ ! -d "/data/config" ]; then
        echo "Initializing /data/config with defaults..."
        mkdir -p /data/config
        cp /app/config/*.example /data/config/ 2>/dev/null || true
        for f in /data/config/*.example; do
            [ -e "$f" ] && mv "$f" "${f%.example}"
        done
        # Also copy any raw jsons if they somehow made it
        cp /app/config/*.json /data/config/ 2>/dev/null || true
    fi
    # Always symlink
    echo "Found existing /data/config. Symlinking..."
    rm -rf /app/config
    ln -s /data/config /app/config

    # Initialize /data/results if empty
    if [ ! -d "/data/results" ]; then
        echo "Initializing /data/results..."
        if [ -d "/app/results" ]; then
            cp -r /app/results /data/results
            rm -rf /app/results
        else
            mkdir -p /data/results
        fi
    fi
    # Always symlink
    echo "Found existing /data/results. Symlinking..."
    rm -rf /app/results
    ln -s /data/results /app/results
fi

echo "Starting automated attendance background scheduler..."
python main.py --schedule &

echo "Starting Flask Admin Dashboard on PORT ${PORT:-5000}..."
exec gunicorn -b 0.0.0.0:${PORT:-5000} "admin.app:create_app()"
