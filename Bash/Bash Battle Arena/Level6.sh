
Arg(){
    if [ "$#" -eq 0 ];then
     echo "No file provided."
     else
     local name="$1"
     wc -l < "$name"
     fi
}

Arg 'while.sh'


#Alt Solution

#!/bin/bash

if [ -z "$1" ]; then
    echo "No file provided"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "File not found!"
    exit 1
fi

LINE_COUNT=$(wc -l < "$1")
echo "The file '$1' has $LINE_COUNT lines."