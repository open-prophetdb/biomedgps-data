## Environment

```bash
# We assume you are using a conda environment
# Please confirm that you have installed CUDA==1.16 or CUDA==1.17

# torchvision==0.14.0 & torch==1.13 only work with CUDA==1.16 or CUDA==1.17 and python==3.10
conda create -n biomedgps python==3.10

# If you have installed CUDA==1.16 or CUDA==1.17, you can use the following command to install torch==1.13
# dglke is compatible with dgl==0.9.0 and dgl==0.9.0 only works with torch==1.13
pip3 install torch==1.13 torchvision==0.14.0

# Install dglke
pip install git+https://github.com/yjcyxky/dgl-ke.git#subdirectory=python && pip install ogb dgl==0.9.0 wandb
```

## Sweep

The project is configured to run a sweep on the job queue and job. The sweep is configured in wandb_sweep_kge.yaml. The sweep will run a job on a set of hyperparameters. The job will run a training script, train.sh. If you want to know more about the sweep, please refer to [wandb sweep](https://docs.wandb.ai/guides/sweeps/quickstart).

### Step 1: Login to wandb

if you don't have an account, please register one at https://wandb.ai/. After you login at the website, you can find your API key at https://wandb.ai/authorize.

```bash
wandb login
```

### Step 2: Create a project

Create a project at https://wandb.ai/ and replace <project_name> with your project name

### Step 3: Register a sweep

Before you register a sweep, you need to change the arguments in wandb_sweep.yaml. You can find the arguments in train.sh. You can also add more arguments in wandb_sweep.yaml and train.sh. More details on the arguments can be found in the [Arguments](#Arguments) section.

```bash
# Write a sweep config file and a script to run, such as train.sh and wandb_sweep.yaml
# Run sweep
wandb sweep --project <project_name> wandb_sweep.yaml
```

### Step 4: Run sweep agent

```bash
# Run sweep agent
wandb agent <project_name> <sweep_id>

# NOTE: The sweep_id is printed when you run wandb sweep
# wandb.init() will be ignored when running a sweep.
```

## Arguments

Please see the arguments in wandb_sweep_kge.yaml and train.sh. The arguments are listed below. If you find any arguments are listed in wandb_sweep_kge.yaml/train.sh but not in the following list, it just means that the argument is supported by customized dgl-ke but is not listed in the following list.

- enable_embedding: Enable embedding. If it is set to False, the model will not use embedding. If you don't want to use embedding, please set it to False in the wandb_sweep.yaml file.

- wandb_entity: The entity name in wandb. If you want to use wandb to visualize the embeddings, please set it to the entity name in wandb.

- model_name: {TransE, TransE_l1, TransE_l2, TransR, RESCAL, DistMult, ComplEx, RotatE} The models provided by DGL-KE.

- data_path: DATA_PATH The path of the directory where DGL-KE loads knowledge graph data.

- dataset: DATA_SET The name of the knowledge graph stored under data_path. If it is one of the builtin knowledge grpahs such as FB15k, FB15k-237, wn18, wn18rr, and Freebase, DGL-KE will automatically download the knowledge graph and keep it under data_path.

- format: FORMAT The format of the dataset. For builtin knowledge graphs, the format is determined automatically. For users own knowledge graphs, it needs to be raw_udd_{htr} or udd_{htr}. raw_udd_ indicates that the user’s data use raw ID for entities and relations and udd_ indicates that the user’s data uses KGE ID. {htr} indicates the location of the head entity, tail entity and relation in a triplet. For example, htr means the head entity is the first element in the triplet, the tail entity is the second element and the relation is the last element.

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

--double_rel: Double relation dim for complex number.

- neg_adversarial_sampling: Indicate whether to use negative adversarial sampling.It will weight negative samples with higher scores more.

- adversarial_temperature: ADVERSARIAL_TEMPERATURE The temperature used for negative adversarial sampling.

- regularization_coef: REGULARIZATION_COEF The coefficient for regularization.

- regularization_norm: REGULARIZATION_NORM norm used in regularization.

- gpu: [GPU ...] A list of gpu ids, e.g. 0 1 2 4

- mix_cpu_gpu: Training a knowledge graph embedding model with both CPUs and GPUs.The embeddings are stored in CPU memory and the training is performed in GPUs.This is usually used for training large knowledge graph embeddings.

- valid: Evaluate the model on the validation set in the training.

- rel_part: Enable relation partitioning for multi-GPU training.

- async_update: Allow asynchronous update on node embedding for multi-GPU training. This overlaps CPU and GPU computation to speed up.

## Embeddings

If you want to know how to generate initial embeddings, please refer to the [embeddings](../embeddings/README.md) directory.

*-400: reduced from 1024-dim embeddings which was generated by the RoBERTa model

*-768: generated by the Biobert model

*-1024: generated by the RoBERTa model