import click
import logging
import pandas as pd

fmt = "%(asctime)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s"
logger = logging.getLogger("format_hgnc.py")
logging.basicConfig(level=logging.INFO, format=fmt)

# Disable SettingWithCopyWarning
pd.options.mode.chained_assignment = None


@click.command(help="Extract entities from HGNC file")
@click.option(
    "--hgnc",
    "-h",
    required=True,
    help="HGNC file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="Output file",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def main(hgnc, output):
    hgnc_df = pd.read_csv(hgnc, sep="\t", dtype=str, index_col=False)

    # HGNC
    hgnc_column_names = [
        "hgnc_id",
        "ensembl_gene_id",
        "symbol",
        "name",
        "entrez_id",
        "alias_symbol",
        "alias_name",
        "prev_symbol",
        "prev_name",
        "pubmed_id",
    ]

    selected_hgnc_df = hgnc_df[hgnc_column_names]
    # Merge the alias_symbol, alias_name, prev_symbol, prev_name columns into one column
    selected_hgnc_df["synonyms"] = selected_hgnc_df[
        ["alias_symbol", "alias_name", "prev_symbol", "prev_name"]
    ].apply(lambda x: ",".join(x.dropna().astype(str)), axis=1)
    selected_hgnc_df.drop(
        ["alias_symbol", "alias_name", "prev_symbol", "prev_name"], axis=1, inplace=True
    )

    # Rename pubmed_id to pmids
    selected_hgnc_df.rename(columns={"pubmed_id": "pmids"}, inplace=True)

    # Rename entrez_id to id and add a ENTREZ prefix
    selected_hgnc_df.rename(columns={"entrez_id": "id"}, inplace=True)
    selected_hgnc_df["id"] = "ENTREZ:" + selected_hgnc_df["id"]

    # Merge hgnc_id and ensembl_gene_id into one column called xrefs
    selected_hgnc_df["xrefs"] = selected_hgnc_df[["hgnc_id", "ensembl_gene_id"]].apply(
        lambda x: "|".join(x.dropna().astype(str)), axis=1
    )
    selected_hgnc_df.drop(["hgnc_id", "ensembl_gene_id"], axis=1, inplace=True)

    # Rename name to description
    selected_hgnc_df.rename(columns={"name": "description"}, inplace=True)

    # Rename symbol to name
    selected_hgnc_df.rename(columns={"symbol": "name"}, inplace=True)

    # Add a column called label
    selected_hgnc_df["label"] = "Gene"

    # Add a column called resource
    selected_hgnc_df["resource"] = "HGNC"

    selected_hgnc_df["taxid"] = "9606"

    # Filter invalid rows
    # 1. Remove rows with empty name
    selected_hgnc_df = selected_hgnc_df[selected_hgnc_df["name"].notna()]
    # 2. Remove rows with empty id
    selected_hgnc_df = selected_hgnc_df[selected_hgnc_df["id"].notna()]
    # 3. Deduplicate rows
    selected_hgnc_df.drop_duplicates(subset=["id"], keep="first", inplace=True)

    # Remove duplicated rows
    logger.info(
        "Total number of rows before removing duplicated rows: {}".format(
            len(selected_hgnc_df)
        )
    )
    selected_hgnc_df.drop_duplicates(subset=["id"], keep="first", inplace=True)
    logger.info(
        "Total number of rows after removing duplicated rows: {}".format(
            len(selected_hgnc_df)
        )
    )

    # Reorder columns
    merged_df = selected_hgnc_df[
        [
            "id",
            "name",
            "label",
            "description",
            "xrefs",
            "synonyms",
            "pmids",
            "resource",
            "taxid",
        ]
    ]

    # Write to file
    merged_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
