# Standard library packages
import os
import sys
import logging
import click

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
# print("Script dir: {}, sys.path: {}".format(script_dir, sys.path))
from lib.data import convert_id_to_umls
import pandas as pd

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("format_wikipathways.py")
logging.basicConfig(level=logging.INFO, format=fmt)


@click.command(help="Extract entities from meddra data file.")
@click.option(
    "--input",
    "-i",
    required=True,
    help="Input file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="Output file",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def extract(input, output):
    sideeffect_df = pd.read_csv(input, sep="\t", dtype=str)
    # An example id is MEDDRA:10000001, we want to extract the number part
    sideeffect_ids = sideeffect_df["id"].apply(lambda x: x.split(":")[1]).tolist()
    print("Found {} side effects".format(len(sideeffect_ids)))

    xrefs = []
    for id in sideeffect_ids:
        umls_id = convert_id_to_umls(id, id_type="MEDDRA", api_key="00cad330-6151-4552-9c3a-a94710e7a343")
        if umls_id:
            xrefs.append(f"UMLS:{umls_id}")
        else:
            xrefs.append("")

    sideeffect_df["xrefs"] = sideeffect_df["id"]
    sideeffect_df["id"] = xrefs
    sideeffect_df = sideeffect_df.rename({
        "id": "id",
        "name": "name",
        "label": "label",
        "resource": "resource",
        "description": "",
        "xrefs": "xrefs",
        "taxid": "",
        "pmids": "",
    })

    sideeffect_df = sideeffect_df[sideeffect_df["id"] != ""]
    print("Found {} side effects with UMLS xrefs".format(len(sideeffect_df)))

    sideeffect_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    extract()
