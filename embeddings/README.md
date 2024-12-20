## Introduction

You may want to use initial embeddings from a pretrained large language model to improve the performance of the model. 

The idea is that the pretrained large language model has learned the semantic information of the entities and relations from a large corpus. It knows the semantic information of the entities and relations. And in a knowledge graph, many entities might not have enough connections with other entities, we may get a not good embedding for these entities. If we use the initial embeddings instead of the random embeddings, we may make the model learn the semantic information of these entities and relations more easily.

In current version, we support two large language models: BioBert and RoBERTa. Actually, We use the [transformers](https://huggingface.co/docs/transformers/index) library to generate the embeddings. So if you want to use other large language model which is supported by the transformers library, we also support it. You can download the model's weights and refer to it by its path or just use the model name directly.

*-400: reduced from 1024-dim embeddings which was generated by the RoBERTa model

*-768: generated by the Biobert model

*-1024: generated by the RoBERTa model

## LLM Models

### BioBert (biobert-base-cased-v1.1)

Embeddings from BioBert model have 768 dimensions. You don't need to download the model, just use the model name directly. Because the model is supported by transformers library directly. More details on this model, please visit [BioBert](https://huggingface.co/dmis-lab/biobert-base-cased-v1.1) or [BioBert](https://github.com/dmis-lab/biobert-pytorch/blob/master/README.md) repository.

### RoBERTa (RoBERTa-large-PM-M3-Voc)

Embeddings from RoBERTa model have 1024 dimensions. You can download the model from [here](https://dl.fbaipublicfiles.com/biolm/RoBERTa-large-PM-M3-Voc-hf.tar.gz). More details on this model, please visit [BioLM](https://github.com/facebookresearch/bio-lm/blob/main/README.md) repository.

## Generate Embeddings for Entities

```bash
mkdir -p embedding/<MODEL_NAME>

# If your expected model does not support transformers library directly, you can download the model's weights and refer to it by its path.
# We assume you have downloaded entities.tsv file or generated it by following the instructions in the README.md file in the root directory.
python embedding/scripts/gen_embeddings.py entities -e graph_data/entities.tsv -m <MODEL_NAME or MODEL_PATH> -o embedding/<MODEL_NAME>/entities_embeddings.tsv

# Example: generate embeddings for entities using BioBert model
mkdir -p embedding/biobert-base-cased-v1.1
python embedding/scripts/gen_embeddings.py entities -e graph_data/entities.tsv -m dmis-lab/biobert-base-cased-v1.1 -o embedding/biobert-base-cased-v1.1/entities_embeddings.tsv

# Example: generate embeddings for entities using RoBERTa model
mkdir -p embedding/RoBERTa-large-PM-M3-Voc
wget https://dl.fbaipublicfiles.com/biolm/RoBERTa-large-PM-M3-Voc-hf.tar.gz
tar -xvf RoBERTa-large-PM-M3-Voc-hf.tar.gz -C embedding/RoBERTa-large-PM-M3-Voc
python embedding/scripts/gen_embeddings.py entities -e graph_data/entities.tsv -m ./RoBERTa-large-PM-M3-Voc -o embedding/RoBERTa-large-PM-M3-Voc/entities_embeddings.tsv
```

## Generate Embeddings for All Relation Types
### Descriptions for each relation type

More details on relation types, please visit [relation_types.tsv](./graph_data/relation_types.tsv) file.

### Generate Embeddings

```bash
mkdir -p embedding/<MODEL_NAME>

python embedding/scripts/gen_embeddings.py relation-types -r embedding/relation_types.tsv -m <MODEL_NAME or MODEL_PATH> -o embedding/<MODEL_NAME>/realtion_types_embeddings.tsv

# Example: generate embeddings for relation types using BioBert model
mkdir -p embedding/biobert-base-cased-v1.1
python embedding/scripts/gen_embeddings.py relation-types -r embedding/relation_types.tsv -m dmis-lab/biobert-base-cased-v1.1 -o embedding/biobert-base-cased-v1.1/realtion_types_embeddings.tsv

# Example: generate embeddings for relation types using RoBERTa model
mkdir -p embedding/RoBERTa-large-PM-M3-Voc
wget https://dl.fbaipublicfiles.com/biolm/RoBERTa-large-PM-M3-Voc-hf.tar.gz
tar -xvf RoBERTa-large-PM-M3-Voc-hf.tar.gz -C embedding/RoBERTa-large-PM-M3-Voc
python embedding/scripts/gen_embeddings.py relation-types -r embedding/relation_types.tsv -m ./RoBERTa-large-PM-M3-Voc -o embedding/RoBERTa-large-PM-M3-Voc/realtion_types_embeddings.tsv
```

## Visualize Embeddings

More details on visualization, please visit visualize.ipynb file in each model folder.
