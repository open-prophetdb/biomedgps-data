# Standard library packages
import os
import sys
import logging
import click
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
# print("Script dir: {}, sys.path: {}".format(script_dir, sys.path))
from lib.data import convert_id_to_umls, intall_cache
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

    sideeffect_df = pd.read_csv(input, sep="\t", dtype=str)
    # An example id is MEDDRA:10000001, we want to extract the number part
    sideeffect_ids = sideeffect_df["id"].apply(lambda x: x.split(":")[1]).tolist()
    print("Found {} side effects".format(len(sideeffect_ids)))

    xrefs_dict = {}

    def convert_id_and_append(id):
        umls_id = convert_id_to_umls(
            id,
            id_type="MEDDRA",
            api_key="00cad330-6151-4552-9c3a-a94710e7a343",
            cached_session=cached_session,
        )
        if umls_id:
            return {id: f"UMLS:{umls_id}"}
        else:
            return {id: ""}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(convert_id_and_append, id) for id in sideeffect_ids]

        for future in tqdm(
            as_completed(futures), total=len(sideeffect_ids), desc="Processing IDs"
        ):
            xrefs_dict.update(future.result())

    xrefs = [xrefs_dict[id] for id in sideeffect_ids]
    sideeffect_df["xrefs"] = sideeffect_df["id"]
    sideeffect_df["id"] = xrefs
    sideeffect_df = sideeffect_df.rename(
        {
            "id": "id",
            "name": "name",
            "label": "label",
            "resource": "resource",
            "description": "",
            "xrefs": "xrefs",
            "taxid": "",
            "pmids": "",
        }
    )

    sideeffect_df = sideeffect_df[sideeffect_df["id"] != ""]
    print("Found {} side effects with UMLS xrefs".format(len(sideeffect_df)))

    sideeffect_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    extract()
