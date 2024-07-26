# Standard library packages
import os
import sys
import logging
import click


script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
# print("Script dir: {}, sys.path: {}".format(script_dir, sys.path))
from lib.data import batch_convert_id_to_umls, intall_cache
import pandas as pd

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("format_meddra.py")
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
@click.option(
    "--cache-file",
    "-c",
    default=None,
    help="A cache file to store the results of the API calls",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def extract(input, output, cache_file):
    if cache_file:
        cached_session = intall_cache(cache_file, enable_threading=True)
    else:
        cached_session = None

    sep = input.endswith("tsv") and "\t" or ","
    sideeffect_df = pd.read_csv(input, sep=sep, dtype=str)
    # An example id is MedDRA:10000001, we want to extract the number part
    sideeffect_ids = sideeffect_df["id"].apply(lambda x: x.split(":")[1]).tolist()
    print("Found {} MedDra items.".format(len(sideeffect_ids)))

    xrefs = batch_convert_id_to_umls(
        sideeffect_ids,
        cached_session=cached_session,
        id_type="MEDDRA",
        api_key="00cad330-6151-4552-9c3a-a94710e7a343",
    )

    sideeffect_df["xrefs"] = sideeffect_df["id"]
    sideeffect_df["id"] = xrefs
    sideeffect_df["label"] = "SideEffect"
    sideeffect_df["description"] = ""
    sideeffect_df["taxid"] = ""
    sideeffect_df["pmids"] = ""
    sideeffect_df["synonyms"] = ""

    sideeffect_df = sideeffect_df[sideeffect_df["id"] != ""]
    sideeffect_df = sideeffect_df[
        [
            "id",
            "name",
            "label",
            "resource",
            "xrefs",
            "synonyms",
            "description",
            "taxid",
            "pmids",
        ]
    ]
    print("Found {} MedDra items with UMLS xrefs".format(len(sideeffect_df)))

    sideeffect_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    extract()
