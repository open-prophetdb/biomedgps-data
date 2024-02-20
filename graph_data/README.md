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

### Raw User Defined Knowledge Graph File
Raw user defined knowledge graph dataset uses the Raw IDs. The knowledge graph can be stored in a single file (only providing the trainset) or in three files (trainset, validset and testset). Each file stores the triplets of the knowledge graph. The order of head, relation and tail can be arbitry, e.g. [h, r, t]. A delimiter should be used to seperate them. The recommended delimiter is \t.

```
Gene::ENTREZ:8350       Hetionet::GiG::Gene:Gene        Gene::ENTREZ:54583
Gene::ENTREZ:1022       bioarx::HumGenHumGen::Gene:Gene  Gene::ENTREZ:890
Gene::ENTREZ:2534       STRING::REACTION::Gene:Gene     Gene::ENTREZ:5063
```


### Knowledge Graph File

The knowledge graph file is a tab-separated file with the following format:

```
relation_type   resource        pmids   key_sentence    source_id       source_type     target_id       target_type     source_name     target_name
DGIDB::INHIBITOR::Gene:Compound DGIDB                   ENTREZ:4311     Gene    MESH:D015244    Compound        membrane metalloendopeptidase   Thiorphan
DGIDB::INHIBITOR::Gene:Compound DGIDB                   ENTREZ:4311     Gene    MESH:C097292    Compound        membrane metalloendopeptidase   aladotrilat
```

### Annotated Knowledge Graph File

The annotated knowledge graph file is a tab-separated file with the following format:

```
relation_type   resource        pmids   key_sentence    source_id       source_type     target_id       target_type     source_name     source_description      target_name        target_description
DGIDB::INHIBITOR::Gene:Compound DGIDB                   ENTREZ:4311     Gene    MESH:D015244    Compound        membrane metalloendopeptidase   The protein encoded by this gene is a type II transmembrane glycoprotein and a common acute lymphocytic leukemia antigen that is an important cell surface marker in the diagnosis of human acute lymphocytic leukemia (ALL). The encoded protein is present on leukemic cells of pre-B phenotype, which represent 85% of cases of ALL. This protein is not restricted to leukemic cells, however, and is found on a variety of normal tissues. The protein is a neutral endopeptidase that cleaves peptides at the amino side of hydrophobic residues and inactivates several peptide hormones including glucagon, enkephalins, substance P, neurotensin, oxytocin, and bradykinin. [provided by RefSeq, Aug 2017].   Thiorphan       A potent inhibitor of membrane metalloendopeptidase (ENKEPHALINASE). Thiorphan potentiates morphine-induced ANALGESIA and attenuates naloxone-precipitated withdrawal symptoms.
DGIDB::INHIBITOR::Gene:Compound DGIDB                   ENTREZ:4311     Gene    MESH:C097292    Compound        membrane metalloendopeptidase   The protein encoded by this gene is a type II transmembrane glycoprotein and a common acute lymphocytic leukemia antigen that is an important cell surface marker in the diagnosis of human acute lymphocytic leukemia (ALL). The encoded protein is present on leukemic cells of pre-B phenotype, which represent 85% of cases of ALL. This protein is not restricted to leukemic cells, however, and is found on a variety of normal tissues. The protein is a neutral endopeptidase that cleaves peptides at the amino side of hydrophobic residues and inactivates several peptide hormones including glucagon, enkephalins, substance P, neurotensin, oxytocin, and bradykinin. [provided by RefSeq, Aug 2017].   aladotrilat
```
