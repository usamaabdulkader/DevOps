file="demo.txt"
dir="bash_demo"
mkdir -p "$dir"
echo "This file was created by a Bash script on $(date +%F)" > "$dir"/"$file"

content="$(cat "$dir"/"$file")"

echo "Directory '$dir' created. File '$file' created."
echo "file contents: $content"