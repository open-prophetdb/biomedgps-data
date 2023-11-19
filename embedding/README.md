## Entities

### Generate embeddings for entities

```bash
mkdir -p embedding/<MODEL_NAME>

# If your expected model does not support transformers library directly, you can download the model's weights and refer to it by its path.
# We assume you have downloaded entities.tsv file or generated it by following the instructions in the README.md file in the root directory.
python embedding/scripts/gen_embeddings.py entities -e graph_data/entities.tsv -m <MODEL_NAME or MODEL_PATH> -o embedding/<MODEL_NAME>/entities_embeddings.tsv
```

## Relation Types
### Generate descriptions for each reltion type

More details on relation types, please visit relation_types.xlsx file.

### Generate embeddings for relation types

```bash
mkdir -p embedding/<MODEL_NAME>

python embedding/scripts/gen_embeddings.py relation-types -r embedding/relation_types.tsv -m <MODEL_NAME or MODEL_PATH> -o embedding/<MODEL_NAME>/realtion_types_embeddings.tsv
```

## Visualize embeddings

More details on visualization, please visit visualize.ipynb file in each model folder.