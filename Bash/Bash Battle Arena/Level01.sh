#!/bin/bash
# level01.sh
# Mission: Create a directory named 'Arena',
# create three character files inside it,
# and list the directory contents.

# Create directory
mkdir -p Arena

# Navigate into directory
cd Arena || exit 1

# Create character files
touch warrior.txt mage.txt archer.txt

# List contents
ls