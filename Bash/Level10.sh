mkdir -p Arena_Boss
dir=("Arena_Boss/file1.txt" "Arena_Boss/file2.txt" "Arena_Boss/file3.txt" "Arena_Boss/file4.txt" "Arena_Boss/file5.txt")

for file in "${dir[@]}"
do
    echo " file: $file"
    num=$(( 10 + RANDOM % 11 ))
    for (( i=1; i<=num; i++ ))
    do
    echo "Some text" >> "$file"
    done
done

ls -lh Arena_Boss/* 

mkdir -p Arena_Boss/Victory_Archive/
find "$dir" -type f -exec grep -l "Victory" {} + | while read file;
do
    mv "$file" Arena_Boss/Victory_Archive/
done



# alt sol

#!/bin/bash

mkdir Arena_Boss

for i in {1..5}
do
    FILE="Arena_Boss/file$i.txt"
    LINES=$((RANDOM % 11 + 10))
    for j in $(seq 1 $LINES)
    do
        echo "This is line $j" >> "$FILE"
    done
done

echo "Files sorted by size:"
find Arena_Boss -type f -exec ls -lh {} + | sort -k 5,5 -h


mkdir -p Victory_Archive
for FILE in Arena_Boss/*.txt
do
    if grep -q "Victory" "$FILE"; then
        mv "$FILE" Victory_Archive/
        echo "$FILE contains 'Victory' and has been moved to Victory_Archive."
    fi
done
