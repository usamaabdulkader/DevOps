#!/bin/bash
# level08.sh
# Mission: Search for a word or phrase in all .log files in a directory.

DIRECTORY="."

if [ -z "$1" ]; then
    echo "No search term provided."
    exit 1
fi

WORD="$1"

if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist."
    exit 1
fi

find "$DIRECTORY" -type f -name "*.log" -exec grep -li "$WORD" {} +