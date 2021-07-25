#!/bin/sh

# Run setup process
while true; do
    if flask deploy; then
        break
    fi
    echo 'Deploy command failed, retrying in 5 secs...'
    sleep 5
done

# Start app
exec gunicorn --config instance/gunicorn.conf.py
