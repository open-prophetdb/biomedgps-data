import click
import re
import os
import pandas as pd

cli = click.Group()


@cli.command(help="Parse the cell line ontology")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def entities(input, output):
    # Read a csv.gz file and convert it to a data frame
    df = pd.read_csv(input, compression="gzip", header=0, sep=",", quotechar='"', low_memory=False)

    # Select only the columns that we need
    df = df[
        [
            "Class ID",
            "Preferred Label",
            "Synonyms",
            "definition",
            "database_cross_reference",
        ]
    ]

    # Format the id column by using regex to replace the ".*CLO_" prefix with "CLO:". Must use the regex pattern
    df.loc[:, "Class ID"] = df["Class ID"].apply(
        lambda x: re.sub(r".*CLO_", "CLO:", x)
    )

    # Rename the columns
    df = df.rename(
        columns={
            "Class ID": "id",
            "Preferred Label": "name",
            "Synonyms": "synonyms",
            "definition": "description",
            "database_cross_reference": "xrefs",
        }
    )

    # Remove all unexpected empty characters, such as leading and trailing spaces
    df["description"] = df["description"].fillna("")
    df["description"] = df["description"].apply(
        lambda x: " ".join(x.strip().split())
    )

    # Add label column
    df["label"] = "CellLine"

    # Add resource column
    df["resource"] = "CLO"

    df["xrefs"] = df["xrefs"].apply(lambda x: x.replace("UMLS_CUI:", "UMLS:") if type(x) == str else x)

    # Remove all rows which don't have a CLO: prefix in the id column
    df = df[df["id"].str.contains("CLO:")]

    outputfile = os.path.join(output, "clo_cell_line.tsv")
    # Write the data frame to a tsv file
    df.to_csv(outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
