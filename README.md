# Entities
## Extract entities from a set of databases

If you don't download new data, you can skip the following steps.

### Install dependencies

```bash
virtualenv -p python3 .env
source .env/bin/activate

pip install -r requirements.txt
```

### Download the database by following the instructions in each folder in the data directory

> If you want to add a new database, please add a new folder in the data directory and add a README.md file to describe how to download the database and extract entities from the database. After that, please modify the extract_entities.sh file to add the new database.

### Step1: Extract entities

This step will extract entities from a set of databases. 

The following script will run all the scripts in each folder in the data directory and extract entities. All the extracted entities will be saved in the extracted_entities/raw_entities folder. Each database will have a folder in the extracted_entities/raw_entities folder. If not, then it means that the database has not extracted entities. If you don't download the related database, you will get an error.

```bash
bash scripts/extract_entities.sh
```

### Step2: Merge entities

This step will merge all the entities with the same type into one file.

After merged, all the entities will be saved in the extracted_entities/merged_entities folder. All the entities with the same type will be deduplicated by id and merged into one file. Each entity type will have a file in the extracted_entities/merged_entities folder.

```bash
mkdir -p extracted_entities/merged_entities
python scripts/merge_entities.py from-databases -i extracted_entities/raw_entities -o extracted_entities/merged_entities
```

### Step3: Format entities

This step will map the entities to a default ontology and format the entities with a defined fields and format. If you want to add more fields or change the format of a entity id, you can do it at this step.

After formatted, all the entities will be saved in the formatted_entities folder. All the entities with the same type will be mapped to a default ontology which is defined in the `onco-match` package. Each entity type will have a entity file and a pickle file in the formatted_entities folder. The pickle file is the ontology mapping result. If you want to know why your ids is not mapped successfully, you can check the pickle file.

```bash
# For disease
onto-match ontology -i extracted_entities/merged_entities/disease.tsv -o formatted_entities/disease.tsv -O disease
## Keep all duplicated rows
awk -F'\t' 'NR > 1 { count[$1]++ } END { for (item in count) if (count[item] > 1) print item }' formatted_entities/disease.tsv > formatted_entities/disease.duplicated.tsv
## Deduplicate rows by id.
awk -F'\t' 'NR == 1 || !seen[$1]++' formatted_entities/disease.tsv > formatted_entities/disease.filtered.tsv

# For gene
onto-match ontology -i extracted_entities/merged_entities/gene.tsv -o formatted_entities/gene.tsv -O gene -s 5 -b 500
awk -F'\t' 'NR == 1 || ($8 == 10090 || $8 == 9606)' formatted_entities/gene.tsv > formatted_entities/gene.filtered.tsv
## Deduplicate rows by id. The following processes are not necessary at most time.
awk -F'\t' 'NR == 1 || !seen[$1]++' formatted_entities/gene.filtered.tsv > formatted_entities/tmp_gene.filtered.tsv
mv formatted_entities/tmp_gene.filtered.tsv formatted_entities/gene.filtered.tsv

# For compound
onto-match ontology -i extracted_entities/merged_entities/compound.tsv -o formatted_entities/compound.tsv -O compound -s 5 -b 500
## Deduplicate rows by id. The following processes are not necessary at most time.
awk -F'\t' 'NR == 1 || !seen[$1]++' formatted_entities/compound.tsv > formatted_entities/compound.filtered.tsv

# For metabolite
onto-match ontology -i extracted_entities/merged_entities/metabolite.tsv -o formatted_entities/metabolite.tsv -O metabolite -s 5 -b 500
## Deduplicate rows by id. The following processes are not necessary at most time.
awk -F'\t' 'NR == 1 || !seen[$1]++' formatted_entities/metabolite.tsv > formatted_entities/metabolite.filtered.tsv

# For pathway
cp extracted_entities/merged_entities/pathway.tsv formatted_entities/pathway.tsv

# For side-effect
cp extracted_entities/merged_entities/side_effect.tsv formatted_entities/side_effect.tsv

# For symptom
cp extracted_entities/merged_entities/symptom.tsv formatted_entities/symptom.tsv

# For anatomy
cp extracted_entities/merged_entities/anatomy.tsv formatted_entities/anatomy.tsv

# For cellular_component
cp extracted_entities/merged_entities/cellular_component.tsv formatted_entities/cellular_component.tsv

# For biological_process
cp extracted_entities/merged_entities/biological_process.tsv formatted_entities/biological_process.tsv

# For molecular_function
cp extracted_entities/merged_entities/molecular_function.tsv formatted_entities/molecular_function.tsv

# For pharmacologic_class
cp extracted_entities/merged_entities/pharmacologic_class.tsv formatted_entities/pharmacologic_class.tsv
```

### Step4: Merge entity files into one file

This step will merge all the entity files into one file. If we can find a `filtered.tsv` file in the formatted_entities folder, we will use the filtered.tsv file to merge entities. Otherwise, we will use the `tsv` file to merge entities. If you want to keep a subset of entities (such as deduplicating rows with some conditions and filtering rows with specified species etc.), this is a good opportunity to do it. You can do this at the Step3 and save a `*.filtered.tsv` file in the formatted_entities folder. Finally, the merged file will be saved in the graph_data folder. This file can be the reference file for formatting relations.

```bash
mkdir -p graph_data
python scripts/merge_entities.py to-single-file -i formatted_entities -o graph_data/entities.tsv
```

## Entity Description
### Disease

We choose to use the MONDO ontology as the source of disease terms. All other disease terms are mapped to MONDO terms.

For more convience, we also include all entity items from knowledgebases. First, we extract the id, name, description, label, resource fields from the knowledgebases, and then we map the id to MONDO terms by using the `ontology-matcher` tool.

There will be more easier to integrate these knowledgebases into our knowledge graph, if we can identify the unmapped terms first.

# Relations

## Extract relations from a set of databases
