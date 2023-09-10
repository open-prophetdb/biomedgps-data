#!/bin/bash

export PATH=$PATH:/opt/conda/bin

SCRIPT_DIR=$(dirname $(realpath $0))
DATA_DIR=${SCRIPT_DIR}

mkdir -p ${DATA_DIR}

aget=`which aget`

if [ -z "$aget" ]; then
    echo "aget not found, if you want to use it please install it first."
    aget=wget
else
    echo "Using aget to download files."
    aget=aget
fi

cd ${DATA_DIR}

while read -r line; do
    if [ -f ${line} ]; then
        echo "File ${line} already exists, skipping download."
        continue
    fi

    echo "Downloading ${line}..."
    FILESIZE=`curl -s -I ${line} | awk '/Content-Length/ {printf("%.0f %s\n", $2 / 1024^2, "")}'`
    K=$(($FILESIZE / ($(nproc) / 2)))
    S=$(($(nproc) / 2))

    if [ $FILESIZE -lt 30 ]; then
        aget="wget"
    else
        aget="aget -k ${K}m -s $S"
    fi

    filename=$(basename ${line})
    ${aget} ${line} && gunzip --keep --force -q ${filename}
done < ${SCRIPT_DIR}/download_links.txt