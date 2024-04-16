# Usage: python correct_graph_data.py --help
# Description: This tool is used to check or correct the relation, entity, relation type embedding, or entity embedding file.
#
# Orders:
# 1. Check id of the relation, entity, relation type embedding, or entity embedding file.
#    python correct_graph_data.py check_id --help
#
# 2. Correct the relation file.
#    python correct_graph_data.py correct_relation --help
#
# 3. Check if all entities in the relation / entity embedding file are in the entity file.
#    python correct_graph_data.py check_entity --help
#
# 4. Check if all relation types in the relation type embedding file are in the relation file.
#    python correct_graph_data.py check_relation_type --help
#

import re
import click
import pandas as pd


def check_node_id(id: str):
    # Gene::ENTREZ:6747 --> <ENTITY_TYPE>::<DB_NAME>:<ID>
    if re.match(r"[a-zA-Z]+::[a-zA-Z\-]+:[a-zA-Z0-9\-_]+", id):
        return True
    return False


def check_entity_id(id: str):
    # SYMP:0000149 --> <DB_NAME>:<ID>
    if re.match(r"[a-zA-Z\-]+:[a-zA-Z0-9\-_]+", id):
        return True
    return False


def _check_relation_type(id: str):
    # STRING::BINDING::Gene:Gene --> <DB_NAME>::<RELATION_TYPE>::<ENTITY_TYPE>:<ENTITY_TYPE>
    if re.match(r"[a-zA-Z]+::[a-zA-Z0-9 \-_\+\>]+::[a-zA-Z]+:[a-zA-Z]+", id):
        return True
    return False


def show_msg(msg: str):
    print(msg)


cli = click.Group()


@cli.command(help="This tool is used to check or correct the relation or entity file.")
@click.option(
    "--input-file", "-i", help="The input file of the knowledge graph.", required=True
)
@click.option(
    "--which-type",
    "-w",
    help="The type of the relation to be corrected.",
    type=click.Choice(
        ["relation", "entity", "relation_type_embedding", "entity_embedding"]
    ),
    required=True,
)
def check_id(input_file, which_type):
    """Check the input file of the knowledge graph.

    Args:
        input_file (str): The input file of the knowledge graph.
        which_type (str): The type of the relation to be corrected. It can be "relation", "entity", "relation_type_embedding", or "entity_embedding".
    """
    print(f"Checking the input file {input_file}...")
    df = pd.read_csv(input_file, sep="\t", dtype=str)

    issues = []
    if which_type == "relation":
        for col in [
            "source_id",
            "target_id",
            "target_type",
            "source_id",
            "relation_type",
        ]:
            if col not in df.columns:
                show_msg(f"{col} is missing.")

        for idx, row in df.iterrows():
            if not check_entity_id(row["source_id"]):
                show_msg(f"{row['source_id']} is not a valid entity id at row {idx}.")
            if not check_entity_id(row["target_id"]):
                show_msg(f"{row['target_id']} is not a valid entity id at row {idx}.")
            if not _check_relation_type(row["relation_type"]):
                show_msg(
                    f"{row['relation_type']} is not a valid relation type at row {idx}. {row['source_type']} {row['target_type']}"
                )

            if _check_relation_type(row["relation_type"]):
                relation_type = row["relation_type"]

                if relation_type is not None:
                    source_type_in_relation, target_type_in_relation = (
                        relation_type.split("::")[2].split(":")
                    )
                else:
                    source_type_in_relation, target_type_in_relation = "", ""

                if (
                    source_type_in_relation != row["source_type"]
                    or target_type_in_relation != row["target_type"]
                ) and source_type_in_relation != target_type_in_relation:
                    show_msg(
                        f"The source and target type in the relation type {relation_type} are not consistent with the source and target type in the relation at row {idx}."
                    )

    if which_type == "entity":
        for col in ["id", "label", "name"]:
            if col not in df.columns:
                show_msg(f"{col} is missing.")

        for idx, row in df.iterrows():
            if not check_entity_id(row["id"]):
                show_msg(f"{row['id']} is not a valid entity id at row {idx}.")

    if which_type == "relation_type_embedding":
        for col in ["id", "embedding"]:
            if col not in df.columns:
                show_msg(f"{col} is missing.")

        for idx, row in df.iterrows():
            if not _check_relation_type(row["id"]):
                show_msg(f"{row['id']} is not a valid relation type at row {idx}.")

    if which_type == "entity_embedding":
        for col in [
            "embedding_id",
            "entity_id",
            "entity_type",
            "embedding",
            "entity_name",
        ]:
            if col not in df.columns:
                show_msg(f"{col} is missing.")

        for idx, row in df.iterrows():
            if not check_entity_id(row["entity_id"]):
                show_msg(f"{row['id']} is not a valid entity id at row {idx}.")

            if not check_node_id(row["embedding_id"]):
                show_msg(f"{row['embedding_id']} is not a valid node id at row {idx}.")

    if issues:
        for issue in issues:
            print(issue)

            print(
                f"Found {len(issues)} issues in the input file {input_file}, please check it manually or remove --dry-run to correct it directly."
            )


