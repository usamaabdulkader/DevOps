#!/bin/bash
# level03.sh
# Mission: Check if 'hero.txt' exists inside the Arena directory.

if [ -f "Arena/hero.txt" ]; then
    echo "Hero found!"
else
    echo "Hero missing!"
fi