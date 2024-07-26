#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

SCRIPTS_DIR=graph_data/scripts
DATADIR=graph_data/entities
FORMATTED_DIR=graph_data/extracted_entities

OUTPUT_DIR=${FORMATTED_DIR}/raw_entities

# We need to add a ontology name for a new ontology
ontologies="hetionet mondo symptom-ontology ndf-rt hgnc mgi meddra drugbank mesh hmdb reactome uberon go cell-line-ontology wikipathways kegg orphanet hpo uniprot"

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
    fi

    if [ "$ONTOLOGY_TYPE" == "all" ]; then
        # Format all the entities from different sources
        rm -rf ${OUTPUT_DIR}
        mkdir -p ${OUTPUT_DIR}
        echo "Extracting entities from all ontologies"
        ONTOLOGY_TYPE=$ontologies
    fi

    for ontology in $ONTOLOGY_TYPE; do
        ontology=$(echo $ontology | sed 's/-/_/g')
        FUNCTION_NAME="format_${ontology}"
        echo "Executing function: $FUNCTION_NAME"
        # Execute the function
        $FUNCTION_NAME
    done

    echo "Finished extracting all entities. You can find the results in ${OUTPUT_DIR}"
}

function format_uniprot() {
    # Format the uniprot
    echo "Extracting entities from the uniprot"
    mkdir -p ${OUTPUT_DIR}/uniprot
    if [ ! -f ${DATADIR}/uniprot/uniprot_sprot.xml.gz ]; then
        echo "Downloading uniprot_sprot.xml.gz, this file is large and may take a while to download..."
        wget https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.xml.gz -O ${DATADIR}/uniprot/uniprot_sprot.xml.gz
    else
        echo "uniprot_sprot.xml.gz already exists, skipping download"
    fi

    if [ ! -f ${DATADIR}/uniprot/uniprot_sprot.xml ]; then
        echo "Decompressing uniprot_sprot.xml.gz"
        gunzip -c ${DATADIR}/uniprot/uniprot_sprot.xml.gz > ${DATADIR}/uniprot/uniprot_sprot.xml
    else
        echo "uniprot_sprot.xml already exists, skipping decompression"
    fi

    if [ ! -f ${DATADIR}/uniprot/uniprot_sprot_filtered.xml ]; then
        echo "Filtering uniprot_sprot.xml, this may take a while..."
        python ${DATADIR}/uniprot/format_uniprot.py filter -i ${DATADIR}/uniprot/uniprot_sprot.xml -o ${DATADIR}/uniprot/uniprot_sprot_filtered.xml
    else
        echo "uniprot_sprot_filtered.xml already exists, skipping filtering"
    fi

    python ${DATADIR}/uniprot/format_uniprot.py entities -i ${DATADIR}/uniprot/uniprot_sprot_filtered.xml -o ${OUTPUT_DIR}/uniprot

    printf "Finished extracting entities from hpo\n\n"

}

function format_hpo() {
    # Format the hpo
    echo "Extracting entities from the hpo"
    mkdir -p ${OUTPUT_DIR}/hpo
    if [ ! -f ${DATADIR}/hpo/hp-base.obo ]; then
        wget https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2024-07-01/hp-base.obo -O ${DATADIR}/hpo/hp-base.obo
    else
        echo "hp-base.obo already exists, skipping download"
    fi
    python ${DATADIR}/hpo/format_hpo.py entities -i ${DATADIR}/hpo/hp-base.obo -o ${OUTPUT_DIR}/hpo
    printf "Finished extracting entities from hpo\n\n"

}

function format_orphanet() {
    # Format the orphanet
    echo "Extracting entities from the orphanet"
    mkdir -p ${OUTPUT_DIR}/orphanet
    if [ ! -f ${DATADIR}/orphanet/ORDO_en_4.5.owl ]; then
        wget https://www.orphadata.com/data/ontologies/ordo/last_version/ORDO_en_4.5.owl -O ${DATADIR}/orphanet/ORDO_en_4.5.owl
    else
        echo "ORDO_en_4.5.owl already exists, skipping download"
    fi
    python ${DATADIR}/orphanet/format_orphanet.py entities -i ${DATADIR}/orphanet/ORDO_en_4.5.owl -o ${OUTPUT_DIR}/orphanet
    printf "Finished extracting entities from orphanet\n\n"

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

function format_hgnc() {
    # Format the hgnc
    echo "Extracting entities from the hgnc"
    mkdir -p ${OUTPUT_DIR}/hgnc
    if [ ! -f ${DATADIR}/hgnc/hgnc_complete_set.txt ]; then
        wget ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt -O hgnc_complete_set.txt
    else
        echo "hgnc_complete_set.txt already exists, skipping download"
    fi
    printf "Finished extracting entities from hgnc\n\n"

    python ${DATADIR}/hgnc/format_hgnc.py --hgnc ${DATADIR}/hgnc/hgnc_complete_set.txt --output ${OUTPUT_DIR}/hgnc/entrez_gene.tsv
    printf "Finished extracting entities from hgnc\n\n"
}

function format_mgi() {
    # Format the mgi
    echo "Extracting entities from the mgi"
    mkdir -p ${OUTPUT_DIR}/mgi

    if [ ! -f ${DATADIR}/mgi/MGI_Gene_Model_Coord.rpt ]; then
        wget http://www.informatics.jax.org/downloads/reports/MGI_Gene_Model_Coord.rpt -O MGI_Gene_Model_Coord.rpt
    else
        echo "MGI_Gene_Model_Coord.rpt already exists, skipping download"
    fi
    python ${DATADIR}/mgi/format_mgi.py --mgi ${DATADIR}/mgi/MGI_Gene_Model_Coord.rpt --output ${OUTPUT_DIR}/mgi/entrez_gene.tsv
    printf "Finished extracting entities from mgi\n\n"
}

function format_drugbank() {
    # Format the drug bank
    echo "Extracting entities from the drug bank"
    mkdir -p ${OUTPUT_DIR}/drugbank
    # python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/drugbank/drugbank_compound.csv -o ${OUTPUT_DIR}/drugbank/drugbank_compound.tsv
    if [ ! -f ${DATADIR}/drugbank/drugbank_vocabulary.csv ]; then
        echo "drugbank_vocabulary.csv does not exist, please follow the instructions in the README to download it from the drugbank website."
        exit 1
    else
        echo "drugbank_vocabulary.csv already exists, skipping download"
    fi
    python ${DATADIR}/drugbank/format_drugbank.py -i ${DATADIR}/drugbank/drugbank_vocabulary.csv -o ${OUTPUT_DIR}/drugbank/drugbank_compound.tsv
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
    mkdir -p ${OUTPUT_DIR}/clo
    if [ ! -f ${DATADIR}/cell-line-ontology/CLO.csv.gz ]; then
        wget 'https://data.bioontology.org/ontologies/CLO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/cell-line-ontology/CLO.csv.gz
    else
        echo "CLO.csv.gz already exists, skipping download"
    fi
    python ${DATADIR}/cell-line-ontology/format_clo.py entities -i ${DATADIR}/cell-line-ontology/CLO.csv.gz -o ${OUTPUT_DIR}/clo
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

function format_meddra() {
    # Format the meddra
    echo "Extracting entities from the meddra"
    mkdir -p ${OUTPUT_DIR}/meddra
    python ${DATADIR}/meddra/format_meddra.py --input ${DATADIR}/meddra/meddra.csv --output ${OUTPUT_DIR}/meddra/meddra_side_effect.tsv --cache-file ${DATADIR}/meddra/meddra_cache.sqlite
    printf "Finished extracting entities from meddra\n\n"
}


main