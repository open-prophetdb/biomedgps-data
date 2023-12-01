import click
import pandas as pd


@click.command(help="csv to tsv")
@click.option("--input", "-i", help="Input file", required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--output", "-o", help="Output directory", required=True, type=click.Path(exists=False, file_okay=True, dir_okay=False))
def cli(input, output):
    data = pd.read_csv(input, sep=",", quotechar='"', low_memory=False)
    data.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    cli()
