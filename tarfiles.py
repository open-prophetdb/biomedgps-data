#!/usr/bin/env python

import os
import tarfile
import click

cli = click.Group()

# Wrap all essential data files into a tarball
graph_data_files = [
    "graph_data/entities.tsv",
    "graph_data/relations.tsv",
    "graph_data/knowledge_graph.tsv",
    "graph_data/knowledge_graph_annotated.tsv",
    "graph_data/relations",
    "graph_data/formatted_relations",
    "graph_data/formatted_entities",
    "graph_data/extracted_entities",
    "graph_data/entities",
    "graph_data/custom_relations",
    # DB
    "ontology_matcher_cache.sqlite",
]

initial_embedding_files = [
    "embeddings",
]


def list_files(path):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


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


# Generate md5sum for a file
def compute_md5sum(filepath):
    command = f"md5sum {filepath}"
    return os.popen(command).read().split(" ")[0]


def list_files_md5sum(file_lst):
    md5sums = []
    for file in file_lst:
        files = list_files(file) if os.path.isdir(file) else [file]
        for filepath in files:
            print(f"Computing md5sum for {filepath}...")
            md5sums.append({"file": filepath, "md5sum": compute_md5sum(filepath)})
    return md5sums


def relative_path(path, dest_dir):
    return os.path.relpath(path, dest_dir)


@cli.command(help="Wrap all essential graph data files into a tarball")
@click.argument("destfile", type=click.Path(exists=False))
def graph_data(destfile):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    md5file = os.path.join(current_dir, "graph_data", "md5sum.txt")
    graph_data_filepaths = [
        os.path.join(current_dir, file) for file in graph_data_files
    ]

    print("Creating tarball...")
    print("Checking if all files exist...")
    if not check_files(graph_data_filepaths):
        return
    print("All files exist!")

    with open(md5file, "w") as f:
        for item in list_files_md5sum(graph_data_filepaths):
            filename = relative_path(item["file"], current_dir)
            f.write(f"{item['md5sum']} {filename}\n")

    graph_data_filepaths.append(md5file)
    create_tarball(graph_data_filepaths, destfile)

    # Remove md5sum.txt
    os.remove(md5file)


@cli.command(help="Wrap all initial embedding files into a tarball")
@click.argument("destfile", type=click.Path(exists=False))
def initial_embeddings(destfile):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    md5file = os.path.join(current_dir, "embeddings", "md5sum.txt")
    initial_embedding_filepaths = [
        os.path.join(current_dir, file) for file in initial_embedding_files
    ]

    print("Creating tarball...")
    print("Checking if all files exist...")
    if not check_files(initial_embedding_filepaths):
        return
    print("All files exist!")

    with open(md5file, "w") as f:
        for item in list_files_md5sum(initial_embedding_filepaths):
            filename = relative_path(item["file"], current_dir)
            f.write(f"{item['md5sum']} {filename}\n")

    initial_embedding_filepaths.append(md5file)
    create_tarball(initial_embedding_filepaths, destfile)

    # Remove md5sum.txt
    os.remove(md5file)


if __name__ == "__main__":
    cli()
