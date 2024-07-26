import pywikipathways as pwpw
import xmltodict
import logging
import click
import pandas as pd

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("format_wikipathways.py")
logging.basicConfig(level=logging.INFO, format=fmt)

# Disable SettingWithCopyWarning
pd.options.mode.chained_assignment = None

organisms = {
    "Homo sapiens": "9606",
    "Mus musculus": "10090",
    "Rattus norvegicus": "10116",
}


def parse_gpml(gpml_str):
    gpml = xmltodict.parse(gpml_str)
    logger.debug("GPML: %s" % gpml)
    return gpml


def get_pathway_lst(organism):
    pathways = pwpw.list_pathways(organism)
    pathway_dicts = []

    for index, pathway in pathways.iterrows():  # type: ignore
        id = pathway.get("id")
        gpml_str = pwpw.get_pathway(id)
        descriptions = parse_gpml(gpml_str).get("Pathway", {}).get("Comment", {})
        print("Description: %s" % descriptions)
        if type(descriptions) == dict:
            descriptions = [descriptions]

        filtered_descriptions = list(
            filter(
                lambda x: type(x) == dict
                and x.get("@Source", "") == "WikiPathways-description",
                descriptions,
            )
        )
        if len(filtered_descriptions) >= 1:
            description = filtered_descriptions[0]
            description = description.get("#text", "").replace("\n", "")
        else:
            description = ""

        pathway_dict = {
            "resource": "WikiPathways",
            "label": "Pathway",
            "id": f"WikiPathways:{id}",
            "name": pathway.get("name"),
            "synonyms": "",
            "description": description,
            "xrefs": "",
            "taxid": f"{organisms.get(organism)}",
        }

        pathway_dicts.append(pathway_dict)

    return pathway_dicts


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
    for organism in organisms.keys():
        pathway_lst = get_pathway_lst(organism)
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
