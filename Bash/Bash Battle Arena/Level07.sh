#!/bin/bash
# level07.sh
# Mission: Sort all .txt files in the Arena directory
# by size (smallest to largest) and display the results.

DIRECTORY="Arena"

if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist."
    exit 1
fi

find "$DIRECTORY" -type f -name "*.txt" -exec ls -lh {} + \
    | sort -k 5,5 -h \
    | awk '{ print $5, $9 }'