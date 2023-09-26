#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

SCRIPTS_DIR=scripts
DATADIR=databases
FORMATTED_DIR=graph_data/extracted_entities

OUTPUT_DIR=${FORMATTED_DIR}/raw_entities

ontologies="hetionet mondo symptom-ontology ndf-rt hgnc-mgi drugbank mesh hmdb meddra reactome uberon go cell-line-ontology wikipathways kegg"

# Add arguments to the script
while getopts ":t:h" opt; do
    case $opt in
        h) echo "Usage: extract_entities.sh [-t <ontology_type>]"
           echo "Options:"
           echo "  -t <ontology_type>    The type of ontology to extract entities from. Default: all"
           echo "                       Options: all, ${ontologies}"
           echo "  -h                    Display help message"
           exit
        ;;
        t) ONTOLOGY_TYPE="$OPTARG"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
        ;;
    esac
done

function main() {
    if [ ! -z "$ONTOLOGY_TYPE" ] && [ "$ONTOLOGY_TYPE" != "all" ]; then
        mkdir -p ${OUTPUT_DIR}
        # Check if the ontology type is in the list of ontologies
        for ontology in $ontologies; do
            if [[ ! " ${ontologies[@]} " =~ " ${ontology} " ]]; then
                echo "Invalid ontology type: $ontology"
                echo "Valid ontology types: all, ${ontologies}"
                exit
            fi
        done

        echo "Extracting entities from $ONTOLOGY_TYPE"
        ONTOLOGY_TYPE=$(echo $ONTOLOGY_TYPE | sed 's/-/_/g')
    fi

    if [ "$ONTOLOGY_TYPE" == "all" ]; then
        # Format all the entities from different sources
        rm -rf ${OUTPUT_DIR}
        mkdir -p ${OUTPUT_DIR}
        echo "Extracting entities from all ontologies"
        ONTOLOGY_TYPE=$ontologies
    fi

    for ontology in $ONTOLOGY_TYPE; do
        FUNCTION_NAME="format_${ontology}"
        echo "Executing function: $FUNCTION_NAME"
        # Execute the function
        $FUNCTION_NAME
    done

    echo "Finished extracting all entities. You can find the results in ${OUTPUT_DIR}"
}

function format_hetionet() {
    # Format the hetionet
    echo "Extracting entities from the hetionet"
    mkdir -p ${OUTPUT_DIR}/hetionet
    if [ ! -f ${DATADIR}/hetionet/hetionet-v1.0-nodes.tsv ]; then
        wget https://raw.githubusercontent.com/hetio/hetionet/main/hetnet/tsv/hetionet-v1.0-nodes.tsv -O ${DATADIR}/hetionet/hetionet-v1.0-nodes.tsv
    else
        echo "hetionet-v1.0-nodes.tsv already exists, skipping download"
    fi
    python ${DATADIR}/hetionet/format_hetionet.py entities -i ${DATADIR}/hetionet/hetionet-v1.0-nodes.tsv -o ${OUTPUT_DIR}/hetionet
    printf "Finished extracting entities from hetionet\n\n"
}

