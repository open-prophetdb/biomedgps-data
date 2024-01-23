import os
import re
import click
import logging
import pandas as pd

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("merge_relations.py")
logging.basicConfig(level=logging.INFO, format=fmt)


@click.command(help="Annotate relations from a entity file")
@click.option(
    "--entity-file",
    "-e",
    help="Entity file path, such as entities.tsv",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--relation-file",
    "-r",
    help="Relation file path, such as relations.tsv",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-dir",
    "-o",
    help="Output directory path, such as output",
    required=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
)
def cli(entity_file, relation_file, output_dir):
    entities = pd.read_csv(entity_file, sep="\t", low_memory=False)
    relations_df = pd.read_csv(relation_file, sep="\t", low_memory=False)

    # Annotate relations_df with the entities dataframe
    entities = entities[["id", "label", "name", "description"]]
    relations_df = relations_df.merge(
        entities, left_on=["source_id", "source_type"], right_on=["id", "label"]
    )
    relations_df = relations_df.rename(
        columns={"name": "source_name", "description": "source_description"}
    )
    relations_df = relations_df.drop(columns=["id", "label"])
    relations_df = relations_df.merge(
        entities, left_on=["target_id", "target_type"], right_on=["id", "label"]
    )
    relations_df = relations_df.rename(
        columns={"name": "target_name", "description": "target_description"}
    )
    relations_df = relations_df.drop(columns=["id", "label"])
    knowledge_graph = relations_df[
        [
            "relation_type",
            "resource",
            "pmids",
            "key_sentence",
            "source_id",
            "source_type",
            "target_id",
            "target_type",
            "source_name",
            "target_name",
        ]
    ]
    output_file = os.path.join(output_dir, "knowledge_graph.tsv")
    knowledge_graph.to_csv(output_file, sep="\t", index=False)

    output_file = os.path.join(output_dir, "knowledge_graph_annotated.tsv")
    knowledge_graph_annotated = relations_df[
        [
            "relation_type",
            "resource",
            "pmids",
            "key_sentence",
            "source_id",
            "source_type",
            "target_id",
            "target_type",
            "source_name",
            "source_description",
            "target_name",
            "target_description",
        ]
    ]
    knowledge_graph_annotated.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()
