echo "enter"
read file

if [ -e "$file" ]
then
    if [ -r "$file" ]
    then
    echo "$file is readable"
    else
    echo "$file isnt readable"
    fi

    if [ -w "$file" ]
    then
    echo "$file is Writable"
    else
    echo "$file isnt Writable"
    fi

    if [ -x "$file" ]
    then
    echo "$file is executable"
    else
    echo "$file isnt executable"
    fi

else
    echo "$file not found"
fi
