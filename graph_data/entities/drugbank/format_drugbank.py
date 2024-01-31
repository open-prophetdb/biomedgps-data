import click
import os
import pandas as pd


@click.command(
    help="Parse drugbank vocabulary and convert it to a biomedgps entity file."
)
@click.option(
    "--input-file",
    "-i",
    required=True,
    help="The input file path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--output-file",
    "-o",
    required=True,
    help="The output file path",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def format(input_file, output_file):
    # Read a csv.gz file and convert it to a data frame
    df = pd.read_csv(input_file, sep=",", quotechar='"', low_memory=False)

    # Select only the columns that we need
    df = df[
        [
            "DrugBank ID",
            "Accession Numbers",
            "Common name",
            "CAS",
            "UNII",
            "Synonyms",
            "Standard InChI Key",
        ]
    ]

    # Add label column
    df["label"] = "Compound"

    # Add resource column
    df["resource"] = "DrugBank"

    df = df.rename(
        columns={
            "DrugBank ID": "id",
            "Common name": "name",
            "label": "label",
            "resource": "resource",
            "Accession Numbers": "accession_numbers",
            "CAS": "cas_number",
            "UNII": "unii",
            "Synonyms": "synonyms",
            "Standard InChI Key": "inchi_key",
        }
    )

    df["id"] = "DrugBank:" + df["id"].astype(str)

    # Remove the white spaces from the synonyms
    df["synonyms"] = df["synonyms"].str.replace(" ", "")

    # Save the data frame as a csv file
    df.to_csv(
        output_file,
        index=False,
        header=True,
        sep="\t",
    )


if __name__ == "__main__":
    format()
