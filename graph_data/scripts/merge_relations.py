import os
import re
import click
import logging
import pandas as pd

# #### Merge all formatted relations into one file

# ```bash
# # Merge formatted relation files into one file
# python graph_data/scripts/merge_relations.py -i graph_data/formatted_relations -o graph_data/relations.tsv
# ```

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("merge_relations.py")
logging.basicConfig(level=logging.INFO, format=fmt)


def get_all_files_recursively(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Ignore the hidden files
            if not file.startswith("."):
                all_files.append(file_path)
    return all_files


@click.command(help="Merge the relation files to a single file")
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
    help="Output file path, such as relations.tsv",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def cli(input_dir, output_file):
    # Get all files in the input directory recursively
    resources = get_all_files_recursively(input_dir)

    logger.info("Resources: %s\n" % resources)

    # Filter the matched resources
    files = sorted(
        list(
            filter(
                lambda x: x.endswith(".tsv")
                and os.path.basename(x).startswith("formatted_"),
                resources,
            )
        )
    )

    logger.info("Merging relations from %s\n" % files)

    def read_csv(filepath: str):
        logger.info("Reading %s" % filepath)
        df = pd.read_csv(
            filepath, sep="\t", quotechar='"', low_memory=False, on_bad_lines="warn"
        )
        # Filter invalid rows and save them to a file
        # Such as having different number of columns
        # Get the number of columns in the DataFrame
        num_columns = len(df.columns)

        # Filter rows with a different number of columns using a mask
        mask = df.apply(lambda row: len(row) == num_columns, axis=1)
        invalid = df[~mask]
        if len(invalid) > 0:
            invalid.to_csv(
                os.path.join(
                    os.path.dirname(filepath),
                    "invalid_" + os.path.basename(filepath),
                ),
                sep="\t",
                index=False,
            )

        # Create a new DataFrame with only valid rows
        valid_rows_df = df[mask]
        return valid_rows_df

    # Read the relations from all files
    relations = list(
        map(
            lambda x: read_csv(x),
            files,
        )
    )
    # Merge the relations from all files
    merged_relations = pd.concat(relations, ignore_index=True)

    # Drop the duplicated relations
    logger.info("Before dropping the duplicated relations: %d" % len(merged_relations))
    merged_relations = merged_relations.drop_duplicates(
        subset=[
            "source_id",
            "source_type",
            "target_id",
            "target_type",
            "relation_type",
        ],
        keep="first",
    )
    logger.info("After dropping the duplicated relations: %d" % len(merged_relations))

    # Write the merged relations to a tsv file
    merged_relations.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()
