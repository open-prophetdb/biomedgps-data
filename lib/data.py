import click
import os
import pandas as pd
import requests
import json
from itertools import combinations
from typing import Tuple


def convert_id_to_umls(id, id_type, api_key):
    """
    Convert a ID to UMLS ID using BioPortal's REST API.

    :param id: The ID to convert.
    :param id_type: The type of ID to convert. Must be one of MESH, SNOMEDCT, SYMP, MEDDRA.
    :param api_key: Your BioPortal API key.
    :return: The corresponding UMLS ID, if found.
    """
    base_url = "http://data.bioontology.org"
    headers = {"Authorization": f"apikey token={api_key}"}

    # More details on the API here: https://data.bioontology.org/documentation#Class
    # You can get the related UMLS ids for SYMP from the downloaded file here: https://bioportal.bioontology.org/ontologies/SYMP?p=summary
    if id_type not in ["MESH", "SNOMEDCT", "MEDDRA"]:
        print(
            f"Error: {id_type} is not a valid ID type, must be one of MESH, SNOMEDCT, MEDDRA"
        )
        return None

    if id_type in ["MESH", "SNOMEDCT", "MEDDRA"]:
        path = f"http%3A%2F%2Fpurl.bioontology.org%2Fontology%2F{id_type}%2F{id}"

    url = f"{base_url}/ontologies/{id_type}/classes/{path}"
    print("The URL is: ", url)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        mappings = data.get("cui", [])
        if len(mappings) > 0:
            return mappings[0]
        else:
            print(f"Error: No mappings found for {id}")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def check_format(df: pd.DataFrame) -> bool:
    """Check if a dataframe has the right format

    Args:
        df (pd.DataFrame): Dataframe to check

    Returns:
        bool: True if the dataframe has the right format, False otherwise
    """
    columns = df.columns
    expected_columns = [
        "source_id",
        "source_type",
        "target_id",
        "target_type",
        "relation_type",
        "resource",
    ]
    return all(column in columns for column in expected_columns)


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
    # Remove all rows which are in df_2 from df_1
    df = pd.merge(df_1, df_2, on=index_cols, how="outer", indicator=True)
    df = df[df["_merge"] == "left_only"]
    df = df.drop(columns=["_merge"])
    return df


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

    print("Substracting the two dataframes with the following columns: ", columns)

    df = substract_data(df_1, df_2, index_cols=columns)
    df.to_csv(output, sep="\t", index=False)


@cli.command(help="Prepare a file with hrt format")
@click.option(
    "--input",
    "-i",
    type=str,
    help="A dataframe in a tsv file which contains the following columns: source_type, source_id, relation_type, target_type, target_id. The source_type and target_type columns must be in the format of the entity type (e.g. Gene, Disease, Compound, etc.) and the source_id and target_id columns must be in the format of the entity id (e.g. ENTREZ:1234, MONDO:1234, MESH:D1234, etc.). You can call this format as biomedgps format.",
)
@click.option(
    "--output",
    "-o",
    type=str,
    help="Output file, which will be in the hrt format. The hrt format is a tab-separated file with the following columns: source_id, relation_type, target_id. The source_id and target_id columns are in the format of the entity type and entity id (e.g. Gene::ENTREZ:1234, Disease::MONDO:1234, Compound::MESH:D1234, etc.)",
)
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


@cli.command(help="Merge a list of files into one file by rows")
@click.option(
    "--input",
    "-i",
    type=str,
    help="A csv/tsv file, but you can specify it several times",
    multiple=True,
)
@click.option("--output", "-o", type=str, help="Output file")
def merge_files(input: list, output: str) -> None:
    def detect_separator(file: str) -> str:
        with open(file, "r") as f:
            first_line = f.readline()
            if "\t" in first_line:
                return "\t"
            elif "," in first_line:
                return ","
            else:
                raise ValueError("Separator not found")

    # Get the same columns for all the dataframes
    dfs = [pd.read_csv(file, sep=detect_separator(file)) for file in input]
    common_columns = set(dfs[0].columns)
    for df in dfs[1:]:
        common_columns = common_columns.intersection(set(df.columns))

    columns = list(common_columns)
    if len(columns) == 0:
        raise ValueError("No shared columns found")

    print("Merging the following files: ", input)
    for idx, df in enumerate(dfs):
        print(f"The following columns are in the {input[idx]}: {df.columns.to_list()}")

    print("The following columns will be used: ", columns)

    # Merge the dataframes
    df = pd.concat([df[columns] for df in dfs], ignore_index=True)
    df.to_csv(output, sep="\t", index=False)


