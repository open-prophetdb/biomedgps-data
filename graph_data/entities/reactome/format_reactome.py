import click
import pandas as pd


@click.command(help="Format the entities from Reactome")
@click.option("--input-file", "-i", help="Input file", required=True)
@click.option("--output-file", "-o", help="Output file", required=True)
def cli(input_file, output_file):
    df = pd.read_csv(
        input_file,
        header=None,
        sep="\t",
    )

    df = df.rename(columns={0: "id", 1: "name", 2: "taxname"})

    df["id"] = "REACT:" + df["id"]
    df["label"] = "Pathway"
    df["taxid"] = df["taxname"].apply(lambda x: 9606 if x == "Homo sapiens" else 10090)
    df["resource"] = "Reactome"

    # Remove all unexpected empty characters, such as leading and trailing spaces
    df["description"] = df["description"].fillna("")
    df["description"] = df["description"].apply(lambda x: " ".join(x.strip().split()))

    filtered_df = df[(df["taxname"] == "Homo sapiens") | (df["taxname"] == "Mus musculus")]

    filtered_df.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()
