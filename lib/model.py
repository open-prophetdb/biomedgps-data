import pandas as pd
from pathlib import Path
from typing import Tuple
import click

cli = click.Group(help="The command line interface for the model")


def check_relation_exists(row: pd.Series, relations_df: pd.DataFrame) -> bool:
    source_type, source_id = row["source"].split("::")
    target_type, target_id = row["target"].split("::")
    option1 = (source_id, source_type, target_id, target_type) in relations_df.index

    target_type, target_id = row["source"].split("::")
    source_type, source_id = row["target"].split("::")
    option2 = (source_id, source_type, target_id, target_type) in relations_df.index
    return option1 or option2


def draw_score_hist(topkpd: pd.DataFrame) -> None:
    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.set(style="ticks")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(x="score", hue="relation", data=topkpd, element="step", ax=ax)


def draw_score_hist_plotly(topkpd: pd.DataFrame, nbins: int = 100) -> None:
    # Show the score distribution with plotly
    import plotly.express as px

    fig = px.histogram(topkpd, x="score", nbins=nbins)
    fig.show()


def merge_topkpd_with_entities_relations(
    topkpd: pd.DataFrame, entities: pd.DataFrame, relations: pd.DataFrame
) -> pd.DataFrame:
    """Merge the topkpd with the entities and relations dataframes

    Args:
        topkpd (pd.DataFrame): The topkpd dataframe
        entities (pd.DataFrame): The entities dataframe
        relations (pd.DataFrame): The relations dataframe

    Returns:
        pd.DataFrame: The merged dataframe
    """
    # Join the topkpd with the entity dataframe
    df = entities.copy()
    relations_df = relations.copy()

    df["node_id"] = entities["label"] + "::" + entities["id"]
    merged = topkpd.merge(df, left_on="target", right_on="node_id")

    relations_df.set_index(
        ["source_id", "source_type", "target_id", "target_type"], inplace=True
    )

    # Apply the function with axis=1 to check if the relationship exists
    merged["status"] = merged.apply(check_relation_exists, args=(relations_df,), axis=1)
    return merged


def merge_scores_with_entities_relations(
    scores: pd.DataFrame,
    entities: pd.DataFrame,
    relations: pd.DataFrame,
    target: str = "head",
) -> pd.DataFrame:
    """Merge the topkpd with the entities and relations dataframes

    Args:
        scores (pd.DataFrame): The scores dataframe, which have four columns: head, rel, tail, score
        entities (pd.DataFrame): The entities dataframe
        relations (pd.DataFrame): The relations dataframe

    Returns:
        pd.DataFrame: The merged dataframe
    """
    # Join the topkpd with the entity dataframe
    df = entities.copy()
    relations_df = relations.copy()

    scores = scores.rename(
        columns={"head": "source", "tail": "target", "rel": "relation"}
    )

    column_name = "source" if target == "head" else "target"

    df["node_id"] = entities["label"] + "::" + entities["id"]
    merged = scores.merge(df, left_on=column_name, right_on="node_id")

    relations_df.set_index(
        ["source_id", "source_type", "target_id", "target_type"], inplace=True
    )

    # Apply the function with axis=1 to check if the relationship exists
    merged["status"] = merged.apply(check_relation_exists, args=(relations_df,), axis=1)
    return merged


