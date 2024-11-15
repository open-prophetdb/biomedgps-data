import pandas as pd
import click



@click.command(help="Extract relation types from a relation file")
@click.option(
    "--input-file",
    "-i",
    help="Relation file path, such as relations.tsv",
    required=True,
)
@click.option(
    "--output-file",
    "-o",
    help="Output file path, such as relation_types.tsv",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def cli(input_file, output_file):
    print("Reading %s" % input_file)
    data = pd.read_csv(input_file, sep="\t", low_memory=False)

    print("Extracting, sorting and deduplicating relation types...")
    relation_types = data["relation_type"].drop_duplicates().sort_values()

    header = pd.Series(["relation_type"])
    sorted_relation_types = pd.concat([header, relation_types]).reset_index(drop=True)

    print("Writing to %s" % output_file)
    sorted_relation_types.to_csv(output_file, index=False, header=False, sep="\t")



if __name__ == "__main__":
    cli()
