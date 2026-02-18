#!/bin/bash

DIRECTORY="Arena"

if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist."
    exit 1
fi

find "$DIRECTORY" -type f -name "*.txt" -exec ls -lh {} + | sort -k 5,5 -h | awk '{ print $5, $9 }'

# Explanation: 
# find "$DIRECTORY" -type f -name "*.txt" finds all .txt files. 
# -exec option executes the command ls -lh
# ls -lh lists files with sizes in human-readable format.
# {}   | placeholder for found file    
# \;   | execute command once per file 
# +    | batch files together   
# sort -k 5,5 -h sorts the files by the 5th column (size) in human-readable format.
# awk '{ print $5, $9 }' prints the 5th and 9th column, the size and file name to filter the output of the ls command


        
