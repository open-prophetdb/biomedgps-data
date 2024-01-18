## Download the Formatted Data

The formatted data is available at [Google Drive](https://drive.google.com/drive/folders/1DekWFRbGCmGpLHDIZsJCsWvqBYzZ-EoI?usp=sharing)

Now you can download the formatted data and put all data you expected in the `graph_data` folder. Other codes will read the data from this folder.

## ID Format

### Entity ID

We use `entity_id` to represent an entity. It is a string of the following format:

```
<entity_type>:<database_id>
```

such as `Gene::ENTREZ:1234`, `Disease::OMIM:1234`, `Drug::DRUGBANK:DB1234`.

### Relation ID

We use `relation_id` to represent a relation. It is a string of the following format:

```
<resource>::<relation_type>::<source_entity_type>:<target_entity_type>
```

such as `STRING::INTERACTS_WITH::Gene:Gene`, `STRING::INTERACTS_WITH::Gene:Disease`.

## Data Format

### Entity File

The entity file is a tab-separated file with the following format:

```
id	name	label	resource	description	synonyms	pmids	taxid	xrefs
SYMP:0000149	obsolete sudden onset of severe chills	Symptom	SymptomOntology					
SYMP:0000259	dry hacking cough	Symptom	SymptomOntology	A dry cough that is characterized by a rough and loud sound.				
```

### Relation File

The relation file is a tab-separated file with the following format:

```
raw_source_id   raw_target_id   raw_source_type raw_target_type relation_type   resource        pmids   key_sentence    source_id       source_type     target_id   target_type
ENTREZ:2261     CHEMBL:CHEMBL100473     Gene    Compound        DGIDB::OTHER::Gene:Compound     DGIDB                   ENTREZ:2261     Gene    MESH:C113580Compound
ENTREZ:2776     CHEMBL:CHEMBL100473     Gene    Compound        DGIDB::OTHER::Gene:Compound     DGIDB                   ENTREZ:2776     Gene    MESH:C113580Compound
```
