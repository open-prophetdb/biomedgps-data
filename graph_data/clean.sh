#!/bin/bash

while getopts ":d:" opt; do
    case ${opt} in
        d )
            DIR=$OPTARG
            ;;
        \? )
            echo "Usage: ./clean.sh [-d] [directory]"
            exit 1
            ;;
    esac
done

if [ -z "$DIR" ]; then
    echo "Usage: ./clean.sh [-d] [directory]"
    exit 1
fi

if [ ! -d "$DIR" ]; then
    echo "Directory $DIR does not exist."
    exit 1
fi

# Remove all files and directories which listed in .gitignore
files=( $(find $DIR -type f -o -type d | git check-ignore --stdin) )

echo "Find ${#files[@]} files and directories in $DIR and listed in .gitignore."
for file in "${files[@]}"; do
    echo "$file"
done

printf "\n\n"
# Ask for confirmation
read -p "Are you sure you want to remove the above files and directories in $DIR and listed in .gitignore? [y/N] " -n 1 -r

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo
    exit 1
fi

for file in "${files[@]}"; do
    rm -rf "$file"
done