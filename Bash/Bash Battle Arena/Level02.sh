#!/bin/bash
# level02.sh
# Mission: Output numbers from 1 to 10, one per line.

for (( i=1; i<=10; i++ )); do
    echo "$i"
done

# Alternative implementations:

# Using while loop
# counter=1
# while [ "$counter" -le 10 ]; do
#     echo "$counter"
#     ((counter++))
# done

# Using brace expansion
# for i in {1..10}; do
#     echo "$i"
# done
