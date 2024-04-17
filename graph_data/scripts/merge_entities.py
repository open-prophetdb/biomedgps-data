import os
import re
import logging
import click
import pandas as pd
from ontology_matcher.ontology_formatter import BaseOntologyFileFormat

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("merge_entities.py")
logging.basicConfig(level=logging.INFO, format=fmt)

cli = click.Group()


def read_csv(filepath: str):
    logger.info("Reading %s" % filepath)
    df = pd.read_csv(filepath, sep="\t", quotechar='"', low_memory=False, dtype=str)
    expected_columns = BaseOntologyFileFormat.expected_columns()
    optional_columns = BaseOntologyFileFormat.optional_columns()

    # Check if the dataframe has all expected columns
    for column in expected_columns:
        if column not in df.columns:
            raise ValueError("The dataframe must have the column %s" % column)

    # Check if the dataframe has all optional columns, if not then add them
    for column in optional_columns:
        if column not in df.columns:
            df[column] = ""

    df = df[expected_columns + optional_columns]

    return df


entity_types = [
    "Disease",
    "Anatomy",
    "Gene",
    "Compound",
    "Pathway",
    "PharmacologicClass",
    "SideEffect",
    "Symptom",
    "MolecularFunction",
    "BiologicalProcess",
    "CellularComponent",
    "Metabolite",
]

# NOTICE: The values in the entity_db_order_map must keep the same format as the name of the folder in the input directory
entity_db_order_map = {
    "Disease": [
        "mondo",
        "mesh",
        "hetionet",
    ],
    "Anatomy": [
        "uberon",
        "mesh",
        "hetionet",
    ],
    "Gene": [
        "hgnc_mgi",
        "hetionet",
    ],
    "Compound": [
        "drugbank",
        "mesh",
        "hetionet",
    ],
    "Pathway": [
        "reactome",
        "hetionet",
        "kegg",
        "wikipathways"
    ],
    "PharmacologicClass": [
        "ndf-rt",
        "hetionet",
    ],
    "SideEffect": [
        "meddra",
        "hetionet",
    ],
    "Symptom": [
        "symptom-ontology",
        "hetionet",
    ],
    "MolecularFunction": [
        "go",
        "hetionet",
    ],
    "BiologicalProcess": [
        "go",
        "hetionet",
    ],
    "CellularComponent": [
        "go",
        "hetionet",
    ],
    "Metabolite": ["hmdb"],
}


def title_case_to_snake_case(title_str):
    snake_case_str = re.sub(r"(?<!^)(?=[A-Z])", "_", title_str).lower()
    return snake_case_str


def get_all_files_recursively(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Ignore the hidden files
            if not file.startswith("."):
                all_files.append(file_path)
    return all_files


@cli.command(help="Merge the entities from all resources")
@click.option(
    "--input-dir",
    "-i",
    help="Input directory which contains entities from resources, such as ctd, hetionet etc. If you need to add a new resource, you need to add a new folder in data and keep its filename as the following format. `${resource}/${resource}_${entity_type}`, all characters must be lower.",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--output-dir",
    "-o",
    help="Output file path, such as formatted_data",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def from_databases(input_dir, output_dir):
    # Get all files in the input directory recursively
    resources = get_all_files_recursively(input_dir)

    logger.info("Resources: %s\n" % resources)

    # Filter the matched resources for the specified entity type
    def filter_resources(entity_type):
        return list(
            filter(
                lambda x: x.endswith(title_case_to_snake_case(entity_type) + ".tsv"),
                resources,
            )
        )

    # Merge the entities from all resources for the specified entity type
    def merge_entities(entity_type):
        # Filter the matched resources for the specified entity type
        matched_resources = filter_resources(entity_type)

        logger.info("Merging %s entities from %s\n" % (entity_type, matched_resources))

        # Order the matched resources by the entity_db_order_map
        matched_resources = sorted(
            matched_resources,
            key=lambda x: entity_db_order_map[entity_type].index(
                # NOTICE: The name must keep the same format as the value in the entity_db_order_map
                os.path.basename(os.path.dirname(x))
            ),
        )

        logger.info(
            "The order of matched resources: %s\n" % entity_db_order_map[entity_type]
        )
        logger.info("Ordered matched resources: %s\n" % matched_resources)
        # Read the entities from all matched resources
        entities = list(
            map(
                lambda x: read_csv(x),
                matched_resources,
            )
        )
        # Merge the entities from all matched resources
        merged_entities = pd.concat(entities, ignore_index=True, axis=0)

        # Drop the duplicated entities
        merged_entities = merged_entities.drop_duplicates(subset=["id"], keep="first")

        # Return the merged entities
        return merged_entities

    for entity_type in entity_types:
        # Merge the entities from all resources for the specified entity type
        merged_entities = merge_entities(entity_type)

        # Remove the rows that have empty id, name, label
        merged_entities = merged_entities[
            merged_entities["id"].notnull()
            & merged_entities["name"].notnull()
            & merged_entities["label"].notnull()
        ]

        # Write the merged entities to a tsv file
        merged_entities.to_csv(
            os.path.join(output_dir, "%s.tsv" % title_case_to_snake_case(entity_type)),
            sep="\t",
            index=False,
        )


@cli.command(help="Merge the entity files to a single file")
@click.option(
    "--input-dir",
    "-i",
    help="Input directory which contains a set of entity files",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--output-file",
    "-o",
    help="Output file path, such as entities.tsv",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def to_single_file(input_dir, output_file):
    # Get all files in the input directory recursively
    resources = get_all_files_recursively(input_dir)

    # Filter the matched resources for the specified entity type
    entity_files = list(
        filter(
            lambda x: x.endswith(".tsv"),
            resources,
        )
    )

    # Group the entity files by entity type
    entity_types = list(map(lambda x: os.path.basename(x).split(".")[0], entity_files))
    filtered_entity_files = list(
        filter(lambda x: x.endswith("filtered.tsv"), entity_files)
    )
    filtered_entity_types = list(
        map(lambda x: os.path.basename(x).split(".")[0], filtered_entity_files)
    )
    grouped_entity_files = dict(zip(entity_types, entity_files))
    grouped_entity_files.update(dict(zip(filtered_entity_types, filtered_entity_files)))

    logger.info(
        "Entity files: %s\n\nEntity types:%s\n\nGrouped entity files: %s\n"
        % (entity_files, entity_types, grouped_entity_files)
    )

    entity_files = list(grouped_entity_files.values())
    # Read the entities from all files
    entities = list(
        map(
            lambda x: read_csv(x),
            entity_files,
        )
    )
    # Merge the entities from all files by row
    merged_entities = pd.concat(entities, ignore_index=True, axis=0)

    # Drop the duplicated entities
    merged_entities = merged_entities.drop_duplicates(
        subset=["id", "label"], keep="first"
    )

    # Write the merged entities to a tsv file
    merged_entities.to_csv(output_file, sep="\t", index=False)


@cli.command(help="Merge multiple entity files to a single file")
@click.option(
    "--input-file",
    "-i",
    help="Input file which contains a set of entity files",
    multiple=True,
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-file",
    "-o",
    help="Output file path, such as entities.tsv",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def merge_multiple_files(input_file, output_file):
    # Read the entities from all files
    entities = list(map(lambda x: read_csv(x), input_file))

    # Merge the entities from all files by row
    merged_entities = pd.concat(entities, ignore_index=True, axis=0)

    # Drop the duplicated entities
    merged_entities = merged_entities.drop_duplicates(
        subset=["id", "label"], keep="first"
    )

    # Write the merged entities to a tsv file
    merged_entities.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()
