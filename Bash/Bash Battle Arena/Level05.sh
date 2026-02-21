#!/bin/bash
# level05.sh
# Boss Battle: Combine directory creation, file creation,
# conditional checks, file movement, and listing contents.

# 1. Create Battlefield directory
mkdir -p Battlefield

# 2. Create character files
touch Battlefield/knight.txt Battlefield/sorcerer.txt Battlefield/rogue.txt

# 3. If knight.txt exists, move it to Archive
if [ -f "Battlefield/knight.txt" ]; then
    mkdir -p Archive
    mv Battlefield/knight.txt Archive/
    echo "knight.txt has been moved to Archive."
else
    echo "knight.txt not found."
fi

# 4. List directory contents
echo "Contents of Battlefield:"
ls Battlefield

echo "Contents of Archive:"
ls Archive 2>/dev/null || echo "Archive directory does not exist."