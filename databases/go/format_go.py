import click
import re
import os
import pandas as pd

cli = click.Group()


def title_case_to_snake_case(title_str):
    snake_case_str = re.sub(r"(?<!^)(?=[A-Z])", "_", title_str).lower()
    return snake_case_str


@cli.command(help="Parse the mondo ontology")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def entities(input, output):
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
            "Obsolete",
        ]
    ]

    # Format the id column by using regex to replace the ".*UBERON_" prefix with "UBERON:". Must use the regex pattern
    df.loc[:, "Class ID"] = df["Class ID"].apply(lambda x: re.sub(r".*GO_", "GO:", x))

    # Rename the columns
    df = df.rename(
        columns={
            "Class ID": "id",
            "Preferred Label": "name",
            "Synonyms": "synonyms",
            "Definitions": "description",
            "database_cross_reference": "xrefs",
            "has_obo_namespace": "label",
            "Obsolete": "obsolete",
        }
    )

    label_map = {
        "cellular_component": "CellularComponent",
        "biological_process": "BiologicalProcess",
        "molecular_function": "MolecularFunction",
    }

    # Add label column
    df["label"] = df["label"].apply(lambda x: label_map.get(x, "Unknown"))

    # Add resource column
    df["resource"] = "GO"

    # Remove all obsolete terms
    # It may cause some compatible issues when it works with the other databases, so we comment it out
    # df = df[(df["obsolete"] == False) | (df["obsolete"] == "FALSE")]

    grouped = df.groupby("label")
    for label, group in grouped:
        outputfile = os.path.join(output, "go_%s.tsv" % title_case_to_snake_case(label))
        # Write the data frame to a tsv file
        group.to_csv(outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
