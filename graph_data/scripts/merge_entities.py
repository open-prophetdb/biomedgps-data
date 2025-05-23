import os
import re
import logging
import click
import pandas as pd
from typing import List
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
    # Add the new entity type here
    "Phenotype",
    "Protein",
    "CellLine",
]

# NOTICE: The values in the entity_db_order_map must keep the same format as the name of the folder in the input directory
# These values will be used to locate the data files in the entity directory. More details can be found in the merge_entities function.
entity_db_order_map = {
    # The id prefix is MONDO or MESH or UMLS or DOID
    "Disease": [
        "Mondo",
        "MESH",
        "Hetionet",
        "Orphanet",
    ],
    # The id prefix is UBERON or MESH
    "Anatomy": [
        "Uberon",
        "MESH",
        "Hetionet",
    ],
    # The id prefix is ENTREZ
    "Gene": [
        "HGNC",
        "MGI",
        "Hetionet",
    ],
    # The id prefix is DrugBank or MESH
    "Compound": [
        "DrugBank",
        "MESH",
        "Hetionet",
    ],
    # The id prefix is REACT or WikiPathways or KEGG
    "Pathway": ["Reactome", "Hetionet", "KEGG", "WikiPathways"],
    "PharmacologicClass": [
        "NDF-RT",
        "Hetionet",
    ],
    "SideEffect": [
        "MedDRA",
        "Hetionet",
    ],
    "Symptom": [
        # The id prefix is SYMP
        "Symptom-Ontology",
        # The id prefix is UMLS or MESH
        "Hetionet",
    ],
    # The id prefix is GO
    "MolecularFunction": [
        "GO",
        "Hetionet",
    ],
    # The id prefix is GO
    "BiologicalProcess": [
        "GO",
        "Hetionet",
    ],
    # The id prefix is GO
    "CellularComponent": [
        "GO",
        "Hetionet",
    ],
    # The id prefix is HMDB
    "Metabolite": ["HMDB"],
    # Add the new entity type here
    # The id prefix is HP
    "Phenotype": ["HPO"],
    # The id prefix is Uniprot
    "Protein": ["Uniprot"],
    # The id prefix is CLO
    "CellLine": ["CLO"],
}


id_priority = {
    # When you want to do deep deduplication on a specific entity type, you need to add the id priority here. If not, the deep deduplication will not be performed on this entity type.
    # Don't add gene here, because the gene id is unique for each species
    "Disease": ["MONDO", "MESH", "UMLS", "DOID"],
    "Symptom": ["SYMP", "UMLS", "MESH"],
    "Phenotype": ["HP", "UMLS", "MESH", "SYMP"],
    "Compound": ["DrugBank", "MESH"],
}


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, item):
        if item not in self.parent:
            self.parent[item] = item
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1, item2):
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            self.parent[root2] = root1


def deep_deduplicate(entities_df, id_priority):
    """Deep deduplicate the entities with the same id or cross-references.

    Args:
        entities_df (pd.DataFrame): The entities dataframe to be deduplicated.
        id_priority (dict): The priority dictionary for id selection.

    Returns:
        pd.DataFrame: The deduplicated entities dataframe.
        list: The logs for the deduplication process.
    """
    entities = entities_df.copy()
    logs = []
    entities["xrefs"] = entities["xrefs"].fillna("")
    entities["xrefs_list"] = entities["xrefs"].str.split("|")

    def is_prefixed_id(id, prefixes):
        return any(id.startswith(prefix) for prefix in prefixes)

    # We might get multiple ids for the same entity, we need to choose the main id based on the priority order.
    def choose_id(ids, label):
        for prefix in id_priority.get(label, []):
            for id in ids:
                if id.startswith(prefix):
                    return id
        return list(ids)[0]

    # We might get multiple resources for the same entity, we need to choose the main resource based on the priority order.
    def choose_database(databases, label):
        for prefix in entity_db_order_map.get(label, []):
            for db in databases:
                db_lower = db.lower()
                # It's SymptomOntology in the entity file, but we use Symptom-Ontology in the entity_db_order_map, so we need to replace the hyphen with "".
                if (
                    db_lower.startswith(prefix.lower())
                    or db_lower.startswith(prefix.replace("-", "").lower())
                    or db_lower.startswith(prefix.replace("_", "").lower())
                ):
                    return db
        return list(databases)[0]

    merged_rows = []
    uf = UnionFind()

    for label, group in entities.groupby("label"):
        if label not in id_priority:
            merged_rows.extend(group.to_dict(orient="records"))
            continue

        id_to_index = {}
        for index, row in group.iterrows():
            id_to_index.setdefault(row["id"], []).append(index)
            for xref in row["xrefs_list"]:
                if xref and is_prefixed_id(xref, id_priority[str(label)]):
                    id_to_index.setdefault(xref, []).append(index)

            name_lower = row["name"].lower()
            id_to_index.setdefault(name_lower, []).append(index)

        msg = f"Processing {label} entities:"
        logs.append(msg)
        print(msg)

        logs.append(f"Id to Index: {id_to_index}")

        print("Try to merge the indices with the same id or xrefs")
        for key, indices in id_to_index.items():
            for i in range(len(indices) - 1):
                uf.union(indices[i], indices[i + 1])

        index_groups = {}
        for index in group.index:
            root = uf.find(index)
            if root not in index_groups:
                index_groups[root] = []
            index_groups[root].append(index)

        print("Dealing with the merged indices...")
        logs.append(f"Index Groups: {index_groups}")
        for key, indices in index_groups.items():
            related_rows = group.loc[indices]
            ids = related_rows["id"].tolist()
            names = related_rows["name"].tolist()
            id_names = list(zip(ids, names))

            all_ids = set(related_rows["id"].tolist())
            all_xrefs = set(related_rows["xrefs"].str.cat(sep="|").split("|"))
            merged_xrefs = all_ids.union(all_xrefs) - {""}
            main_id = choose_id(all_ids, label)

            if len(set(ids)) > 1:
                msg = f"These ids might point to the same entity with {label} label [Main ID - {main_id}]: {key} - {id_names}"
                logs.append(msg)
                print(msg)
            logs.append(f"\t{main_id} - {related_rows.to_dict(orient='records')}")

            merged_row = related_rows.iloc[0].copy()
            for col in related_rows.columns:
                if col not in ["id", "xrefs", "xrefs_list", "name"]:
                    values = related_rows[col].dropna().unique()
                    merged_row[col] = "|".join(sorted(set(values)))
            merged_row["xrefs"] = "|".join(sorted(merged_xrefs))
            merged_row["id"] = main_id
            merged_row["name"] = related_rows.loc[
                related_rows["id"] == main_id, "name"
            ].values[0]
            merged_rows.append(merged_row)

    merged_df = pd.DataFrame(merged_rows)
    merged_df = merged_df.drop(columns=["xrefs_list"]).fillna("")
    grouped_cols = ["id", "label"]
    first_cols = ["name", "description"]
    join_cols = [
        col for col in merged_df.columns if col not in first_cols + grouped_cols
    ]
    agg_dict = {col: "first" for col in first_cols}
    join_cols_dict: dict = {
        col: lambda x: "|".join(sorted(set("|".join(x).split("|"))))
        for col in join_cols
    }
    agg_dict.update(**join_cols_dict)

    result_df = merged_df.groupby(["id", "label"]).agg(agg_dict).reset_index()
    for col in join_cols + first_cols:
        result_df[col] = result_df[col].str.strip("|")

    # We don't want the resource column to have several values, such as Mondo|Orphanet, we want to keep only one value based on the priority order.
    # The resource column will be used in statistics of entities. We don't like to have several values in the resource column. And we don't care about all the resources, we only care about the main resource.
    result_df["resource"] = result_df.apply(
        lambda row: choose_database(row["resource"].split("|"), row["label"]), axis=1
    )
    return result_df, logs


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


