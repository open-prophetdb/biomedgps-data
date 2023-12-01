import click
import re
import os
import pandas as pd

def title_case_to_snake_case(title_str):
    snake_case_str = re.sub(r"(?<!^)(?=[A-Z])", "_", title_str).lower()
    return snake_case_str


@click.command(help="Parse the mondo ontology")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def cli(input, output):
    # Read a csv.gz file and convert it to a data frame
    df = pd.read_csv(
        input, compression="gzip", header=0, sep=",", quotechar='"', low_memory=False
    )

    # Select only the columns that we need
    df = df[
        [
            "Class ID",
            "Preferred Label",
            "Synonyms",
            "Definitions",
            "database_cross_reference",
            "has_obo_namespace",
        ]
    ]

    # Format the id column by using regex to replace the ".*HP_" prefix with "HP:". Must use the regex pattern
    df.loc[:, "Class ID"] = df["Class ID"].apply(lambda x: re.sub(r".*HP_", "HP:", x))

    # Rename the columns
    df = df.rename(
        columns={
            "Class ID": "id",
            "Preferred Label": "name",
            "Synonyms": "synonyms",
            "Definitions": "description",
            "database_cross_reference": "xrefs",
        }
    )

    # Add label column
    df["label"] = "Symptom"

    # Add resource column
    df["resource"] = "HP"

    df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    cli()
