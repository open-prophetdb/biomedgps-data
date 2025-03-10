### Entities
> Extract entities from a set of databases
> 
> For more convience, we also include all entity items from knowledgebases. First, we extract the id, name, description, label, resource fields from the knowledgebases, and then we map the id to MONDO terms by using the `ontology-matcher` tool.
> 
> There will be more easier to integrate these knowledgebases into our knowledge graph, if we can identify the unmapped terms first.
>
> If you want to add a new database, please add a new folder in the data directory and add a README.md file to describe how to download the database, write a python script to extract entities from the database. After that, please modify the extract_entities.sh file to run the python script. You can follow the existing scripts as an example.

#### Step1: Extract entities

This step will extract entities from a set of databases. 

The following script will run all the scripts in each folder in the data directory and extract entities. All the extracted entities will be saved in the graph_data/extracted_entities/raw_entities folder. Each database will have a folder in the graph_data/extracted_entities/raw_entities folder. If not, then it means that the database has not extracted entities. If you don't download the related database, you will get an error.

```bash
# Extract entities from a set of databases

# Clean the extracted entities folder
rm -rf graph_data/extracted_entities

bash graph_data/scripts/extract_entities.sh -t all
```

#### Step2: Merge entities

This step will merge all the entities with the same type into one file. After merged, all the entities will be saved in the graph_data/extracted_entities/merged_entities folder. All the entities with the same type will be deduplicated by id and merged into one file. Each entity type will have a file in the graph_data/extracted_entities/merged_entities folder.

```bash
# Merge entity files by entity type

mkdir -p graph_data/extracted_entities/merged_entities
python graph_data/scripts/merge_entities.py from-databases -i graph_data/extracted_entities/raw_entities -o graph_data/extracted_entities/merged_entities
```

#### Step3: Format entities

This step will map the entities to a default ontology and format the entities with a defined fields and format. If you want to add more fields or change the format of a entity id, you can do it at this step.

After formatted, all the entities will be saved in the formatted_entities folder. All the entities with the same type will be mapped to a default ontology which is defined in the `onto-match` package. Each entity type will have a entity file and a pickle file in the formatted_entities folder. The pickle file is the ontology mapping result. If you want to know why your ids is not mapped successfully, you can check the pickle file.

> NOTE: The format strategy is defined in the [`onto-match`](https://github.com/yjcyxky/ontology-matcher) package. If you want to change the format strategy, you can modify the `onto-match` package. The basic rules are as follows:
> 
> - We select a default ontology for each entity type. For example, we select the MONDO ID for disease, the ENTREZ ID for gene, the DrugBank ID for compound, the HMDB ID for metabolite, the KEGG ID for pathway, the UMLS ID for side-effect, the SYMP ID for symptom, the UMLS ID for anatomy, the GO ID for cellular_component, the GO ID for biological_process, the GO ID for molecular_function, the UMLS ID for pharmacologic_class.
>
> - We will use the `onto-match` package to map the ids to the default ontology. **NOTE: If the mapping result is not successful, we will use the original id as the ontology id.**

```bash
# Format and filter entities by online ontology service

# Clean the formatted entities folder
rm -rf graph_data/formatted_entities

mkdir graph_data/formatted_entities

# More details about the format strategy, please refer to format_entities.sh (We used the onto-match package to map the ids to the default ontology in the format_entities.sh script)
bash graph_data/scripts/format_entities.sh

# [Optional] Merge several entity types into one new entity type, such as you may want to merge the `Symptom` and `Phenotype` into `Phenotype`
sed -i 's/\tSymptom\t/\tPhenotype\t/g' graph_data/formatted_entities/symptom.tsv
```

##### Step4: Merge entity files into one file

This step will merge all the entity files into one file. If we can find a `filtered.tsv` file in the formatted_entities folder, we will use the filtered.tsv file to merge entities. Otherwise, we will use the `tsv` file to merge entities. If you want to keep a subset of entities (such as deduplicating rows with some conditions and filtering rows with specified species etc.), this is a good opportunity to do it. You can do this at the Step3 and save a `*.filtered.tsv` file in the formatted_entities folder. Finally, the merged file will be saved in the graph_data folder. This file can be the reference file for formatting relations. You will get three files: entities.tsv [after deduplication], entities_full.tsv [before deduplication], entities.log [the log file for deduplication].

NOTE: If you add a new entity type, you should change the merge_entities.py file to add the new entity type.

```bash
# Merge formatted entity files into one file, we will get three files: entities.tsv [after deduplication], entities_full.tsv [before deduplication], entities.log [the log file for deduplication]
python graph_data/scripts/merge_entities.py to-single-file -i graph_data/formatted_entities -o graph_data/entities.tsv --deep-deduplication --remove-obsolete
```

### Relations

#### Extract relations from a set of databases

```bash
# Extract relations from a set of databases

## Clean the formatted relations folder
rm -rf graph_data/formatted_relations

## STEP1: The graph-builder tool only supports the following databases CTD, DRKG, PrimeKG, HSDN automatically. Other databases are included in the relations folder. You may need to format them manually by running the main.ipynb files in each subfolder. Like `biosnap`, `cbcg`, `dgidb`, `ttd`.

## STEP2: Run the graph-builder tool to format the preset databases. You might need to prepare a relation_types.tsv file from the relation_types.xlsx file. If you don't want to format the relation types at this step, please don't provide the --relation-type-dict-fpath option.
# graph-builder --database ctd --database drkg --database primekg --database hsdn -d ./graph_data/relations -o ./graph_data/formatted_relations -f ./graph_data/entities.tsv -n 20 --download --skip -l ./graph_data/log.txt --debug --relation-type-dict-fpath ./graph_data/relation_types.tsv
graph-builder --database ctd --database drkg --database primekg --database hsdn -d ./graph_data/relations -o ./graph_data/formatted_relations -f ./graph_data/entities.tsv -n 20 --download --skip -l ./graph_data/log.txt --debug

# graph-builder --database customdb -d ./datasets/biomedgps-v2/knowledge_graph_filtered_corrected_sideeffect.tsv -o ~/Downloads/Test/ -f ./graph_data/entities.tsv -n 20 --download --skip -l ~/Downloads/Test/log.txt --debug --relation-type-dict-fpath ./graph_data/relation_types.tsv
```

#### Output all of relation types listed in the relation files

```bash
# Merge formatted relation files into one file
python graph_data/scripts/merge_relations.py -i graph_data/formatted_relations -o /tmp/relations.tsv

# Output all of relation types listed in the relation files. The relation types are listed in the `relation_type` column.
python graph_data/scripts/extract_relation_types.py -i /tmp/relations.tsv -o /tmp/relation_types.tsv
```

#### Prepare a dataset for training

Please refer to the `prepare_dataset.ipynb` file in the `graph_data` folder.
