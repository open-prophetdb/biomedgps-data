#!/bin/bash

# You must add a new logic for formatting a new entity type in this script.

# NOTE: We don't treat the side effect as an entity type anymore, we treat it as a relationship type. Because the side effect is important attribute of the drug and we use the side effect to connect the drug and disease/symptom at most time. So for convenience, we add all side effect entities to the disease and symptom entities. Instead of distinguishing whether it is a disease or a symptom.
# For disease
awk -F'\t' 'BEGIN {OFS="\t"} {if ($3 == "SideEffect") $3 = "Disease"; print}' graph_data/extracted_entities/merged_entities/side_effect.tsv > graph_data/extracted_entities/merged_entities/formatted_side_effect.tsv
python3 graph_data/scripts/merge_entities.py merge-multiple-files -i graph_data/extracted_entities/merged_entities/disease.tsv -i graph_data/extracted_entities/merged_entities/formatted_side_effect.tsv -o graph_data/extracted_entities/merged_entities/merged_disease.tsv
rm graph_data/extracted_entities/merged_entities/formatted_side_effect.tsv
onto-match ontology -i graph_data/extracted_entities/merged_entities/merged_disease.tsv -o graph_data/formatted_entities/disease.tsv -O disease -s 0 -b 300
rm graph_data/extracted_entities/merged_entities/merged_disease.tsv

# For anatomy
cp graph_data/extracted_entities/merged_entities/anatomy.tsv graph_data/formatted_entities/anatomy.tsv

# For gene
onto-match ontology -i graph_data/extracted_entities/merged_entities/gene.tsv -o graph_data/formatted_entities/gene.tsv -O gene -s 0 -b 1000 

# For compound
onto-match ontology -i graph_data/extracted_entities/merged_entities/compound.tsv -o graph_data/formatted_entities/compound.tsv -O compound -s 0 -b 500 

# For pathway
cp graph_data/extracted_entities/merged_entities/pathway.tsv graph_data/formatted_entities/pathway.tsv

# For pharmacologic_class
cp graph_data/extracted_entities/merged_entities/pharmacologic_class.tsv graph_data/formatted_entities/pharmacologic_class.tsv

# For symptom
awk -F'\t' 'BEGIN {OFS="\t"} {if ($3 == "SideEffect") $3 = "Symptom"; print}' graph_data/extracted_entities/merged_entities/side_effect.tsv > graph_data/extracted_entities/merged_entities/formatted_side_effect.tsv
python3 graph_data/scripts/merge_entities.py merge-multiple-files -i graph_data/extracted_entities/merged_entities/symptom.tsv -i graph_data/extracted_entities/merged_entities/formatted_side_effect.tsv -o graph_data/extracted_entities/merged_entities/merged_symptom.tsv
rm graph_data/extracted_entities/merged_entities/formatted_side_effect.tsv
cp graph_data/extracted_entities/merged_entities/merged_symptom.tsv graph_data/formatted_entities/symptom.tsv

# For molecular_function
cp graph_data/extracted_entities/merged_entities/molecular_function.tsv graph_data/formatted_entities/molecular_function.tsv

# For biological_process
cp graph_data/extracted_entities/merged_entities/biological_process.tsv graph_data/formatted_entities/biological_process.tsv

# For cellular_component
cp graph_data/extracted_entities/merged_entities/cellular_component.tsv graph_data/formatted_entities/cellular_component.tsv

# For metabolite
onto-match ontology -i graph_data/extracted_entities/merged_entities/metabolite.tsv -o graph_data/formatted_entities/metabolite.tsv -O metabolite -s 0 -b 500 

# For phenotype
cp graph_data/extracted_entities/merged_entities/phenotype.tsv graph_data/formatted_entities/phenotype.tsv

# For protein
cp graph_data/extracted_entities/merged_entities/protein.tsv graph_data/formatted_entities/protein.tsv

# For cellline
cp graph_data/extracted_entities/merged_entities/cell_line.tsv graph_data/formatted_entities/cell_line.tsv