@cli.command(help="Correct the relation file.")
@click.option(
    "--uncorrected-file", "-r", help="The uncorrected relation file.", required=True
)
@click.option("--relation-type-map", "-m", help="The relation type map file.")
@click.option(
    "--which-type",
    "-w",
    help="The type of the relation to be corrected.",
    type=click.Choice(["relation", "relation_type_embedding"]),
    required=True,
)
def correct_relation(uncorrected_file, relation_type_map, which_type):
    """Correct the relation file or the relation type embedding file.

    Args:
        uncorrected_file (str): The uncorrected relation file.
        relation_type_map (str): The relation type map file which contains the relation type and the corrected relation type.
        which_type (str): The type of the relation to be corrected. It can be "relation" or "relation_type_embedding".
    """
    df = pd.read_csv(uncorrected_file, sep="\t", dtype=str)
    # Keep the source and target type in the relation consistent with the relation type

    if which_type == "relation_type_embedding":
        for col in [
            "id",
            "embedding",
        ]:
            if col not in df.columns:
                raise Exception(
                    f"{col} is missing in the relation_type_embedding file."
                )

        if relation_type_map is not None:
            relation_type_df = pd.read_csv(relation_type_map, sep="\t", dtype=str)

            for col in ["relation_type", "corrected_relation_type"]:
                if col not in relation_type_df.columns:
                    raise Exception(f"{col} is missing in the relation type map file.")

            # Replace the relation type with the corrected relation type
            print("Replacing the relation type with the corrected relation type...")
            df.loc[
                df["id"].isin(relation_type_df["relation_type"]),
                "id",
            ] = df.loc[
                df["id"].isin(relation_type_df["relation_type"]),
                "id",
            ].map(
                relation_type_df.set_index("relation_type")["corrected_relation_type"]
            )

    if which_type == "relation":
        for col in [
            "source_id",
            "target_id",
            "target_type",
            "source_id",
            "relation_type",
        ]:
            if col not in df.columns:
                raise Exception(f"{col} is missing in the relation file.")

        if relation_type_map is not None:
            relation_type_df = pd.read_csv(relation_type_map, sep="\t", dtype=str)

            for col in ["relation_type", "corrected_relation_type"]:
                if col not in relation_type_df.columns:
                    raise Exception(f"{col} is missing in the relation type map file.")

            # Replace the relation type with the corrected relation type
            print("Replacing the relation type with the corrected relation type...")
            df.loc[
                df["relation_type"].isin(relation_type_df["relation_type"]),
                "relation_type",
            ] = df.loc[
                df["relation_type"].isin(relation_type_df["relation_type"]),
                "relation_type",
            ].map(
                relation_type_df.set_index("relation_type")["corrected_relation_type"]
            )

        print(
            "The source and target type in the relation type are not consistent with the source and target type in the relation, correcting it..."
        )
        for idx, row in df.iterrows():
            relation_type = row["relation_type"]
            if type(relation_type) is not str:
                raise Exception(
                    f"relation_type is not a string: {relation_type} at row {idx}."
                )

            try:
                source_type_in_relation, target_type_in_relation = relation_type.split(
                    "::"
                )[2].split(":")
            except Exception as e:
                raise Exception(
                    f"relation_type is not in the correct format: {relation_type} at row {idx}. {row['source_type']} {row['target_type']}"
                )

            if (
                source_type_in_relation != row["source_type"]
                or target_type_in_relation != row["target_type"]
            ):
                df.at[idx, "source_type"] = source_type_in_relation
                df.at[idx, "target_type"] = target_type_in_relation
                source_id = row["source_id"]
                target_id = row["target_id"]
                df.at[idx, "source_id"] = target_id
                df.at[idx, "target_id"] = source_id

    relation_file = uncorrected_file.replace(".tsv", "_corrected.tsv")
    df.to_csv(relation_file, sep="\t", index=False)


