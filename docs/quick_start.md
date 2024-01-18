---
hide:
	- navigation
---

# BioMedGPS Data

A repo for building a knowledge graph and training knowledge graph embedding models for drug repurposing and disease mechanism research.

## Table of Contents

- [Introduction](#introduction)
  - [Key Steps in the Project](#key-steps-in-the-project)
  - [Related Papers](#related-papers)
- [Install Dependencies](#install-dependencies)
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
- [GNN/KGE Models](#gnn-models)
  - [Train KGE models](#traning-train-knowledge-graph-embedding-models)
  - [Evaluate KGE models](#prediction-evaluate-knowledge-graph-embedding-models)
  - [Benchmark KGE models](#benchmark-knowledge-graph-embedding-models)
- [Downstream Analysis](#analysis)
  - [Analyze the knowledge graph](#analyze-the-knowledge-graph)
  - [Analyze the knowledge graph embedding models](#analyze-the-knowledge-graph-embedding-models)
  - [Link Prediction](#link-prediction)
  - [Explain the prediction results](#explain-the-prediction-results)

## Introduction

### Key Steps in the Project

If you want to use the pre-built knowledge graph and the pre-trained knowledge graph embedding models, you can skip the following steps and access [our online service](https://drugs.3steps.cn/).

If you only want to use and analyze the pre-built knowledge graph, you can follow the instructions in the [README.md](https://github.com/open-prophetdb/biomedgps-data/blob/main/graph_data/README.md) file to download the pre-built knowledge graph. After that, you can see the [graph_analysis](https://github.com/open-prophetdb/biomedgps-data/blob/main/graph_analysis) directory to analyze the knowledge graph.

If you are interested in how the training scripts work, you can see the [examples](https://github.com/open-prophetdb/biomedgps-data/blob/main/examples/notebooks) directory.

If you want to prepare a dataset for training the knowledge graph embedding models, you can see the [datasets](https://github.com/open-prophetdb/biomedgps-data/blob/main/datasets) directory.

If you want to train the knowledge graph embedding models by yourself, you can see the [wandb](https://github.com/open-prophetdb/biomedgps-data/blob/main/wandb) directory.

If you want to analyze the knowledge graph embedding models, you can see the [embedding_analysis](https://github.com/open-prophetdb/biomedgps-data/blob/main/embedding_analysis) directory.

If you want to benchmark the knowledge graph embedding models, you can see the [benchmarks](https://github.com/open-prophetdb/biomedgps-data/blob/main/benchmarks) directory.

Please note that it is not necessary to run all the steps in the project. You can run the steps you are interested in. But you need to make sure the dependencies among the steps. For example, if you want to train the knowledge graph embedding models, you need to build a knowledge graph or download the pre-built knowledge graph first. If you want to analyze the knowledge graph embedding models, you need to train the knowledge graph embedding models first.

- Build a knowledge graph

  A knowledge graph is a graph-structured database that contains entities and relations. The entities are the nodes in the graph and the relations are the edges in the graph. The knowledge graph can be used to represent the biomedical knowledge and the relations between entities. A biomedical knowledge graph can be used for drug repurposing and disease mechanism research. Such as:

  ![Knowledge Graph](https://raw.githubusercontent.com/open-prophetdb/biomedgps-data/main/assets/knowledge_graph.png)

  <p style="text-align: center;"><i>From Nicholson et al. CSBJ 2020.</i></p>
  
  The knowledge graph can be used to train knowledge graph embedding models.

  ![Model](https://raw.githubusercontent.com/open-prophetdb/biomedgps-data/main/assets/gnn_model.png)

  <p style="text-align: center;"><i>From Nicholson et al. CSBJ 2020.</i></p>
  
  But before that, we need to do some preprocessing to build a knowledge graph. Such as `Entity Alignment`, `Entity Disambiguation`. The following figure shows the key steps in the project.

  ![Key Steps](https://raw.githubusercontent.com/open-prophetdb/biomedgps-data/main/assets/key_steps.png)

  <p style="text-align: center;"><i>Unknown Source [TBD]</i></p>

- Analyze the knowledge graph

- Train & Evaluate KGE models

- Benchmark KGE models

- Analyze the KGE models

- Link Prediction

- Explain the prediction results

### Related Papers

Before you start, I recommend you to read the following papers:

- Barabási, A.-L., Gulbahce, N. & Loscalzo, J. Network medicine: a network-based approach to human disease. Nat. Rev. Genet. 12, 56–68 (2011).

- Nicholson, David N., and Casey S. Greene. "Constructing knowledge graphs and their biomedical applications." Computational and structural biotechnology journal 18 (2020): 1414-1428.

- Ioannidis, Vassilis N. and Song, Xiang and Manchanda, Saurav and Li, Mufei and Pan, Xiaoqin and Zheng, Da and Ning, Xia and Zeng, Xiangxiang and Karypis, George. DRKG - Drug Repurposing Knowledge Graph for Covid-19. <a href="https://github.com/gnn4dr/DRKG/blob/master/DRKG%20Drug%20Repurposing%20Knowledge%20Graph.pdf" target="_blank">PDF</a>

## Install Dependencies

> NOTE: 
> 1. Python >=3.10 is required.
> 2. All scripts in the repository are dependent on the following dependencies. If you want to run the scripts/jupyter notebooks in this repository, you need to install all dependencies first. In addition, you need to specify the python kernel in the jupyter notebook to the python environment you created when running a jupyter notebook in this repository.

We assume that you have download/clone this repository to your local machine. If not, please download/clone this repository to your local machine first.

```bash
# Clone the repository
git clone https://github.com/open-prophetdb/biomedgps-data

cd biomedgps-data
```

We recommend you to use [virtualenv](https://virtualenv.pypa.io/en/latest/) or [conda](https://docs.conda.io/en/latest/) to install the dependencies. If you don't have virtualenv or conda installed, you can install them by following the instructions in the official document.

```
# [Option 1] Install the dependencies with virtualenv
virtualenv -p python3 .env
source .env/bin/activate

# [Option 2] Install the dependencies with conda
conda create -n biomedgps-data python=3.10
conda activate biomedgps-data

# Install the dependencies
pip install -r requirements.txt
```

## Knowledge Graph

This repository contains the codes to build a knowledge graph for BioMedGPS project. Which depends on the [ontology-matcher](https://github.com/yjcyxky/ontology-matcher) package and [graph-builder](https://github.com/yjcyxky/graph-builder) package.

If you want to run the following codes to build a knowledge graph for BioMedGPS project, you need to install all dependencies first. Please see the [Install Dependencies](#install-dependencies) section for more details.

After that, you can run the following codes to build a knowledge graph for BioMedGPS project.

> NOTE: Be sure to activate the python environment you created and located in the root directory of this repository when running the following codes.

```
python run_markdown.py ./graph_data/KG_README.md --run-all

# The run_markdown.py is a script to run the codes in a markdown file. 
# It will extract the code blocks from the markdown file and run them one by one. 
# If you want to run a specific code block, you can use the following command. 
# If you see 'Cannot identify the language' message, this means that the code block is not necessary to run.

python run_markdown.py ./graph_data/KG_README.md
```

If you want to build a knowledge graph for BioMedGPS project step by step by yourself, you can follow the instructions in the [KG_README.md](https://github.com/open-prophetdb/biomedgps-data/blob/main/graph_data/KG_README.md) file.

## GNN Models in Production

### [Traning] Train knowledge graph embedding models

More details can be found in the [wandb](https://github.com/open-prophetdb/biomedgps-data/blob/main/wandb) directory.

### [Benchmark] Benchmark knowledge graph embedding models

More details can be found in the [benchmarks](https://github.com/open-prophetdb/biomedgps-data/blob/main/benchmarks) directory.

## Analysis

### Analyze the knowledge graph

More details can be found in the [graph_analysis](https://github.com/open-prophetdb/biomedgps-data/blob/main/graph_analysis) directory.

### Analyze the knowledge graph embedding models

More details can be found in the [embedding_analysis](https://github.com/open-prophetdb/biomedgps-data/blob/main/embedding_analysis) directory.

### Link Prediction

More details can be found in the [prediction](https://github.com/open-prophetdb/biomedgps-data/blob/main/prediction) directory.

### Explain the prediction results

More details can be found in the [biomedgps-explainer](https://github.com/yjcyxky/biomedgps-explainer) repository.
