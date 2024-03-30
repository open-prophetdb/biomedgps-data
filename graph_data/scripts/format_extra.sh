#!/bin/bash

export SCRIPTS_DIR=$(dirname $(realpath $0))
export DATADIR=${SCRIPTS_DIR}/../extra
export OUTPUT_DIR=${SCRIPTS_DIR}/../extra

function format_meddra() {
    # Format the meddra
    echo "Extracting entities from the meddra"
    mkdir -p ${OUTPUT_DIR}/meddra
    python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/meddra/meddra.csv -o ${OUTPUT_DIR}/meddra/meddra.tsv
    python ${DATADIR}/meddra/format_meddra.py -i ${OUTPUT_DIR}/meddra/meddra.tsv -o ${OUTPUT_DIR}/meddra/formatted_meddra.tsv --cache-file ${DATADIR}/meddra/meddra_cache
    printf "Finished extracting entities from meddra\n\n"
}

# Run the functions
format_meddra