@cli.command(
    help="Check if all entities in the relation / entity embedding file are in the entity file."
)
@click.option(
    "--unchecked-file",
    "-r",
    help="A file is to be checked. It can be a relation file or an entity embedding file.",
    required=True,
)
@click.option("--entity-file", "-e", help="The entity file.", required=True)
def check_entity(unchecked_file, entity_file):
    """Check if all entities in the relation / entity embedding file are in the entity file.

    Args:
        unchecked_file (str): A file is to be checked. It can be a relation file or an entity embedding file.
        entity_file (str): The entity file.
    """
    unchecked = pd.read_csv(unchecked_file, sep="\t", dtype=str)
    entity_df = pd.read_csv(entity_file, sep="\t", dtype=str)
    node_ids = [
        f"{entity_type}::{entity_id}"
        for entity_type, entity_id in zip(entity_df["label"], entity_df["id"])
    ]

    issues = []
    # It's a relation file
    if "source_id" in unchecked.columns and "target_id" in unchecked.columns:
        source_node_ids = list(
            set(
                [
                    f"{entity_type}::{entity_id}"
                    for entity_type, entity_id in zip(
                        unchecked["source_type"], unchecked["source_id"]
                    )
                ]
            )
        )
        for node_id in source_node_ids:
            if node_id not in node_ids:
                show_msg(f"Source {node_id} is not in the entity file.")

        target_node_ids = list(
            set(
                [
                    f"{entity_type}::{entity_id}"
                    for entity_type, entity_id in zip(
                        unchecked["target_type"], unchecked["target_id"]
                    )
                ]
            )
        )
        for node_id in target_node_ids:
            if node_id not in node_ids:
                show_msg(f"Target {node_id} is not in the entity file.")

    # It's a entity embedding file
    if "entity_id" in unchecked.columns and "entity_type" in unchecked.columns:
        for entity_type, entity_id in zip(
            unchecked["entity_type"], unchecked["entity_id"]
        ):
            if f"{entity_type}::{entity_id}" not in node_ids:
                show_msg(f"{entity_type}::{entity_id} is not in the entity file.")

    if issues:
        for issue in issues:
            print(issue)


@cli.command(
    help="Check if all relation types in the relation file are in the relation type embedding file."
)
@click.option("--relation-file", "-r", help="The relation file.", required=True)
@click.option(
    "--relation-type-embedding-file",
    "-e",
    help="The relation type embedding file.",
    required=True,
)
def check_relation_type(relation_file, relation_type_embedding_file):
    """Check if all relation types in the relation type embedding file are in the relation file.

    Args:
        relation_file (str): The relation file.
        relation_type_embedding_file (str): The relation type embedding file.
    """
    relation_df = pd.read_csv(relation_file, sep="\t", dtype=str)
    relation_type_embedding_df = pd.read_csv(
        relation_type_embedding_file, sep="\t", dtype=str
    )
    relation_types = relation_type_embedding_df["id"].unique()

    issues = []
    for relation_type in relation_df["relation_type"].unique():
        if relation_type not in relation_types:
            show_msg(f"{relation_type} is not in the relation type embedding file.")

    if issues:
        for issue in issues:
            print(issue)


if __name__ == "__main__":
    cli()
