import os
import click
import pandas as pd


cli = click.Group()


@cli.command(help="Format the entities from Hetionet")
@click.option("--input", "-i", help="Input file", required=True)
@click.option("--output-dir", "-o", help="Output directory", required=True)
def entities(input, output_dir):
    # Read a tsv file and convert it to a data frame
    df = pd.read_csv(input, sep="\t", quotechar='"')

    grouped = df.groupby("kind")
    for group in grouped.groups.keys():
        output_file = os.path.join(
            output_dir, "hetionet_" + group.replace(" ", "_").lower() + ".tsv" # type: ignore
        )
        data = grouped.get_group(group)
        # Format the id column
        if group in [
            "Anatomy",
            "Biological Process",
            "Cellular Component",
            "Disease",
            "Molecular Function",
        ]:
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("%s::" % group, ""))
            data.loc[:, "kind"] = data["kind"].apply(lambda x: x.replace(" ", ""))
        elif group == "Gene":
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("%s::" % group, "ENTREZ:"))
        elif group == "Compound":
            data.loc[:, "id"] = data["id"].apply(
                lambda x: x.replace("%s::" % group, "DrugBank:")
            )
        elif group == "Pathway":
            # Filter out the pathways that start with "WP"
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("%s::" % group, ""))
            data = data[data["id"].str.startswith("WP")]
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("WP", "WikiPathways:WP").split("_")[0])
        elif group == "Pharmacologic Class":
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("%s::" % group, "NDF-RT:"))
            data.loc[:, "kind"] = data["kind"].apply(lambda x: x.replace(" ", ""))
        elif group == "Side Effect":
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("%s::" % group, "UMLS:"))
            data.loc[:, "kind"] = data["kind"].apply(lambda x: x.replace(" ", ""))
        elif group == "Symptom":
            data.loc[:, "id"] = data["id"].apply(lambda x: x.replace("%s::" % group, "MESH:"))

        # Rename the columns
        data = data.rename(columns={"id": "id", "name": "name", "kind": "label"})

        # Add resource column
        data.loc[:, "resource"] = "Hetionet"

        # Write the data frame to a tsv file
        data.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()
