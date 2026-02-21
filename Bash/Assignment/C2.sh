#!/bin/bash
# file_operations.sh
# Description: Creates a directory and file, writes the current date,
#              and displays the file contents.
# Usage: ./file_operations.sh

dir="bash_demo"
file="demo.txt"
file_path="$dir/$file"

# Create directory
mkdir -p "$dir"

# Create file with current date
echo "This file was created by a Bash script on $(date +%F)" > "$file_path"

# Display confirmation message
echo "Directory '$dir' created. File '$file' created."

# Display file contents
echo -n "File contents: "
cat "$file_path"
