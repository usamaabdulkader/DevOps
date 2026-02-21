#!/bin/bash
# backup_txt.sh
# Description: Backs up all .txt files from a source directory
#              into a timestamped backup directory.
# Usage: ./backup_txt.sh

read -p "Enter source directory: " dir

if [ ! -d "$dir" ]; then
    echo "No directory found."
    exit 1
fi

stamp=$(date +%F_%H-%M)
backup_dir="backup/backup_$stamp"

mkdir -p "$backup_dir"

echo "Backup directory created: $backup_dir"
echo "Copying .txt files..."

count=0

for file in "$dir"/*.txt; do
    [ -e "$file" ] || continue
    cp "$file" "$backup_dir"
    ((count++))
done

echo "Backup complete! Files backed up: $count"






