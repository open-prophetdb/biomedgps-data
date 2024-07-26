# Standard library packages
import io
import logging
import click


# Import Biopython modules to interact with KEGG
from Bio.KEGG import REST
import pandas as pd

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("format_wikipathways.py")
logging.basicConfig(level=logging.INFO, format=fmt)

organism_keys = {
    "Homo sapiens": "hsa",
    "Mus musculus": "mmu",
    "Rattus norvegicus": "rno",
}

organism_ids = {
    "hsa": "9606",
    "mmu": "10090",
    "rno": "10116",
}


def to_df(result):
    df = pd.read_table(io.StringIO(result), header=None)
    # Change the column names
    df = df.rename(columns={0: "id", 1: "name"})
    return df

def get_value(line):
    items = line.split()
    if len(items) >= 2:
        return " ".join(items[1:])
    else:
        return ""

def get_pathway(pathway_id):
    """Get a dict from a pathway text.

    Args:
        pathway_id: a pathway id, such as hsa00010

    An example of pathway text:
    ENTRY       hsa01521                    Pathway
    NAME        EGFR tyrosine kinase inhibitor resistance - Homo sapiens (human)
    DESCRIPTION EGFR is a tyrosine kinase that participates in the regulation of cellular homeostasis.
    """
    result = REST.kegg_get(pathway_id).read()

    lines = result.split('\n')

    # Initialize variables to store extracted information
    description = ""
    references = []

    # Iterate through the lines to extract the fields
    for line in lines:
        if line.startswith("DESCRIPTION"):
            description = get_value(line)
        elif line.startswith("REFERENCE"):
            references.append(get_value(line))

    pmids = [reference.replace("PMID:", "") for reference in references if reference]

    return {
        "description": description,
        "pmids": pmids
    }

def get_pathways(organism):
    # Get all entries in the PATHWAY database for K. setae as a dataframe
    result = REST.kegg_list("pathway", organism).read()
    df = to_df(result)

    pathways = []

    for index, pathway in df.iterrows():
        id = pathway.get("id")
        name = pathway.get("name")
        logger.info("Processing pathway %s", id)
        pathway_additional_info = get_pathway(id)

        pathway_dict = {
            "resource": "KEGG",
            "label": "Pathway",
            "id": f"KEGG:{id}",
            "name": name,
            "synonyms": "",
            "description": pathway_additional_info.get("description"),
            "xrefs": "",
            "taxid": f"{organism_ids.get(organism)}",
            "pmids": "|".join(pathway_additional_info.get("pmids"))  # type: ignore
        }

        pathways.append(pathway_dict)

    return pathways


@click.command(help="Extract entities from wikipathways' api")
@click.option(
    "--output",
    "-o",
    required=True,
    help="Output file",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def extract(output):
    pathway_df = pd.DataFrame()
    for organism in organism_keys.values():
        pathway_lst = get_pathways(organism)
        # Merge pathway_lst into pathway_df by rows
        pathway_df = pd.concat(
            [pathway_df, pd.DataFrame(pathway_lst)], ignore_index=True
        )

    # Remove all unexpected empty characters, such as leading and trailing spaces
    pathway_df["description"] = pathway_df["description"].fillna("")
    pathway_df["description"] = pathway_df["description"].apply(
        lambda x: " ".join(x.strip().split())
    )
    pathway_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    extract()
