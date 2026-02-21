#!/bin/bash
# level10.sh
# Boss Battle 2 - Intermediate Scripting

mkdir -p Arena_Boss

# Create files with random line counts (10–20)
for i in {1..5}; do
    FILE="Arena_Boss/file$i.txt"
    LINES=$((RANDOM % 11 + 10))

    for ((j=1; j<=LINES; j++)); do
        echo "This is line $j" >> "$FILE"
    done
done

echo "Files sorted by size:"
find Arena_Boss -type f -exec ls -lh {} + | sort -k 5,5 -h

mkdir -p Victory_Archive

# Move files containing "Victory"
for FILE in Arena_Boss/*.txt; do
    if grep -q "Victory" "$FILE"; then
        mv "$FILE" Victory_Archive/
        echo "$FILE contains 'Victory' and has been moved."
    fi
done