function format_mondo() {
    # Format the mondo
    echo "Extracting entities from the mondo"
    mkdir -p ${OUTPUT_DIR}/mondo
    if [ ! -f ${DATADIR}/mondo/MONDO.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/MONDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/mondo/MONDO.csv.gz
    else
        echo "MONDO.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/mondo/format_mondo.py entities -i ${DATADIR}/mondo/MONDO.csv.gz -o ${OUTPUT_DIR}/mondo
    printf "Finished extracting entities from mondo\n\n"
}

function format_symptom_ontology {
    # Format the symptom ontology
    echo "Extracting entities from the symptom ontology"
    mkdir -p ${OUTPUT_DIR}/symptom-ontology
    if [ ! -f ${DATADIR}/symptom-ontology/SYMP.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/SYMP/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/symptom-ontology/SYMP.csv.gz
    else
        echo "SYMP.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/symptom-ontology/format_symptom.py entities -i ${DATADIR}/symptom-ontology/SYMP.csv.gz -o ${OUTPUT_DIR}/symptom-ontology/
    printf "Finished extracting entities from symptom ontology\n\n"
}

function format_ndf_rt() {
    # Format the NDF-RT
    echo "Extracting entities from the NDF-RT"
    mkdir -p ${OUTPUT_DIR}/ndf-rt
    python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/ndf-rt/ndfrt_pharmacologic_class.csv -o ${OUTPUT_DIR}/ndf-rt/ndfrt_pharmacologic_class.tsv
    printf "Finished extracting entities from NDF-RT\n\n"
}

function format_hgnc_mgi() {
    # Format the hgnc_mgi
    echo "Extracting entities from the hgnc_mgi"
    mkdir -p ${OUTPUT_DIR}/hgnc_mgi
    if [ ! -f ${DATADIR}/hgnc_mgi/hgnc_complete_set.txt ]; then
        wget ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt -O hgnc_complete_set.txt
    else
        echo "hgnc_complete_set.txt already exists, skipping download"
    fi
    printf "Finished extracting entities from hgnc_mgi\n\n"

    if [ ! -f ${DATADIR}/hgnc_mgi/MGI_Gene_Model_Coord.rpt ]; then
        wget http://www.informatics.jax.org/downloads/reports/MGI_Gene_Model_Coord.rpt -O MGI_Gene_Model_Coord.rpt
    else
        echo "MGI_Gene_Model_Coord.rpt already exists, skipping download"
    fi
    python ${DATADIR}/hgnc_mgi/format_hgnc_mgi.py --hgnc ${DATADIR}/hgnc_mgi/hgnc_complete_set.txt --mgi ${DATADIR}/hgnc_mgi/MGI_Gene_Model_Coord.rpt --output ${OUTPUT_DIR}/hgnc_mgi/entrez_gene.tsv
    printf "Finished extracting entities from hgnc_mgi\n\n"
}

function format_drugbank() {
    # Format the drug bank
    echo "Extracting entities from the drug bank"
    mkdir -p ${OUTPUT_DIR}/drugbank
    python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/drugbank/drugbank_compound.csv -o ${OUTPUT_DIR}/drugbank/drugbank_compound.tsv
    printf "Finished extracting entities from drug bank\n\n"
}

function format_mesh() {
    # Format the mesh
    echo "Extracting entities from the mesh"
    mkdir -p ${OUTPUT_DIR}/mesh
    if [ ! -f ${DATADIR}/mesh/MESH.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/MESH/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/mesh/MESH.csv.gz
    else
        echo "MESH.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/mesh/format_mesh.py entities -i ${DATADIR}/mesh/MESH.csv.gz -o ${OUTPUT_DIR}/mesh
    printf "Finished extracting entities from mesh\n\n"
}

function format_hmdb() {
    # Format the HMDB
    echo "Extracting entities from the HMDB"
    mkdir -p ${OUTPUT_DIR}/hmdb
    python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/hmdb/hmdb_metabolite.csv -o ${OUTPUT_DIR}/hmdb/hmdb_metabolite.tsv
    printf "Finished extracting entities from HMDB\n\n"
}

function format_meddra() {
    # Format the meddra
    echo "Extracting entities from the meddra"
    mkdir -p ${OUTPUT_DIR}/meddra
    python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/meddra/meddra_side_effect.csv -o ${OUTPUT_DIR}/meddra/meddra_side_effect.tsv
    printf "Finished extracting entities from meddra\n\n"
}

function format_reactome() {
    # Format the reactome
    echo "Extracting entities from the reactome"
    mkdir -p ${OUTPUT_DIR}/reactome
    if [ ! -f ${DATADIR}/reactome/ReactomePathways.txt ]; then
        wget "https://reactome.org/download/current/ReactomePathways.txt" -O ${DATADIR}/reactome/ReactomePathways.txt
    else
        echo "ReactomePathways.txt already exists, skipping download"
    fi
    python ${DATADIR}/reactome/format_reactome.py -i ${DATADIR}/reactome/ReactomePathways.txt -o ${OUTPUT_DIR}/reactome/reactome_pathway.tsv
    printf "Finished extracting entities from reactome\n\n"
}

function format_uberon() {
    # Format the uberon
    echo "Extracting entities from the uberon"
    mkdir -p ${OUTPUT_DIR}/uberon
    if [ ! -f ${DATADIR}/uberon/uberon.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/UBERON/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/uberon/uberon.csv.gz
    else
        echo "uberon.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/uberon/format_uberon.py entities -i ${DATADIR}/uberon/uberon.csv.gz -o ${OUTPUT_DIR}/uberon
    printf "Finished extracting entities from uberon\n\n"
}

function format_go() {
    # Format the go
    echo "Extracting entities from the gene ontology"
    mkdir -p ${OUTPUT_DIR}/go
    if [ ! -f ${DATADIR}/go/go.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/GO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/go/go.csv.gz
    else
        echo "go.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/go/format_go.py entities -i ${DATADIR}/go/go.csv.gz -o ${OUTPUT_DIR}/go
    printf "Finished extracting entities from GO\n\n"
}

function format_cell_line_ontology() {
    # Format the cell line ontology
    echo "Extracting entities from the cell line ontology"
    mkdir -p ${OUTPUT_DIR}/cell-line-ontology
    if [ ! -f ${DATADIR}/cell-line-ontology/CLO.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/CLO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/cell-line-ontology/CLO.csv.gz
    else
        echo "CLO.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/cell-line-ontology/format_clo.py entities -i ${DATADIR}/cell-line-ontology/CLO.csv.gz -o ${OUTPUT_DIR}/cell-line-ontology
    printf "Finished extracting entities from cell line ontology\n\n"
}

function format_wikipathways() {
    # Format the wikipathways
    echo "Extracting entities from the wikipathways"
    mkdir -p ${OUTPUT_DIR}/wikipathways

    if [ -f ${DATADIR}/wikipathways/wikipathways_pathway.tsv ]; then
        echo "wikipathways_pathway.tsv already exists, skipping download"
    else
        python ${DATADIR}/wikipathways/format_wikipathways.py -o ${DATADIR}/wikipathways/wikipathways_pathway.tsv
    fi

    cp ${DATADIR}/wikipathways/wikipathways_pathway.tsv ${OUTPUT_DIR}/wikipathways/wikipathways_pathway.tsv
    printf "Finished extracting entities from wikipathways\n\n"
}

function format_kegg() {
    # Format the kegg
    echo "Extracting entities from the kegg"
    mkdir -p ${OUTPUT_DIR}/kegg

    if [ -f ${DATADIR}/kegg/kegg_pathway.tsv ]; then
        echo "kegg_pathway.tsv already exists, skipping download"
    else
        python ${DATADIR}/kegg/format_kegg.py -o ${DATADIR}/kegg/kegg_pathway.tsv
    fi

    cp ${DATADIR}/kegg/kegg_pathway.tsv ${OUTPUT_DIR}/kegg/kegg_pathway.tsv
    printf "Finished extracting entities from kegg\n\n"
}


main