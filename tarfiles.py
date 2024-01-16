#!/usr/bin/env python

import os
import tarfile
import click

# Wrap all essential data files into a tarball
files = [
    "./graph_data/entities.tsv",
    "./graph_data/knowledge_graph.tsv",
    "./graph_data/knowledge_graph_annotated.tsv",
    "./graph_data/log.txt",
    "./graph_data/relations",
    "./graph_data/formatted_relations",
    "./graph_data/formatted_entities",
    "./graph_data/extracted_entities",
    "./graph_data/entities",
    # Embeddings
    "./embeddings/biobert-base-cased-v1.1/entities_embeddings.tsv",
    "./embeddings/biobert-base-cased-v1.1/relation_types_embeddings.tsv",
    "./embeddings/RoBERTa-large-PM-M3-Voc/entities_embeddings.tsv",
    "./embeddings/RoBERTa-large-PM-M3-Voc/relation_types_embeddings.tsv",
    # Datasets
    "./datasets/custom",
    "./datasets/drkg",
    "./datasets/drkg+hsdn",
    "./datasets/drkg+hsdn+custom+malacards",
    "./datasets/raw_drkg",
    "./datasets/rawdata",
    # DB
    "./ontology_matcher_cache.sqlite",
]


# Check if all files exist
def check_files(files):
    for file in files:
        if not os.path.exists(file):
            print(f"File {file} does not exist!")
            return False
    return True


# Create a tarball
def create_tarball(files, destfile):
    # Create a new tarball in write and gzip mode
    with tarfile.open(destfile, "w:gz") as tar:
        for file in files:
            print(f"Adding {file} to tarball...")
            # Add each file/directory to the tarball
            tar.add(file, arcname=os.path.basename(file))


@click.command(help="Wrap all essential data files into a tarball")
@click.argument("destfile", type=click.Path(exists=False))
def upload(destfile):
    print("Creating tarball...")
    print("Checking if all files exist...")
    if not check_files(files):
        return
    print("All files exist!")
    create_tarball(files, destfile)


if __name__ == "__main__":
    upload()