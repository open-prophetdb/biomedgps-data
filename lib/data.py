import click
import numpy as np
import pandas as pd
from typing import Tuple


def split_data(
    df: pd.DataFrame, ratio: float, seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split a dataframe into two subsets.

    Args:
        df (pd.DataFrame): Dataframe to split
        ratio (float): Ratio of the split
        seed (int, optional): Seed for the random split. Defaults to 42.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Two subsets of the dataframe
    """
    df_1 = df.sample(frac=ratio, random_state=seed)
    df_2 = df.drop(df_1.index)
    return df_1, df_2


def substract_data(
    df_1: pd.DataFrame, df_2: pd.DataFrame, index_cols: list
) -> pd.DataFrame:
    """Substract two dataframes

    Args:
        df_1 (pd.DataFrame): First dataframe
        df_2 (pd.DataFrame): Second dataframe
        index_cols (list): List of columns to use as index

    Returns:
        pd.DataFrame: Substraction of the two dataframes
    """
    # Remove all rows from df_1 that are in df_2 (based on the index_cols)
    df_1 = df_1[~df_1[index_cols].isin(df_2[index_cols]).all(axis=1)]
    return df_1


cli = click.Group()


@cli.command(help="Split a dataframe into two subsets")
@click.option("--input", "-i", type=str, help="A dataframe in a tsv file")
@click.option("--output-1", "-o1", type=str, help="Output file for subset 1")
@click.option("--output-2", "-o2", type=str, help="Output file for subset 2")
@click.option("--ratio", "-r", type=float, help="Ratio of the split", default=0.5)
@click.option("--seed", "-s", type=int, help="Seed for the random split", default=42)
def split(input: str, output_1: str, output_2: str, ratio: float, seed: int) -> None:
    df = pd.read_csv(input, sep="\t")
    df_1, df_2 = split_data(df, ratio, seed)
    df_1.to_csv(output_1, sep="\t", index=False)
    df_2.to_csv(output_2, sep="\t", index=False)


@cli.command(help="Substract two dataframes")
@click.option("--input-1", "-i1", type=str, help="First dataframe")
@click.option("--input-2", "-i2", type=str, help="Second dataframe")
@click.option("--output", "-o", type=str, help="Output file")
def substract(input_1: str, input_2: str, output: str) -> None:
    df_1 = pd.read_csv(input_1, sep="\t")
    df_2 = pd.read_csv(input_2, sep="\t")

    columns_1 = df_1.columns
    columns_2 = df_2.columns

    # Find the columns that are in both dataframes
    columns = [column for column in columns_1 if column in columns_2]
    df_1 = df_1[columns]
    df_2 = df_2[columns]

    df = substract_data(df_1, df_2, index_cols=columns)
    df.to_csv(output, sep="\t", index=False)


@cli.command(help="Prepare a file with hrt format")
@click.option("--input", "-i", type=str, help="A dataframe in a tsv file")
@click.option("--output", "-o", type=str, help="Output file")
def hrt(input: str, output: str) -> None:
    relations = pd.read_csv(input, sep="\t")

    # Check if the dataframe has the right columns
    columns = ["source_type", "source_id", "relation_type", "target_type", "target_id"]
    assert all(
        column in relations.columns for column in columns
    ), f"Columns {columns} not found in {input}"

    df = pd.DataFrame()
    # Merge the source_type and source_id columns
    df["merged_source_id"] = (
        relations["source_type"] + "::" + relations["source_id"].astype(str)
    )

    # Merge the target_type and target_id columns
    df["merged_target_id"] = (
        relations["target_type"] + "::" + relations["target_id"].astype(str)
    )

    df["relation_type"] = relations["relation_type"]

    # Reorder the columns
    df = df[["merged_source_id", "relation_type", "merged_target_id"]]

    # Remove the header
    df.to_csv(output, sep="\t", index=False, header=False)


if __name__ == "__main__":
    cli()
