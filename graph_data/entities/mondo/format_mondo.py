import click
import re
import os
import pandas as pd


cli = click.Group()


@cli.command(help="Parse the mondo ontology")
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

    # Format the id column by using regex to replace the ".*MONDO_" prefix with "MONDO:". Must use the regex pattern
    df.loc[:, "Class ID"] = df["Class ID"].apply(
        lambda x: re.sub(r".*MONDO_", "MONDO:", x)
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

    # Add label column
    df["label"] = "Disease"

    # Add resource column
    df["resource"] = "Mondo"

    # Remove all unexpected empty characters, such as leading and trailing spaces
    df["description"] = df["description"].fillna("")
    df["description"] = df["description"].apply(lambda x: " ".join(x.strip().split()))

    outputfile = os.path.join(output, "mondo_disease.tsv")
    # Write the data frame to a tsv file
    df.to_csv(outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