@cli.command(
    help="Load the embeddings from the given filepaths and save them as .tsv files."
)
@click.option(
    "--entity_emb_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the entity embeddings",
)
@click.option(
    "--relation_emb_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the relation embeddings",
)
@click.option(
    "--entity_id_map_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the entity id map",
)
@click.option(
    "--relation_type_id_map_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the relation type id map",
)
@click.option(
    "--output_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="The output directory to save the embeddings",
)
def load_embeddings(
    entity_emb_fpath: Path,
    relation_emb_fpath: Path,
    entity_id_map_fpath: Path,
    relation_type_id_map_fpath: Path,
    output_dir: Path,
) -> Tuple[Path, Path]:
    """Load the embeddings from the given filepaths

    Args:
        entity_emb_fpath (str): The filepath of the entity embeddings
        relation_emb_fpath (str): The filepath of the relation embeddings

    Returns:
        tuple: A tuple of two numpy arrays, the first one is the entity embeddings, the second one is the relation embeddings. Each file has two columns: 'id' and 'embedding'.
    """
    import numpy as np
    import pandas as pd
    import os

    def validate_npy_file(file_path):
        try:
            np.load(file_path)
            return True
        except:
            return False

    def validate_tsv_file(file_path, expected_columns):
        if not os.path.exists(file_path):
            return False
        try:
            df = pd.read_csv(file_path, sep="\t", header=None)
            return len(df.columns) == expected_columns
        except:
            return False

    # Validate the file paths
    if not validate_npy_file(entity_emb_fpath):
        raise ValueError(
            "Cannot load '%s' or file format is incorrect" % entity_emb_fpath
        )
    if not validate_npy_file(relation_emb_fpath):
        raise ValueError(
            "Cannot load '%s' or file format is incorrect" % relation_emb_fpath
        )
    if not validate_tsv_file(entity_id_map_fpath, 2):
        raise ValueError(
            "Cannot load '%s' or file format is incorrect, we expect 2 columns which one is 'idx' and the other is 'entity_id'"
            % entity_id_map_fpath
        )
    if not validate_tsv_file(relation_type_id_map_fpath, 2):
        raise ValueError(
            "Cannot load '%s' or file format is incorrect, we expect 2 columns which one is 'idx' and the other is 'relation_type_id'"
            % relation_type_id_map_fpath
        )

    # Load the embeddings
    entity_embeddings = np.load(entity_emb_fpath)
    relation_type_embeddings = np.load(relation_emb_fpath)

    # Load the entity and relation type id map
    entity_id_map = pd.read_csv(
        entity_id_map_fpath, sep="\t", header=None, names=["idx", "entity_id"]
    )
    relation_type_id_map = pd.read_csv(
        relation_type_id_map_fpath,
        sep="\t",
        header=None,
        names=["idx", "relation_type_id"],
    )

    # Save the embeddings as .tsv files
    entity_embeddings_df = entity_id_map.copy()
    entity_embeddings_df["embedding"] = entity_embeddings_df["idx"].apply(
        lambda x: "|".join(entity_embeddings[x].astype(str))
    )
    entity_embeddings_df.rename(columns={"entity_id": "id"}, inplace=True)

    relation_type_embeddings_df = relation_type_id_map.copy()
    relation_type_embeddings_df["embedding"] = relation_type_embeddings_df["idx"].apply(
        lambda x: "|".join(relation_type_embeddings[x].astype(str))
    )
    relation_type_embeddings_df.rename(columns={"relation_type_id": "id"}, inplace=True)

    entity_embedding_fpath = output_dir / "entity_embeddings.tsv"
    relation_embedding_fpath = output_dir / "relation_type_embeddings.tsv"
    entity_embeddings_df[["id", "embedding"]].to_csv(
        entity_embedding_fpath, sep="\t", index=False
    )
    relation_type_embeddings_df[["id", "embedding"]].to_csv(
        relation_embedding_fpath, sep="\t", index=False
    )


class ModelEnum:
    TransE_l2 = "TransE_l2"
    TransE_l1 = "TransE_l1"
    ComplEx = "ComplEx"
    DistMult = "DistMult"
    RotatE = "RotatE"
    TransR = "TransR"
    TransD = "TransD"
    TransH = "TransH"


