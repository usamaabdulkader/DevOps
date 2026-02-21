#!/bin/bash
# level09.sh
# Mission: Monitor the Arena directory for changes
# and log events with timestamps.

DIRECTORY="Arena"
LOG_FILE="change.txt"

if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist."
    exit 1
fi

echo "Monitoring '$DIRECTORY' for changes..."
echo "Logging to '$LOG_FILE'..."

fswatch -r "$DIRECTORY" | while read -r event; do
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')

    if [ -e "$event" ]; then
        echo "$timestamp - File modified/created: $event" >> "$LOG_FILE"
    else
        echo "$timestamp - File deleted: $event" >> "$LOG_FILE"
    fi
done