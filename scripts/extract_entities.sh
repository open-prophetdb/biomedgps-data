#!/bin/bash

SCRIPTS_DIR=scripts
DATADIR=databases
FORMATTED_DIR=extracted_entities


OUTPUT_DIR=${FORMATTED_DIR}/raw_entities

# Format all the entities from different sources
rm -rf ${OUTPUT_DIR}
mkdir -p ${OUTPUT_DIR}

# Format the ctdbase
echo "Extracting entities from the ctdbase"
mkdir -p ${OUTPUT_DIR}/ctd
python ${DATADIR}/ctd/format_ctd.py extract-all-entities -b ${DATADIR}/ctd -o ${OUTPUT_DIR}/ctd

# Format the hetionet
echo "Extracting entities from the hetionet"
mkdir -p ${OUTPUT_DIR}/hetionet
python ${DATADIR}/hetionet/format_hetionet.py entities -i ${DATADIR}/hetionet/hetionet-v1.0-nodes.tsv -o ${OUTPUT_DIR}/hetionet

# Format the mondo
echo "Extracting entities from the mondo"
mkdir -p ${OUTPUT_DIR}/mondo
if [ ! -f ${DATADIR}/mondo/MONDO.csv.gz ]; then
    wget 'https://data.bioontology.org/ontologies/MONDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/mondo/MONDO.csv.gz
fi
python ${DATADIR}/mondo/format_mondo.py entities -i ${DATADIR}/mondo/MONDO.csv.gz -o ${OUTPUT_DIR}/mondo

# Format the sympotm ontology
echo "Extracting entities from the sympotm ontology"
mkdir -p ${OUTPUT_DIR}/symptom-ontology
if [ ! -f ${DATADIR}/symptom-ontology/SYMP.csv.gz ]; then
    wget 'https://data.bioontology.org/ontologies/SYMP/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/symptom-ontology/SYMP.csv.gz
fi
python ${DATADIR}/symptom-ontology/format_symptom.py entities -i ${DATADIR}/symptom-ontology/SYMP.csv.gz -o ${OUTPUT_DIR}/symptom-ontology/

# Format the NDF-RT
echo "Extracting entities from the NDF-RT"
mkdir -p ${OUTPUT_DIR}/ndf-rt
python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/ndf-rt/ndfrt_pharmacologic_class.csv -o ${OUTPUT_DIR}/ndf-rt/ndfrt_pharmacologic_class.tsv

# Format the hgnc_mgi
echo "Extracting entities from the hgnc_mgi"
mkdir -p ${OUTPUT_DIR}/hgnc_mgi
if [ ! -f ${DATADIR}/hgnc_mgi/hgnc_complete_set.txt ]; then
    wget ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt -O hgnc_complete_set.txt
fi

if [ ! -f ${DATADIR}/hgnc_mgi/MGI_Gene_Model_Coord.rpt ]; then
    wget http://www.informatics.jax.org/downloads/reports/MGI_Gene_Model_Coord.rpt -O MGI_Gene_Model_Coord.rpt
fi
python ${DATADIR}/hgnc_mgi/format_hgnc_mgi.py --hgnc ${DATADIR}/hgnc_mgi/hgnc_complete_set.txt --mgi ${DATADIR}/hgnc_mgi/MGI_Gene_Model_Coord.rpt --output ${OUTPUT_DIR}/hgnc_mgi/entrez_gene.tsv

# Format the drug bank
echo "Extracting entities from the drug bank"
mkdir -p ${OUTPUT_DIR}/drugbank
python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/drugbank/drugbank_compound.csv -o ${OUTPUT_DIR}/drugbank/drugbank_compound.tsv

# Format the mesh
echo "Extracting entities from the mesh"
mkdir -p ${OUTPUT_DIR}/mesh
if [ ! -f ${DATADIR}/mesh/MESH.csv.gz ]; then
    wget 'https://data.bioontology.org/ontologies/MESH/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/mesh/MESH.csv.gz
fi
python ${DATADIR}/mesh/format_mesh.py entities -i ${DATADIR}/mesh/MESH.csv.gz -o ${OUTPUT_DIR}/mesh

# Format the HMDB
echo "Extracting entities from the HMDB"
mkdir -p ${OUTPUT_DIR}/hmdb
python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/hmdb/hmdb_metabolite.csv -o ${OUTPUT_DIR}/hmdb/hmdb_metabolite.tsv

# Format the meddra
echo "Extracting entities from the meddra"
mkdir -p ${OUTPUT_DIR}/meddra
python ${SCRIPTS_DIR}/csv2tsv.py -i ${DATADIR}/meddra/meddra_side_effect.csv -o ${OUTPUT_DIR}/meddra/meddra_side_effect.tsv

# Format the reactome
echo "Extracting entities from the reactome"
mkdir -p ${OUTPUT_DIR}/reactome
if [ ! -f ${DATADIR}/reactome/ReactomePathways.txt ]; then
    wget "https://reactome.org/download/current/ReactomePathways.txt" -O ${DATADIR}/reactome/ReactomePathways.txt
fi
python ${DATADIR}/reactome/format_reactome.py -i ${DATADIR}/reactome/ReactomePathways.txt -o ${OUTPUT_DIR}/reactome/reactome_pathway.tsv

# Format the uberon
echo "Extracting entities from the uberon"
mkdir -p ${OUTPUT_DIR}/uberon
if [ ! -f ${DATADIR}/uberon/uberon.csv.gz ]; then
    wget 'https://data.bioontology.org/ontologies/UBERON/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/uberon/uberon.csv.gz
fi
python ${DATADIR}/uberon/format_uberon.py entities -i ${DATADIR}/uberon/uberon.csv.gz -o ${OUTPUT_DIR}/uberon

# Format the go
echo "Extracting entities from the gene ontology"
mkdir -p ${OUTPUT_DIR}/go
if [ ! -f ${DATADIR}/go/go.csv.gz ]; then
    wget 'https://data.bioontology.org/ontologies/GO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv' -O ${DATADIR}/go/go.csv.gz
fi
python ${DATADIR}/go/format_go.py entities -i ${DATADIR}/go/go.csv.gz -o ${OUTPUT_DIR}/go