def check_entities(entities: pd.DataFrame) -> List[str]:
    """Check whether the entities are valid.

    Args:
        entities (pd.DataFrame): The entities to be checked.

    Returns:
        List[str]: The errors found in the entities.
    """
    errors = []

    # TODO: Add the entity checking logic here, such as checking the id, name, label, resource, etc.
    return errors


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
            key=lambda x: str(entity_db_order_map[entity_type])
            .lower()
            .index(
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

        # Remove all unexpected empty characters, such as leading and trailing spaces
        merged_entities["description"] = merged_entities["description"].fillna("")
        merged_entities["description"] = merged_entities["description"].apply(
            lambda x: " ".join(x.strip().split())
        )

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
@click.option(
    "--deep-deduplication",
    "-d",
    help="Whether to perform deep deduplication",
    is_flag=True,
)
@click.option(
    "--remove-obsolete",
    "-r",
    help="Whether to remove obsolete entities",
    is_flag=True,
)
def to_single_file(input_dir, output_file, deep_deduplication, remove_obsolete):
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
    grouped_entity_files = dict(zip(entity_types, entity_files))

    # TODO: We will remove the filtered entities in the future, instead, we use the deep deduplication to remove the duplicated entities
    filtered_entity_files = list(
        filter(lambda x: x.endswith("filtered.tsv"), entity_files)
    )
    filtered_entity_types = list(
        map(lambda x: os.path.basename(x).split(".")[0], filtered_entity_files)
    )
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
    raw_merged_entities = merged_entities.drop_duplicates(
        subset=["id", "label"], keep="first"
    )
    merged_entities = raw_merged_entities.copy()
    obsolete_entities = None

    raw_output_file = output_file.replace(".tsv", "_full.tsv")
    log_output_file = output_file.replace(".tsv", ".log")
    obsolete_output_file = output_file.replace(".tsv", "_obsolete.tsv")

    if deep_deduplication:
        merged_entities, logs = deep_deduplicate(merged_entities, id_priority)

        with open(log_output_file, "w") as f:
            f.write("\n".join(logs))

    if remove_obsolete:
        obsolete_entities = merged_entities[
            merged_entities["name"].str.contains(
                "obsolete", na=False
            )  # na=False 防止 NaN 引发错误
            & (
                merged_entities["xrefs"].str.len().fillna(0)
                == 0 | (merged_entities["xrefs"] == merged_entities["id"])
            )
        ]
        logger.info("Number of obsolete entities: %s\n" % obsolete_entities.shape[0])
        merged_entities = merged_entities[
            ~merged_entities.index.isin(obsolete_entities.index)
        ]
        logger.info("Number of merged entities: %s\n" % merged_entities.shape[0])

    raw_merged_entities.to_csv(raw_output_file, sep="\t", index=False)
    merged_entities.to_csv(output_file, sep="\t", index=False)

    if obsolete_entities is not None:
        obsolete_entities.to_csv(obsolete_output_file, sep="\t", index=False)


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
