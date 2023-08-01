import click
import pandas as pd

# Disable SettingWithCopyWarning
pd.options.mode.chained_assignment = None


@click.command(help="Extract entities from HGNC & MGI file")
@click.option(
    "--hgnc",
    "-h",
    required=True,
    help="HGNC file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--mgi",
    "-m",
    required=True,
    help="MGI file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="Output file",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def main(hgnc, mgi, output):
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

    # Filter invalid rows
    # 1. Remove rows with empty name
    selected_hgnc_df = selected_hgnc_df[selected_hgnc_df["name"].notna()]
    # 2. Remove rows with empty id
    selected_hgnc_df = selected_hgnc_df[selected_hgnc_df["id"].notna()]
    # 3. Deduplicate rows
    selected_hgnc_df.drop_duplicates(subset=["id"], keep="first", inplace=True)

    # MGI
    name_dict = {
        "1. MGI accession id": "mgi_id",
        "2. marker type": "marker_type",
        "3. marker symbol": "symbol",
        "4. marker name": "name",
        "5. genome build": "genome_build",
        "6. Entrez gene id": "entrez_id",
        "7. NCBI gene chromosome": "ncbi_gene_chromosome",
        "8. NCBI gene start": "ncbi_gene_start",
        "9. NCBI gene end": "ncbi_gene_end",
        "10. NCBI gene strand": "ncbi_gene_strand",
        "11. Ensembl gene id": "ensembl_gene_id",
        "12. Ensembl gene chromosome": "ensembl_gene_chromosome",
        "13. Ensembl gene start": "ensembl_gene_start",
        "14. Ensembl gene end": "ensembl_gene_end",
        "15. Ensembl gene strand": "ensembl_gene_strand",
    }

    # Read MGI file
    mgi_df = pd.read_csv(mgi, sep="\t", dtype=str, index_col=False)

    # Rename columns
    mgi_df.rename(columns=name_dict, inplace=True)

    expected_column_names = ["mgi_id", "symbol", "name", "entrez_id", "ensembl_gene_id"]

    selected_mgi_df = mgi_df[expected_column_names]

    # Add a column called label
    selected_mgi_df["label"] = "Gene"

    # Add a column called resource
    selected_mgi_df["resource"] = "MGI"

    # Rename name to description
    selected_mgi_df.rename(columns={"name": "description"}, inplace=True)

    # Rename symbol to name
    selected_mgi_df.rename(columns={"symbol": "name"}, inplace=True)

    # Merge mgi_id and ensembl_gene_id into one column called xrefs
    selected_mgi_df["xrefs"] = selected_mgi_df[["mgi_id", "ensembl_gene_id"]].apply(
        lambda x: "|".join(x.dropna().astype(str)), axis=1
    )
    selected_mgi_df.drop(["mgi_id", "ensembl_gene_id"], axis=1, inplace=True)

    # Rename entrez_id to id and add a ENTREZ prefix
    selected_mgi_df.rename(columns={"entrez_id": "id"}, inplace=True)
    selected_mgi_df["id"] = "ENTREZ:" + selected_mgi_df["id"]

    # Filter invalid rows
    # 1. Remove rows with empty name
    selected_mgi_df = selected_mgi_df[selected_mgi_df["name"].notna()]
    # 2. Remove rows with empty id
    selected_mgi_df = selected_mgi_df[selected_mgi_df["id"].notna()]
    # 3. Deduplicate rows
    selected_mgi_df.drop_duplicates(subset=["id"], keep="first", inplace=True)

    # Merge HGNC and MGI
    merged_df = pd.concat([selected_hgnc_df, selected_mgi_df], ignore_index=True)

    # Remove duplicated rows
    print("Total number of rows before removing duplicated rows: {}".format(len(merged_df)))
    merged_df.drop_duplicates(subset=["id"], keep="first", inplace=True)
    print("Total number of rows after removing duplicated rows: {}".format(len(merged_df)))

    # Reorder columns
    merged_df = merged_df[
        [
            "id",
            "name",
            "label",
            "description",
            "xrefs",
            "synonyms",
            "pmids",
            "resource",
        ]
    ]

    # Write to file
    merged_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
