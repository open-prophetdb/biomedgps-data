import os
import re
import click
import pandas as pd


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

    # Filter the matched resources
    files = list(
        filter(
            lambda x: x.endswith(".tsv") and x.startswith("formatted_"),
            resources,
        )
    )

    def read_csv(filepath: str):
        print("Reading %s" % filepath)
        return pd.read_csv(filepath, sep="\t", quotechar='"', low_memory=False)

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
    print("Before dropping the duplicated relations: %d" % len(merged_relations))
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
    print("After dropping the duplicated relations: %d" % len(merged_relations))

    # Write the merged relations to a tsv file
    merged_relations.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()