@cli.command(help="Check if several files have the same ids")
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="A csv/tsv file which contains knowledges, but you can specify it several times",
    multiple=True,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
    help="Output file",
)
def check_ids(input: list, output: str) -> None:
    def detect_separator(file: str) -> str:
        with open(file, "r") as f:
            first_line = f.readline()
            if "\t" in first_line:
                return "\t"
            elif "," in first_line:
                return ","
            else:
                raise ValueError("Separator not found in file: " + file)

    # 读取数据并检查格式
    dfs = {file: pd.read_csv(file, sep=detect_separator(file)) for file in input}
    for file, df in dfs.items():
        if not check_format(df):
            raise ValueError(f"File {file} does not have the expected format, the columns should be: source_id, source_type, relation_type, target_id, target_type, resource.")

    # 获取实体ID
    ids = {}
    for file, df in dfs.items():
        source_ids = (
            df[["source_type", "source_id"]].astype(str).agg("::".join, axis=1).unique()
        )
        target_ids = (
            df[["target_type", "target_id"]].astype(str).agg("::".join, axis=1).unique()
        )
        ids[file] = set(source_ids).union(set(target_ids))

    # 获取关系类型
    relation_types = {file: set(df["relation_type"]) for file, df in dfs.items()}

    # 计算交集
    output_data = []
    for file_1, file_2 in combinations(input, 2):
        # 实体ID交集
        intersection_ids = ids[file_1].intersection(ids[file_2])
        output_data.append(
            {
                "file1": os.path.basename(file_1),
                "file2": os.path.basename(file_2),
                "num_intersection": len(intersection_ids),
                "num_file1": len(ids[file_1]),
                "num_file2": len(ids[file_2]),
                "category": "ids",
            }
        )

        # 关系类型交集
        intersection_relations = relation_types[file_1].intersection(
            relation_types[file_2]
        )
        output_data.append(
            {
                "file1": os.path.basename(file_1),
                "file2": os.path.basename(file_2),
                "num_intersection": len(intersection_relations),
                "num_file1": len(relation_types[file_1]),
                "num_file2": len(relation_types[file_2]),
                "category": "relation_types",
            }
        )

    # 将结果保存到文件
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(output, sep="\t", index=False)

    print("Number of ids in train, validation, and test: \n{}".format(output_df))

    # 检查文件是否符合要求
    def check_files(df):
        for _, row in df.iterrows():
            # 检查交集数目是否与test或valid的数目一致
            if row["file1"].startswith("train"):
                if row["num_intersection"] != row["num_file2"]:
                    return False
            elif row["file2"].startswith("train"):
                if row["num_intersection"] != row["num_file1"]:
                    return False

        return True

    # 使用该函数检查文件是否符合要求
    is_valid = check_files(output_df)
    if not is_valid:
        raise ValueError(
            "You need to keep the entity ids and relation types in the test and validation files the same as the ones in the train file."
        )
    else:
        print("The files are valid")


