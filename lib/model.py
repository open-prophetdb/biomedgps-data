import sys
import csv
import re
import pandas as pd
import numpy as np
import torch.nn.functional as fn
import torch as th


def load_model(entity_file, relation_file, entity_emb_file, rel_emb_file):
    # Get drugname/disease name to entity ID mappings
    entity_map = {}
    entity_id_map = {}
    relation_map = {}
    nodetype_ids = {}
    ntypePattern = re.compile(r"^(.*)::")

    with open(entity_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t", fieldnames=["id", "name"])
        for row_val in reader:
            ntype = ntypePattern.match(row_val["name"]).group(1)
            iid = int(row_val["id"])
            entity_map[row_val["name"]] = iid
            entity_id_map[iid] = row_val["name"]
            if ntype not in nodetype_ids:
                nodetype_ids[ntype] = []
            nodetype_ids[ntype].append(iid)

    with open(relation_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t", fieldnames=["id", "name"])
        for row_val in reader:
            relation_map[row_val["name"]] = int(row_val["id"])

    # Load embeddings
    entity_emb = np.load(entity_emb_file)
    rel_emb = np.load(rel_emb_file)

    return {
        "entity_map": entity_map,
        "entity_id_map": entity_id_map,
        "relation_map": relation_map,
        "nodetype_ids": nodetype_ids,
        "entity_embedding": entity_emb,
        "rel_embedding": rel_emb,
    }


def distance(head, tail):
    score = head - tail
    return th.norm(score, p=2, dim=-1)


def transE_l2(head, rel, tail, gamma=12.0):
    score = head + rel - tail
    return gamma - th.norm(score, p=2, dim=-1)


def query(
    model_map, relations: list[str], source_id: str, reverse_prediction: bool = True
):
    """
    relations: ['Hetionet::CtD::Compound:Disease', 'GNBR::T::Compound:Disease', 'DRUGBANK::treats::Compound:Disease']
    source_id: MESH:D015673
    """
    if reverse_prediction:
        target, source = relations[0].split("::")[2].split(":")
    else:
        source, target = relations[0].split("::")[2].split(":")

    relation_map = model_map.get("relation_map")
    relation_ids = [relation_map[relation] for relation in relations]
    relation_ids = th.tensor(relation_ids)
    rel_emb = model_map.get("rel_embedding")
    relations_embs = [th.tensor(rel_emb[rid]) for rid in relation_ids]

    sources = [source + "::" + source_id]
    print("Source ID: ", sources)

    entity_map = model_map.get("entity_map")
    source_ids = [entity_map[source] for source in sources if source in entity_map]
    source_ids = th.tensor(source_ids)

    nodetype_ids = model_map.get("nodetype_ids")
    target_ids = nodetype_ids[target]
    target_ids = th.tensor(target_ids)

    entity_emb = model_map.get("entity_embedding")
    target_emb = th.tensor(entity_emb[target_ids])

    return {
        "relation_ids": relation_ids,
        "relations_embeddings": relations_embs,
        "source_ids": source_ids,
        "target_ids": target_ids,
        "target_embedding": target_emb,
        "relations": relations,
    }


# one for each
def relation_each(model_map, results, reverse_prediction=True, topk=100):
    allpd = pd.DataFrame()
    relations_embs = results.get("relations_embeddings")
    source_ids = results.get("source_ids")
    entity_emb = model_map.get("entity_embedding")
    target_emb = results.get("target_embedding")
    relations = results.get("relations")
    target_ids = results.get("target_ids")
    entity_id_map = model_map.get("entity_id_map")

    for rid in range(len(relations_embs)):
        relation_embs = relations_embs[rid]
        for source_id in source_ids:
            source_emb = th.tensor(entity_emb[source_id])
            if reverse_prediction:
                score = fn.logsigmoid(transE_l2(target_emb, relation_embs, source_emb))
            else:
                score = fn.logsigmoid(transE_l2(source_emb, relation_embs, target_emb))

            newpd = pd.DataFrame(
                {
                    "relation": relations[rid],
                    "source_id": int(source_id),
                    "target_id": target_ids.tolist(),
                    "score": score.tolist(),
                }
            )

            allpd = pd.concat([allpd, newpd])
            # scores_per_sources.append(score)
            # dids.append(target_ids)

    topkpd = allpd.sort_values("score", ascending=False).head(n=topk)
    topkpd["source"] = [entity_id_map[i] for i in topkpd["source_id"]]
    topkpd["target"] = [entity_id_map[i] for i in topkpd["target_id"]]
    return topkpd


# average source_id
def relation_ave(model_map, results, reverse_prediction=True, topk=100):
    relations_embs = results.get("relations_embeddings")
    entity_emb = model_map.get("entity_embedding")
    source_ids = results.get("source_ids")
    target_ids = results.get("target_ids")
    target_emb = results.get("target_embedding")
    entity_id_map = model_map.get("entity_id_map")
    relations = results.get("relations")
    allpd = pd.DataFrame()
    for rid in range(len(relations_embs)):
        relation_embs = relations_embs[rid]

        source_emb = th.mean(th.tensor(entity_emb[source_ids]), 0)
        if reverse_prediction:
            score = fn.logsigmoid(transE_l2(target_emb, relation_embs, source_emb))
        else:
            score = fn.logsigmoid(transE_l2(source_emb, relation_embs, target_emb))
        newpd = pd.DataFrame(
            {
                "relation": relations[rid],
                "target_id": target_ids.tolist(),
                "score": score.tolist(),
            }
        )

        allpd = pd.concat([allpd, newpd])
        # scores_per_sources.append(score)
        # dids.append(target_ids)

    topkpd = allpd.sort_values("score", ascending=False).head(n=topk)
    topkpd["target"] = [entity_id_map[i] for i in topkpd["target_id"]]
    return topkpd


def check_relation_exists(row, relations_df):
    source_type, source_id = row["source"].split("::")
    target_type, target_id = row["target"].split("::")
    option1 = (source_id, source_type, target_id, target_type) in relations_df.index

    target_type, target_id = row["source"].split("::")
    source_type, source_id = row["target"].split("::")
    option2 = (source_id, source_type, target_id, target_type) in relations_df.index
    return option1 or option2


def draw_score_hist(topkpd):
    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.set(style="ticks")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(x="score", hue="relation", data=topkpd, element="step", ax=ax)


def draw_score_hist_plotly(topkpd, nbins=100):
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
