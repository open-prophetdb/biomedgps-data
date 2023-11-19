from random import choice
import click
import torch
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from typing import Tuple
from transformers import (
    AutoConfig,
    AutoModel,
    AutoTokenizer,
    PreTrainedTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerFast,
)


def read_entities(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")

    # Check the file whether it has the required columns
    required_columns = [
        "id",
        "name",
        "label",
        "description",
        "resource",
        "taxid",
        "synonyms",
        "pmids",
        "xrefs",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Column {column} is missing from the file")

    # Select only the columns we need
    df = df[required_columns]

    # Check if the description column is empty, if yes, fill it with the related name
    df["description"] = df["description"].fillna(df["name"])

    return df


def read_relation_types(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")

    # Select only the columns we need
    df = df[["relation_type", "description"]]
    return df


def load_model(
    model_name: str,
) -> Tuple[PreTrainedTokenizer | PreTrainedTokenizerFast, PreTrainedModel]:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    return tokenizer, model


def get_max_len(model_name: str) -> int:
    # Load the configuration of the model
    config = AutoConfig.from_pretrained(model_name)

    # Get the maximum sequence length
    max_length = config.max_position_embeddings
    return max_length


def generate_embedding(
    tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
    model: PreTrainedModel,
    text: str,
    max_len: int,
) -> np.ndarray:
    # Tokenize and encode the sentence
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    num_tokens = len(inputs.tokens())
    print("Generating embedding for: %s, %s, %s" % (text, max_len, num_tokens))

    # Make sure that the input ids are not longer than the maximum length
    if num_tokens > max_len:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=max_len,
        )

    # Pass the input to the model
    with torch.no_grad():
        outputs = model(**inputs)

    # The embeddings are usually in the 'last_hidden_state' key of the model outputs
    embeddings = outputs.last_hidden_state

    # Calculate the mean of token embeddings along the token dimension (dimension 1)
    sentence_embedding = torch.mean(embeddings, dim=1)

    return sentence_embedding[0].numpy()


cli = click.Group()


@cli.command(help="Generate embeddings for entities")
@click.option(
    "--entity-file", "-e", type=str, help="Path to entities file", required=True
)
@click.option(
    "--model-name",
    "-m",
    help="Model name/path",
    required=True,
)
@click.option("--output", "-o", type=str, help="Output file", required=True)
def entities(entity_file: str, model_name: str, output: str) -> None:
    tokenizer, model = load_model(model_name)
    entities = read_entities(entity_file)

    # max_len = get_max_len(model_name)
    max_len = 512

    embeddings = [
        generate_embedding(tokenizer, model, text, max_len)
        for text in entities["description"]
    ]

    entities["embedding"] = [
        "|".join([str(value) for value in embedding]) for embedding in embeddings
    ]
    entities["embedding_id"] = [i + 1 for i in range(len(embeddings))]

    # rename columns
    entities = entities.rename(
        columns={"id": "entity_id", "name": "entity_name", "label": "entity_type"}
    )

    # Select only the columns we need
    entities = entities[
        ["embedding_id", "entity_id", "entity_name", "entity_type", "embedding"]
    ]

    # save to file
    entities.to_csv(output, sep="\t", index=False)


@cli.command(help="Generate embeddings for relation types")
@click.option(
    "--relation-type-file",
    "-r",
    type=str,
    help="Path to relation types file",
    required=True,
)
@click.option(
    "--model-name",
    "-m",
    help="Model name/path",
    required=True
)
@click.option("--output", "-o", type=str, help="Output file", required=True)
def relation_types(relation_type_file: str, model_name: str, output: str) -> None:
    tokenizer, model = load_model(model_name)
    relation_types = read_relation_types(relation_type_file)

    max_len = 512

    embeddings = [
        generate_embedding(tokenizer, model, text, max_len)
        for text in relation_types["description"]
    ]

    relation_types["embedding"] = [
        "|".join([str(value) for value in embedding]) for embedding in embeddings
    ]
    relation_types["embedding_id"] = [i + 1 for i in range(len(embeddings))]

    # Select only the columns we need
    relation_types = relation_types[["embedding_id", "relation_type", "embedding"]]

    # save to file
    relation_types.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    cli()