@cli.command(
    help="Compute the attention scores with the given model for each relation."
)
@click.option(
    "--entity_emb_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the entity embeddings",
)
@click.option(
    "--relation_type_emb_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the relation embeddings",
)
@click.option(
    "--relations_fpath",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
    help="The filepath of the relations (tsv file), which has a head-relation-tail format with three columns: source_id, relation_type, target_id.",
)
@click.option(
    "--output_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="The output directory to save the attention scores",
)
@click.option(
    "--model_name",
    type=click.Choice(
        [
            ModelEnum.TransE_l2,
            ModelEnum.TransE_l1,
            ModelEnum.ComplEx,
            ModelEnum.DistMult,
            ModelEnum.RotatE,
            ModelEnum.TransR,
            ModelEnum.TransD,
            ModelEnum.TransH,
        ],
        case_sensitive=False,
    ),
    default=ModelEnum.TransE_l2,
    help="The model name",
)
def compute_attention_scores(
    entity_emb_fpath: Path,
    relation_type_emb_fpath: Path,
    relations_fpath: Path,
    output_dir: Path,
    model_name: ModelEnum = ModelEnum.TransE_l2,
) -> Path:
    """Compute the attention scores for the given model

    Args:
        entity_emb_fpath (Path): The filepath of the entity embeddings
        relation_type_emb_fpath (Path): The filepath of the relation embeddings
        relations_fpath (Path): The filepath of the relations (tsv file), which has a head-relation-tail format with three columns: source_id, relation_type, target_id.
        output_dir (Path): The output directory
        model_name (ModelEnum, optional): The model name. Defaults to ModelEnum.TransE_l2.

    Returns:
        Path: The filepath of the attention scores
    """
    import pandas as pd
    import numpy as np

    # Load the embeddings
    def load_embeddings(file_path):
        df = pd.read_csv(file_path, sep="\t")
        embeddings = {
            row["id"]: np.array(row["embedding"].split("|"), dtype=float)
            for index, row in df.iterrows()
        }
        return embeddings

    entity_embeddings = load_embeddings(entity_emb_fpath)
    relation_type_embeddings = load_embeddings(relation_type_emb_fpath)
    relations = pd.read_csv(
        relations_fpath,
        sep="\t",
        header=None,
        names=["source_id", "relation_type", "target_id"],
    )

    # TransE Score
    def transe_l2_score(h, r, t):
        return -np.linalg.norm(h + r - t, ord=2)

    def transe_l1_score(h, r, t):
        return -np.linalg.norm(h + r - t, ord=1)

    def complex_score(h, r, t):
        return np.sum(h * r * np.conj(t), axis=-1)

    def distmult_score(h, r, t):
        return np.sum(h * r * t, axis=-1)

    def rotate_score(h, r, t):
        re_head, im_head = np.split(h, 2, axis=-1)
        re_tail, im_tail = np.split(t, 2, axis=-1)
        re_relation, im_relation = np.split(r, 2, axis=-1)
        score = (
            re_head * re_relation * re_tail
            + re_head * im_relation * im_tail
            + im_head * re_relation * im_tail
            - im_head * im_relation * re_tail
        )
        return score

    def transr_score(h, r, t):
        h = h.reshape(-1, 1)
        t = t.reshape(-1, 1)
        M_r = relation_type_embeddings[r].reshape(-1, 1)
        score = -np.linalg.norm(h + M_r - t, ord=2)
        return score

    def transd_score(h, r, t):
        h = h.reshape(-1, 1)
        t = t.reshape(-1, 1)
        M_r = relation_type_embeddings[r].reshape(-1, 1)
        score = -np.linalg.norm(h + M_r - t, ord=2)
        return score

    def transh_score(h, r, t):
        h = h.reshape(-1, 1)
        t = t.reshape(-1, 1)
        M_r = relation_type_embeddings[r].reshape(-1, 1)
        score = -np.linalg.norm(h + M_r - t, ord=2)
        return score

    model_score_func = {
        "TransE_l2": transe_l2_score,
        "TransE_l1": transe_l1_score,
        "ComplEx": complex_score,
        "DistMult": distmult_score,
        "RotatE": rotate_score,
        "TransR": transr_score,
        "TransD": transd_score,
        "TransH": transh_score,
    }

    # Compute the scores for each relation with the given model
    all_scores = []
    for index, row in relations.iterrows():
        score = model_score_func[model_name](
            entity_embeddings[row["source_id"]],
            relation_type_embeddings[row["relation_type"]],
            entity_embeddings[row["target_id"]],
        )
        all_scores.append(
            (row["source_id"], row["target_id"], row["relation_type"], score)
        )

    # Create the dataframe for the scores
    scores_df = pd.DataFrame(
        all_scores, columns=["source_id", "target_id", "relation_type", "score"]
    )

    # Apply softmax to the scores
    def softmax(scores):
        exp_scores = np.exp(scores - np.max(scores))  # 防止数值溢出
        return exp_scores / exp_scores.sum()

    # Compute the softmax scores for each target entity
    softmax_scores = []
    for target_id in relations["target_id"].unique():
        target_scores = scores_df[scores_df["target_id"] == target_id][
            "score"
        ].to_numpy()

        softmax_vals = softmax(target_scores)
        print("softmax_vals:", softmax_vals)
        print("target_ids:", scores_df[scores_df["target_id"] == target_id])

        idx = 0
        for _, row in scores_df[scores_df["target_id"] == target_id].iterrows():
            softmax_scores.append(
                (
                    row["source_id"],
                    row["target_id"],
                    row["relation_type"],
                    softmax_vals[idx],
                )
            )
            idx += 1

    # Create the final dataframe
    final_df = pd.DataFrame(
        softmax_scores,
        columns=["source_id", "target_id", "relation_type", "score"],
    )

    # Save the attention scores
    attention_scores_fpath = output_dir / "attention_scores.tsv"
    final_df.to_csv(attention_scores_fpath, sep="\t", index=False)


if __name__ == "__main__":
    cli()
