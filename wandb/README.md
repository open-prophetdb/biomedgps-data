## Environment

```bash
# We assume you are using a conda environment
# Please confirm that you have installed CUDA==11.6 or CUDA==11.7

# torchvision==0.14.0 & torch==1.13 only work with CUDA==11.6 or CUDA==11.7 and python==3.10
conda create -n biomedgps python==3.10

# If you have installed CUDA==11.6 or CUDA==11.7, you can use the following command to install torch==1.13
# dglke is compatible with dgl==0.9.0 and dgl==0.9.0 only works with torch==1.13
pip3 install torch==1.13 torchvision==0.14.0

# Install dglke
pip install git+https://github.com/yjcyxky/dgl-ke.git#subdirectory=python && pip install ogb dgl==0.9.0 wandb
```

> NOTE: 
> 1. The training script is based on a customized dgl-ke library, which is forked from the original dgl-ke library. The customized dgl-ke library is located at [dgl-ke](https://github.com/yjcyxky/dgl-ke.git). The most of the arguments are the same as the original dgl-ke library. The only difference is that the customized dgl-ke library supports wandb and initial embeddings. If you want to know more about the original dgl-ke library, please refer to [dgl-ke docs](https://dglke.dgl.ai/doc/)
> 
> 2. The overall training has already been mostly automated, with the help of Wandb.
>
> 3. If you don't want to use Wandb, you can run it directly through bash train.sh <parameters>.
>
> 4. Wandb will automatically combine all the hyperparameters listed in the configuration file and try to find the optimal hyperparameters. In addition, all logs, performance metrics, model files, data, etc., of the model will be uploaded to your own Wandb account for subsequent tracking and analysis.

## Prepare Data

We assume that you have a set of relation files, such as `formatted_drkg.tsv`, `unformatted_drkg.tsv`, `formatted_ctd.tsv`, `formatted_hsdn.tsv`, `formatted_custom_all_v20240119.tsv`. If you don't have these files, please refer to [graph_data](../graph_data/KG_README.md) for more details about how to generate these files. You also can use your own relation files, please refer to [graph_data](../graph_data/README.md) for more details about the data format. 

After you have the relation files, you can run the [prepare_dataset.ipynb](../graph_data/prepare_dataset.ipynb) notebook to prepare the training/validation/test datasets. The notebook will generate the following files:

```
<your-dir>
  |-- <dataset_name>              # Created by `prepare_dataset.ipynb`, used to store the raw data
  |    |-- test.tsv               # Training set, each line contains a triplet [h, r, t]
  |    |-- valid.tsv              # Validation set, each line contains a triplet [h, r, t]
  |    |-- train.tsv              # Test set, each line contains a triplet [h, r, t]
  |    |-- annotated_entities.tsv # Each line contains an entity and its type
  |    |-- knowledge_graph.tsv    # Each line contains a relation, a head entity and a tail entity etc.
  |    |-- id_checked.tsv         # Each line contains number of intersections between train/valid/test datasets
```

### Relation Files

You can find the formatted relation files in the [formatted_relations](./formatted_relations) folder and the `graph_data/custom_relations` folder.

```bash
graph_data/formatted_relations
    |-- drkg
    |    |-- unformatted_drkg.tsv
    |    |-- formatted_drkg.tsv
    |-- hsdn
    |    |-- formatted_hsdn.tsv
    |-- ctd
    |    |-- formatted_ctd.tsv
    |-- <more databases ...>

custom_relations
    |-- formatted_custom_all_v202401  # This file is curated by the BioMedGPS community.
    |-- formatted_custom_mecfs.tsv    # This file is curated by the BioMedGPS community for the ME/CFS disease.
    |-- formatted_malacards_mecfs.tsv # This file is curated by the BioMedGPS community from the Malacards database for the ME/CFS disease.
```

> **[Additional]** If you want to use initial embeddings to improve the performance of the model, please refer to [embeddings](../embeddings/README.md) for generating initial embeddings.

### Train/Valid/Test File

The train/valid/test file is a tab-separated file with the following format, we call it triplet file, each file contains a list of triplets which are represented by [head_entity_id, relation_id, tail_entity_id]. The format of each head_entity_id and tail_entity_id is composed of entity_type and database_id, such as `Gene::ENTREZ:1234`, `Disease::MONDO:1234`, `Compound::DRUGBANK:DB1234`.

```
Gene::ENTREZ:3358       DGIDB::OTHER::Gene:Compound     Compound::MESH:D008784
Gene::ENTREZ:347688     DGIDB::INHIBITOR::Gene:Compound Compound::DrugBank:DB01394
Gene::ENTREZ:5914       DGIDB::OTHER::Gene:Compound     Compound::DrugBank:DB01394
```

### Understand your data

If you want to know more about your graph data, please refer to [graph_analysis](../graph_analysis/README.md) for more details.

## Training

The project is configured to run a sweep on the job queue and job. The sweep is configured in wandb_sweep_kge.yaml. The sweep will run a job on a set of hyperparameters. The job will run a training script, train.sh. If you want to know more about the sweep, please refer to [wandb sweep](https://docs.wandb.ai/guides/sweeps/quickstart).

### Step 0: Upload/Copy the dataset

Upload/copy the <your-dir>/<dataset_name> directory to the directory you specified in the wandb config file. [Recommended] You can place the <dataset_name> directory in the same directory as the train.sh file and change the data_path argument in the wandb config file to the directory where the dataset is located.

> NOTE: the dataset_name should be replaced by your own dataset name. You also need to keep them same with the dataset name you use in the `../wandb/wandb_sweep_kge.yaml` file.

### Step 1: Login to wandb

if you don't have an account, please register one at https://wandb.ai/. After you login at the website, you can find your API key at https://wandb.ai/authorize.

```bash
wandb login
```

### Step 2: Create a project

Create a project at https://wandb.ai/ and replace <project_name> with your project name

### Step 3: Register a sweep

Before you register a sweep, you need to change the arguments in [wandb_sweep_kge.yaml](./wandb_sweep_kge.yaml). You can find the arguments in train.sh. You can also add more arguments in [wandb_sweep_kge.yaml](./wandb_sweep_kge.yaml) and [train.sh](./train.sh). More details on the arguments can be found in the [Arguments](#Arguments) section.

```bash
# Write a sweep config file and a script to run, such as train.sh and wandb_sweep_kge.yaml
# Run sweep
wandb sweep --project <project_name> wandb_sweep_kge.yaml

# NOTE: The sweep_id is printed when you run wandb sweep
```

### Step 4: Run sweep agent

```bash
# Run sweep agent, you can find the sweep_id in the output of the previous command
wandb agent <wandb_account>/<project_name>/<sweep_id>

# NOTE: You can find all the hyperparameters and results in the sweep page at https://wandb.ai/.
```

### Step 5: Check the results

You can find the results in the sweep page at https://wandb.ai/. You can also find the results in the local directory you specified in the wandb config file. Finally, the directory structure should be like this:

```bash
<your-dir>
  |-- <dataset_name>
  |    |-- entities.tsv           # Generated by the dgl-ke package automatically, ID mapping of entities
  |    |-- relations.tsv          # Generated by the dgl-ke package automatically, ID mapping of relations
  |    |-- ...                    # Other files generated by the prepare_dataset.ipynb script
  |-- models                      # Created by wandb automatically, used to store the trained embeddings
  |    |-- <model_name>
  |    |    |-- config.json
  |    |    |-- <dataset_name>_<model>_entity.npy
  |    |    |-- <dataset_name>_<model>_relation.npy
  |-- wandb                       # Created by wandb automatically, used to store the logs
```

> NOTE:
> THe `models/<model_name>` directory will have the following files, The trained embeddings are generated by dglke_train or dglke_dist_train CMD. The trained embeddings are stored in npy format. Usually there are two files:
> 
> Entity embeddings Entity embeddings are stored in a file named in format of <dataset_name>_<model>_entity.npy and can be loaded through numpy.load().
> 
> Relation embeddings Relation embeddings are stored in a file named in format of <dataset_name>_<model>_relation.npy and can be loaded through numpy.load().

## Evaluate the model

You can login to your wandb account and find the evaluation results in the project you created. You can also find the evaluation results in the log file. The log file is located at the directory you specified in the save_path argument. The log file is named in format of <dataset_name>_<model_name>.log.

## Predict and Visualize

You can use the trained embeddings to predict the probability of a triplet. Please refer to [predict](../prediction/README.md) for more details.

You can also use the trained embeddings to visualize the embeddings. Please refer to [embedding analysis](../embedding_analysis/README.md) for more details.

## Explain Your Results

More details can be found in the [biomedgps-explainer](https://github.com/yjcyxky/biomedgps-explainer) repository.

## Advanced Usage

### Arguments (Hyperparameters)

Please see the arguments in wandb_sweep_kge.yaml and train.sh. The arguments are listed below. If you find any arguments are listed in wandb_sweep_kge.yaml/train.sh but not in the following list, it just means that the argument is supported by customized dgl-ke but is not listed in the following list.

- enable_embedding: Enable embedding. If it is set to False, the model will not use embedding. If you don't want to use embedding, please set it to False in the wandb_sweep.yaml file.

- wandb_entity: The entity name in wandb. If you want to use wandb to visualize the embeddings, please set it to the entity name in wandb.

- model_name: {TransE, TransE_l1, TransE_l2, TransR, RESCAL, DistMult, ComplEx, RotatE}. The models provided by DGL-KE.

- data_path: DATA_PATH The path of the directory where DGL-KE loads knowledge graph data.

- dataset: DATA_SET The name of the knowledge graph stored under data_path. If it is one of the builtin knowledge grpahs such as FB15k, FB15k-237, wn18, wn18rr, and Freebase, DGL-KE will automatically download the knowledge graph and keep it under data_path.

- format: FORMAT The format of the dataset. For builtin knowledge graphs, the format is determined automatically. For users own knowledge graphs, it needs to be raw_udd_{htr} or udd_{htr}. raw_udd_ indicates that the user's data use raw ID for entities and relations and udd_ indicates that the user's data uses KGE ID. {htr} indicates the location of the head entity, tail entity and relation in a triplet. For example, htr means the head entity is the first element in the triplet, the tail entity is the second element and the relation is the last element.

- data_files: [DATA_FILES ...] A list of data file names. This is required for training KGE on their own datasets. If the format is raw_udd_{htr}, users need to provide train_file [valid_file] [test_file]. If the format is udd_{htr}, users need to provide entity_file relation_file train_file [valid_file] [test_file]. In both cases, valid_file and test_file are optional.

- delimiter: DELIMITER Delimiter used in data files. Note all files should use the same delimiter.

- save_path: SAVE_PATH The path of the directory where models and logs are saved.

- no_save_emb: Disable saving the embeddings under save_path.

- max_step: MAX_STEP The maximal number of steps to train the model in a single process. A step trains the model with a batch of data. In the case of multiprocessing training, the total number of training steps is MAX_STEP * NUM_PROC.

- batch_size: BATCH_SIZE The batch size for training.

- batch_size_eval: BATCH_SIZE_EVAL The batch size used for validation and test.

- neg_sample_size: NEG_SAMPLE_SIZE The number of negative samples we use for each positive sample in the training.

- neg_deg_sample: Construct negative samples proportional to vertex degree in the training. When this option is turned on, the number of negative samples per positive edge will be doubled. Half of the negative samples are generated uniformly whilethe other half are generated proportional to vertex degree.

- neg_deg_sample_eval: Construct negative samples proportional to vertex degree in the evaluation.

- neg_sample_size_eval: NEG_SAMPLE_SIZE_EVAL The number of negative samples we use to evaluate a positive sample.

- eval_percent: EVAL_PERCENT Randomly sample some percentage of edges for evaluation.

- no_eval_filter: Disable filter positive edges from randomly constructed negative edges for evaluation.

- log: LOG_INTERVAL Print runtime of different components every LOG_INTERVAL steps.

- eval_interval: EVAL_INTERVAL Print evaluation results on the validation dataset every EVAL_INTERVAL steps if validation is turned on.

- test: Evaluate the model on the test set after the model is trained.

- num_proc: NUM_PROC The number of processes to train the model in parallel. In multi-GPU training, the number of processes by default is the number of GPUs. If it is specified explicitly, the number of processes needs to be divisible by the number of GPUs.

- num_thread: NUM_THREAD The number of CPU threads to train the model in each process. This argument is used for multi-processing training.

- force_sync_interval: FORCE_SYNC_INTERVAL We force a synchronization between processes every FORCE_SYNC_INTERVAL steps for multiprocessing training. This potentially stablizes the training process to get a better performance. For multiprocessing training, it is set to 1000 by default.

- hidden_dim: HIDDEN_DIM The embedding size of relations and entities.

- lr: LR The learning rate. DGL-KE uses Adagrad to optimize the model parameters.

- gamma: GAMMA The margin value in the score function. It is used by TransX and RotatE.

- double_ent: Double entitiy dim for complex number It is used by RotatE.

- double_rel: Double relation dim for complex number.

- neg_adversarial_sampling: Indicate whether to use negative adversarial sampling.It will weight negative samples with higher scores more.

- adversarial_temperature: ADVERSARIAL_TEMPERATURE The temperature used for negative adversarial sampling.

- regularization_coef: REGULARIZATION_COEF The coefficient for regularization.

- regularization_norm: REGULARIZATION_NORM norm used in regularization.

- gpu: [GPU ...] A list of gpu ids, e.g. 0 1 2 4

- mix_cpu_gpu: Training a knowledge graph embedding model with both CPUs and GPUs.The embeddings are stored in CPU memory and the training is performed in GPUs.This is usually used for training large knowledge graph embeddings.

- valid: Evaluate the model on the validation set in the training.

- rel_part: Enable relation partitioning for multi-GPU training.

- async_update: Allow asynchronous update on node embedding for multi-GPU training. This overlaps CPU and GPU computation to speed up.

### Strategies for improving model performance

#### Improve the data quality

According to our experiments, the performance of the model is highly related to the quality of the data. If the data is noisy, the performance of the model will be poor. We think the number of entities and relations in the knowledge graph is an important factor, and more entities and relations might lead to better performance. More importantly, the diversity of entities and relations is an important factor. For example, due to the lack of appropriate connections, your knowledge graph may contain N subgraphs. Completing some relationships to enrich the local connections of the knowledge graph may help to improve the overall predictive performance.

> The idea that enriching the local connections in a knowledge graph can improve its overall predictive performance is generally correct. Here's why:
> 
> Enhanced Connectivity: Knowledge graphs represent entities and their interrelations. When there are missing or weak connections (i.e., relationships or links) within the graph, the ability of the graph to represent complex relationships and dependencies is hindered. Adding relevant connections can make the graph more interconnected and holistic.
>
> Improved Context Understanding: In many AI applications, especially those involving natural language processing or recommendation systems, context is crucial. More connections in a knowledge graph can provide a richer context, which allows for better interpretation and understanding of the data.
>
> Better Data Integration: Knowledge graphs often integrate data from multiple sources. By adding more connections, the integration becomes more comprehensive, leading to a more accurate and complete representation of knowledge.
> 
> Enhanced Predictive Analytics: With a more connected graph, algorithms that traverse this graph (like graph neural networks) can make better predictions, as they have access to more relevant information.
>
> However, it's important to note that the quality of the connections matters. Adding irrelevant or incorrect relationships can lead to noise in the data, which might degrade the performance of predictive models. Therefore, while adding connections can be beneficial, it should be done thoughtfully and accurately to ensure that the overall quality of the knowledge graph is maintained or improved.

#### Use initial embeddings from a pretrained large language model

More details can be found in [embeddings](../embeddings/README.md).

#### Extract more attributes from the publications by using a pretrained large language model [TODO]

#### Integrate multiomics data [TODO]

#### Integrate electronic health records (EHR) [TODO]

#### Other strategies [TODO]