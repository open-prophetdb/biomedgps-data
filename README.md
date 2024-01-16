# BioMedGPS Data

A repo for building a knowledge graph and training knowledge graph embedding models for drug repurposing.

- [Knowledge Graph](#knowledge-graph)
  - [Entities](#entities)
    - [Download the database by following the instructions in each folder in the data directory](#download-the-database-by-following-the-instructions-in-each-folder-in-the-data-directory)
    - [Step1: Extract entities](#step1-extract-entities)
    - [Step2: Merge entities](#step2-merge-entities)
    - [Step3: Format entities](#step3-format-entities)
    - [Step4: Merge entity files into one file](#step4-merge-entity-files-into-one-file)
  - [Relations](#relations)
    - [Extract relations from a set of databases](#extract-relations-from-a-set-of-databases)
    - [Merge relations into one file](#merge-relations-into-one-file)
- [GNN/KGE Models for Exercise](#gnnkge-models-for-exercise)
- [GNN/KGE Models in Production](#gnn-models)
  - [Generate initial embeddings for entities and relations](#embedding-generate-initial-embeddings-for-entities-and-relations)
  - [Train gnn models](#traning-train-knowledge-graph-embedding-models)
  - [Evaluate gnn models](#prediction-evaluate-knowledge-graph-embedding-models)
  - [Benchmark gnn models](#benchmark-knowledge-graph-embedding-models)
- [Downstream Analysis](#analysis)
  - [Analyze the knowledge graph](#analyze-the-knowledge-graph)
  - [Analyze the knowledge graph embedding models](#analyze-the-knowledge-graph-embedding-models)
  - [Link Prediction](#link-prediction)
  - [Explain the prediction results](#explain-the-prediction-results)

## Knowledge Graph

This repository contains the codes to build a knowledge graph for BioMedGPS project. Which depends on the [ontology-matcher](https://github.com/yjcyxky/ontology-matcher) package and [graph-builder](https://github.com/yjcyxky/graph-builder) package.

If you only want to use and analyze the pre-built knowledge graph, you can see the [graph_data](./graph_data) directory and the [models](./models) directory.

If you want to run the following codes to build a knowledge graph for BioMedGPS project, you need to install the following dependencies first.

NOTE: Python >=3.10 is required.

```
# Clone the repository
git clone https://github.com/yjcyxky/biomedgps-data

cd biomedgps-data

# [Option 1] Install the dependencies with virtualenv
virtualenv -p python3 .env
source .env/bin/activate

# [Option 2] Install the dependencies with conda
conda create -n biomedgps-data python=3.10
conda activate biomedgps-data

pip install -r requirements.txt
```

After that, you can run the following codes to build a knowledge graph for BioMedGPS project.

```
python run_markdown.py README.md --run-all

# The run_markdown.py is a script to run the codes in a markdown file. 
# It will extract the code blocks from the markdown file and run them one by one. 
# If you want to run a specific code block, you can use the following command. 
# If you see 'Cannot identify the language' message, this means that the code block is not necessary to run.

python run_markdown.py README.md
```

If you want to build a knowledge graph for BioMedGPS project step by step, you can run the following steps.

### Entities
> Extract entities from a set of databases
>
> If you don't need to download new data, you can skip the following steps.

> Disease
>
> We choose to use the MONDO ontology as the source of disease terms. All other disease terms are mapped to MONDO terms.
>
> For more convience, we also include all entity items from knowledgebases. First, we extract the id, name, description, label, resource fields from the knowledgebases, and then we map the id to MONDO terms by using the `ontology-matcher` tool.
> 
> There will be more easier to integrate these knowledgebases into our knowledge graph, if we can identify the unmapped terms first.

#### Download the database by following the instructions in each folder in the data directory

> If you want to add a new database, please add a new folder in the data directory and add a README.md file to describe how to download the database and extract entities from the database. After that, please modify the extract_entities.sh file to add the new database.

#### Step1: Extract entities

This step will extract entities from a set of databases. 

The following script will run all the scripts in each folder in the data directory and extract entities. All the extracted entities will be saved in the graph_data/extracted_entities/raw_entities folder. Each database will have a folder in the graph_data/extracted_entities/raw_entities folder. If not, then it means that the database has not extracted entities. If you don't download the related database, you will get an error.

```bash
# Extract entities from a set of databases

bash graph_data/scripts/extract_entities.sh -t all
```

#### Step2: Merge entities

This step will merge all the entities with the same type into one file.

After merged, all the entities will be saved in the graph_data/extracted_entities/merged_entities folder. All the entities with the same type will be deduplicated by id and merged into one file. Each entity type will have a file in the graph_data/extracted_entities/merged_entities folder.

```bash
# Merge entity files by entity type

mkdir -p graph_data/extracted_entities/merged_entities
python graph_data/scripts/merge_entities.py from-databases -i graph_data/extracted_entities/raw_entities -o graph_data/extracted_entities/merged_entities
```

#### Step3: Format entities

This step will map the entities to a default ontology and format the entities with a defined fields and format. If you want to add more fields or change the format of a entity id, you can do it at this step.

After formatted, all the entities will be saved in the formatted_entities folder. All the entities with the same type will be mapped to a default ontology which is defined in the `onto-match` package. Each entity type will have a entity file and a pickle file in the formatted_entities folder. The pickle file is the ontology mapping result. If you want to know why your ids is not mapped successfully, you can check the pickle file.

```bash
# Format and filter entities by online ontology service

mkdir graph_data/formatted_entities

# For disease
onto-match ontology -i graph_data/extracted_entities/merged_entities/disease.tsv -o graph_data/formatted_entities/disease.tsv -O disease -s 0 -b 300
## Keep all duplicated rows
awk -F'\t' 'NR > 1 { count[$1]++ } END { for (item in count) if (count[item] > 1) print item }' graph_data/formatted_entities/disease.tsv > graph_data/formatted_entities/disease.duplicated.tsv
## Deduplicate rows by id.
awk -F'\t' 'NR == 1 || !seen[$1]++' graph_data/formatted_entities/disease.tsv > graph_data/formatted_entities/disease.filtered.tsv

# For gene
onto-match ontology -i graph_data/extracted_entities/merged_entities/gene.tsv -o graph_data/formatted_entities/gene.tsv -O gene -s 0 -b 1000 
awk -F'\t' 'NR == 1 || ($8 == 10090 || $8 == 9606)' graph_data/formatted_entities/gene.tsv > graph_data/formatted_entities/gene.filtered.tsv
## Deduplicate rows by id. The following processes are not necessary at most time.
awk -F'\t' 'NR == 1 || !seen[$1]++' graph_data/formatted_entities/gene.filtered.tsv > graph_data/formatted_entities/tmp_gene.filtered.tsv
mv graph_data/formatted_entities/tmp_gene.filtered.tsv graph_data/formatted_entities/gene.filtered.tsv

# For compound
onto-match ontology -i graph_data/extracted_entities/merged_entities/compound.tsv -o graph_data/formatted_entities/compound.tsv -O compound -s 0 -b 500 
## Deduplicate rows by id. The following processes are not necessary at most time.
awk -F'\t' 'NR == 1 || !seen[$1]++' graph_data/formatted_entities/compound.tsv > graph_data/formatted_entities/compound.filtered.tsv

# For metabolite
onto-match ontology -i graph_data/extracted_entities/merged_entities/metabolite.tsv -o graph_data/formatted_entities/metabolite.tsv -O metabolite -s 0 -b 500 
## Deduplicate rows by id. The following processes are not necessary at most time.
awk -F'\t' 'NR == 1 || !seen[$1]++' graph_data/formatted_entities/metabolite.tsv > graph_data/formatted_entities/metabolite.filtered.tsv

# For pathway
cp graph_data/extracted_entities/merged_entities/pathway.tsv graph_data/formatted_entities/pathway.tsv

# For side-effect
cp graph_data/extracted_entities/merged_entities/side_effect.tsv graph_data/formatted_entities/side_effect.tsv

# For symptom
cp graph_data/extracted_entities/merged_entities/symptom.tsv graph_data/formatted_entities/symptom.tsv

# For anatomy
cp graph_data/extracted_entities/merged_entities/anatomy.tsv graph_data/formatted_entities/anatomy.tsv

# For cellular_component
cp graph_data/extracted_entities/merged_entities/cellular_component.tsv graph_data/formatted_entities/cellular_component.tsv

# For biological_process
cp graph_data/extracted_entities/merged_entities/biological_process.tsv graph_data/formatted_entities/biological_process.tsv

# For molecular_function
cp graph_data/extracted_entities/merged_entities/molecular_function.tsv graph_data/formatted_entities/molecular_function.tsv

# For pharmacologic_class
cp graph_data/extracted_entities/merged_entities/pharmacologic_class.tsv graph_data/formatted_entities/pharmacologic_class.tsv
```

##### Step4: Merge entity files into one file

This step will merge all the entity files into one file. If we can find a `filtered.tsv` file in the formatted_entities folder, we will use the filtered.tsv file to merge entities. Otherwise, we will use the `tsv` file to merge entities. If you want to keep a subset of entities (such as deduplicating rows with some conditions and filtering rows with specified species etc.), this is a good opportunity to do it. You can do this at the Step3 and save a `*.filtered.tsv` file in the formatted_entities folder. Finally, the merged file will be saved in the graph_data folder. This file can be the reference file for formatting relations.

```bash
# Merge formatted entity files into one file

mkdir -p graph_data
python graph_data/scripts/merge_entities.py to-single-file -i graph_data/formatted_entities -o graph_data/entities.tsv
```

### Relations

#### Extract relations from a set of databases

```bash
# Extract relations from a set of databases

graph-builder --database ctd --database drkg --database primekg --database hsdn -d ./graph_data/relations -o ./graph_data/formatted_relations -f ./graph_data/entities.tsv -n 20 --download --skip -l ./graph_data/log.txt --debug
```

#### Merge relations into one file

```bash
# Merge relations into one file

python graph_data/scripts/merge_relations.py -i graph_data/formatted_relations -o graph_data/relations.tsv
```

## GNN/KGE Models for Exercise

You can follow the instructions in the [notebooks](./examples/README.md) to train a KGE model for exercises. If you want to train a KGE model for your own datasets in production, you can refer to the [README](./wandb/README.md) in the `wandb` folder.

## GNN Models in Production

### [Embedding] Generate initial embeddings for entities and relations

More details can be found in the [embeddings](./embeddings) directory.

### [Traning] Train knowledge graph embedding models

More details can be found in the [wandb](./wandb) directory.

### [Benchmark] Benchmark knowledge graph embedding models

More details can be found in the [benchmarks](./benchmarks) directory.

## Analysis

### Analyze the knowledge graph

More details can be found in the [graph_analysis](./graph_analysis) directory.

### Analyze the knowledge graph embedding models

More details can be found in the [embedding_analysis](./embedding_analysis) directory.

### Link Prediction

More details can be found in the [prediction](./prediction/) directory.

### Explain the prediction results

More details can be found in the [biomedgps-explainer](https://github.com/yjcyxky/biomedgps-explainer) repository.
