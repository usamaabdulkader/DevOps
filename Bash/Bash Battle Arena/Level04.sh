#!/bin/bash
# level04.sh
# Mission: Copy all .txt files from the Arena directory
# into a directory named Backup.

mkdir -p Backup

for file in Arena/*.txt; do
    [ -e "$file" ] || continue
    cp "$file" Backup/
done

echo "Copy operation completed."