#!/bin/bash
# file_checker.sh
# Description: Checks whether a file exists and reports its permissions.
# Usage: ./file_checker.sh

read -p "Enter filename to check: " file

if [ -e "$file" ]; then
    echo "File '$file' exists."

    # Check readability
    if [ -r "$file" ]; then
        echo "✓ File is readable"
    else
        echo "✗ File is not readable"
    fi

    # Check writability
    if [ -w "$file" ]; then
        echo "✓ File is writable"
    else
        echo "✗ File is not writable"
    fi

    # Check executability
    if [ -x "$file" ]; then
        echo "✓ File is executable"
    else
        echo "✗ File is not executable"
    fi
else
    echo "File '$file' not found."
fi