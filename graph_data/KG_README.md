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

> NOTE: The format strategy is defined in the [`onto-match`](https://github.com/yjcyxky/ontology-matcher) package. If you want to change the format strategy, you can modify the `onto-match` package. The basic rules are as follows:
> 
> - We select a default ontology for each entity type. For example, we select the MONDO ID for disease, the ENTREZ ID for gene, the DrugBank ID for compound, the HMDB ID for metabolite, the KEGG ID for pathway, the UMLS ID for side-effect, the SYMP ID for symptom, the UMLS ID for anatomy, the GO ID for cellular_component, the GO ID for biological_process, the GO ID for molecular_function, the UMLS ID for pharmacologic_class.
>
> - We will use the `onto-match` package to map the ids to the default ontology. If the mapping result is not successful, we will use the original id as the ontology id.

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

NOTE: If you add a new entity type, you should add a new line in the merge_entities.py file.

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

#### Annotate relations

```bash
# Annotate relations, It will generate two files: graph_data/knowledge_graph.tsv and graph_data/knowledge_graph_annotated.tsv
python graph_data/scripts/annotate_relations.py -e graph_data/entities.tsv -r graph_data/relations.tsv -o graph_data
```
