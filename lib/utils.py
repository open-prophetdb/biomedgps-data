import pandas as pd
from typing import List, Dict, Union

# Return matched line if a id matches with the id or xrefs in the entities.tsv
def get_matched_id(id: str, etype: str, entities: pd.DataFrame) -> Union[None, str]:
    """Get matched id if a id matches with the id or xrefs in the entities.tsv

    Args:
        id (str): entity id
        etype (str): entity type
        entities (pd.DataFrame): entities.tsv

    Returns:
        str: matched id
    """
    rows = entities[
        ((entities["id"] == id) | entities["xrefs"].str.contains(id))
        & (entities["label"] == etype)
    ]
    if len(rows) == 0:
        return None
    else:
        return rows.iloc[0]["id"]


def get_matched_name(id: str, etype: str, entities: pd.DataFrame) -> Union[None, str]:
    """Get matched name if a id matches with the id or xrefs in the entities.tsv

    Args:
        id (str): entity id
        etype (str): entity type
        entities (pd.DataFrame): entities.tsv

    Returns:
        str: matched name
    """
    rows = entities[
        ((entities["id"] == id) | entities["xrefs"].str.contains(id))
        & (entities["label"] == etype)
    ]
    if len(rows) == 0:
        return None
    else:
        return rows.iloc[0]["name"]

def remove_whitespace(text: str) -> str:
    """Remove whitespace from text

    Args:
        text (str): text

    Returns:
        str: text without newline characters, leading and trailing spaces, multiple spaces
    """
    return " ".join(text.strip().split())