@cli.command(help="Keep the train/test/validation datasets valid")
@click.option(
    "--train-file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="A csv/tsv file which contains the train dataset",
)
@click.option(
    "--test-file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="A csv/tsv file which contains the test dataset",
)
@click.option(
    "--valid-file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="A csv/tsv file which contains the validation dataset",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    help="Output directory.",
)
def keep_valid(
    train_file: str, test_file: str, valid_file: str, output_dir: str
) -> None:
    # Read the dataframes
    print("Reading the train, test and validation dataframes...")
    train_df = pd.read_csv(train_file, sep="\t", dtype=str).drop_duplicates()
    print("Found {} rows in train".format(len(train_df)))
    test_df = pd.read_csv(test_file, sep="\t", dtype=str).drop_duplicates()
    print("Found {} rows in test".format(len(test_df)))
    validation_df = pd.read_csv(valid_file, sep="\t", dtype=str).drop_duplicates()
    print("Found {} rows in validation".format(len(validation_df)))

    print("Checking the format of the dataframes...")
    # Check if the dataframes have the right format
    for name, df in zip(
        ["train", "test", "validation"], [train_df, test_df, validation_df]
    ):
        if not check_format(df):
            raise ValueError(f"File {name} does not have the expected format")

    def get_unique_entities(df):
        source_entities = set(zip(df["source_id"], df["source_type"]))
        target_entities = set(zip(df["target_id"], df["target_type"]))
        return source_entities.union(target_entities)

    entities_train = get_unique_entities(train_df)
    print("Found {} entities in train".format(len(entities_train)))
    entities_test = get_unique_entities(test_df)
    print("Found {} entities in test".format(len(entities_test)))
    entities_validation = get_unique_entities(validation_df)
    print("Found {} entities in validation".format(len(entities_validation)))

    entities_intersection = entities_train.intersection(entities_test).intersection(
        entities_validation
    )
    print("Found {} entities in interaction".format(len(entities_intersection)))

    relation_train = set(train_df["relation_type"].str.lower().unique())
    relation_test = set(test_df["relation_type"].str.lower().unique())
    relation_validation = set(validation_df["relation_type"].str.lower().unique())

    relation_intersection = relation_train.intersection(relation_test).intersection(
        relation_validation
    )
    print("Found {} rows in relation intersection".format(len(relation_intersection)))

    def filter_df(df, entities, relations, keep_in_intersection=True):
        source_in_intersection = df.apply(
            lambda row: (row["source_id"], row["source_type"]) in entities, axis=1
        )
        target_in_intersection = df.apply(
            lambda row: (row["target_id"], row["target_type"]) in entities, axis=1
        )
        relation_in_intersection = df["relation_type"].str.lower().isin(relations)

        if keep_in_intersection:
            return df[
                source_in_intersection
                & target_in_intersection
                & relation_in_intersection
            ].drop_duplicates()
        else:
            return df[
                ~(
                    source_in_intersection
                    & target_in_intersection
                    & relation_in_intersection
                )
            ].drop_duplicates()

    # 筛选出交集中的部分和非交集的部分
    test_df_in_intersection = filter_df(
        test_df, entities_intersection, relation_intersection
    )
    print("Found {} rows in test intersection".format(len(test_df_in_intersection)))
    print(
        "Found {} entities in test intersection".format(
            len(get_unique_entities(test_df_in_intersection))
        )
    )
    validation_df_in_intersection = filter_df(
        validation_df, entities_intersection, relation_intersection
    )
    print(
        "Found {} rows in validation intersection".format(
            len(validation_df_in_intersection)
        )
    )
    print(
        "Found {} entities in validation intersection".format(
            len(get_unique_entities(validation_df_in_intersection))
        )
    )

    test_df_not_in_intersection = filter_df(
        test_df,
        entities_intersection,
        relation_intersection,
        keep_in_intersection=False,
    )
    print(
        "Found {} rows in test not in intersection".format(
            len(test_df_not_in_intersection)
        )
    )
    validation_df_not_in_intersection = filter_df(
        validation_df,
        entities_intersection,
        relation_intersection,
        keep_in_intersection=False,
    )
    print(
        "Found {} rows in validation not in intersection".format(
            len(validation_df_not_in_intersection)
        )
    )

    # 将不在交集中的测试集和验证集的部分合并到训练集中
    extended_train_df = pd.concat(
        [train_df, test_df_not_in_intersection, validation_df_not_in_intersection],
        ignore_index=True,
    )
    print("Found {} rows in extended train".format(len(extended_train_df)))

    # 保存处理后的数据集
    extended_train_df.to_csv(
        os.path.join(output_dir, "train_valid.tsv"), sep="\t", index=False
    )
    test_df_in_intersection.to_csv(
        os.path.join(output_dir, "test_valid.tsv"), sep="\t", index=False
    )
    validation_df_in_intersection.to_csv(
        os.path.join(output_dir, "valid_valid.tsv"), sep="\t", index=False
    )


if __name__ == "__main__":
    cli()
