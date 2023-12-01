#!/bin/bash

# Script Description:
# This script scans a specified directory for files larger than 50MB.
# If '-a' argument is false, it compresses these files and records their paths in dvc_imported.txt.
# If '-a' argument is true, it checks if dvc_imported.txt exists and uses DVC to batch add the files listed in it.

# Usage:
# ./script.sh -d <directory_path> -a <true|false>

# Initialize parameters
TARGET_DIR=""
ADD_TO_DVC=false

# Parse command line arguments using getopts
# -d specifies the directory path
# -a specifies whether to add to DVC (true|false)
while getopts ":d:a:" opt; do
  case $opt in
    d) TARGET_DIR=$OPTARG ;;
    a) ADD_TO_DVC=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2
        exit 1 ;;
    :) echo "Option -$OPTARG requires an argument." >&2
      exit 1 ;;
  esac
done

# Check if the required directory parameter is provided
if [ -z "$TARGET_DIR" ]; then
    echo "Usage: $0 -d <directory_to_scan> -a <add_to_dvc>"
    exit 1
fi

echo "Starting the script for directory: $TARGET_DIR"

# Paths for .dvcignore file and dvc_imported.txt file
DVCIGNORE="$TARGET_DIR/.dvcignore"
DVC_IMPORTED_FILE="$TARGET_DIR/dvc_imported.txt"

# Create or clear the dvc_imported.txt file
if [ "$ADD_TO_DVC" = "false" ]; then
    echo "Creating or clearing $DVC_IMPORTED_FILE"
    > "$DVC_IMPORTED_FILE"
fi

# Function to check if a file is excluded by .dvcignore
is_ignored() {
    if [ -f "$DVCIGNORE" ]; then
        if grep -qE "$(basename "$1")" "$DVCIGNORE"; then
            return 0 # File is ignored
        fi

        # Ignore all files without tsv/csv extension
        if ! [[ "$1" =~ \.(tsv|csv)$ ]]; then
            return 0 # File is ignored
        fi
    fi
    return 1 # File is not ignored
}

# Function to process files
process_files() {
    echo "Starting to process files in $TARGET_DIR"
    find "$TARGET_DIR" -type f -size +50M | while read -r file; do
        gz_file="${file}.tar.gz"

        if is_ignored "$file"; then
            echo "Ignoring file $file as per .dvcignore"
            continue
        fi

        if [ -f "$gz_file" ]; then
            echo "File $gz_file already exists, skipping compression"
            continue
        fi

        echo "Compressing file $file to $gz_file"
        filename=$(basename "$file")
        dir=$(dirname "$file")
        temp_file="._${filename}.tar.gz"
        temp_file="$dir/$temp_file"
        tar -czf "$temp_file" "$file" && mv "$temp_file" "$gz_file"
        echo "Compression complete for $file"

        if [ "$ADD_TO_DVC" = "false" ]; then
            echo "Recording $gz_file in $DVC_IMPORTED_FILE"
            echo "$gz_file" >> "$DVC_IMPORTED_FILE"
        fi
    done
    echo "Finished processing files in $TARGET_DIR"
}

# Function to add files to DVC
add_to_dvc() {
    if [ -f "$DVC_IMPORTED_FILE" ]; then
        echo "Adding files listed in $DVC_IMPORTED_FILE to DVC"
        while read -r file; do
            dvc add "$file"
        done < "$DVC_IMPORTED_FILE"
        echo "DVC add operation complete"
    else
        echo "dvc_imported.txt does not exist. No files were added to DVC."
    fi
}

# Main logic
if [ "$ADD_TO_DVC" = "true" ]; then
    echo "Option set to add files to DVC"
    add_to_dvc
else
    echo "Option set to process files without adding to DVC"
    process_files
fi

echo "Script execution completed"
