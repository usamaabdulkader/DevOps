DIRECTORY="."
WORD="ERROR"

if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist."
    exit 1
fi

find "$DIRECTORY" -type f -name "*.log" -exec grep -li "$WORD" {} + 