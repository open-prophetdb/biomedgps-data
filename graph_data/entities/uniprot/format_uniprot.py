import xml.etree.ElementTree as ET
import click
import pandas as pd
import os
import json


cli = click.Group()


def filter_sequences(input_xml, output_xml):
    tree = ET.parse(input_xml)
    root = tree.getroot()

    # Define namespaces
    namespaces = {"ns": "http://uniprot.org/uniprot"}

    # Define the target species
    target_species = {
        "9606": "Homo sapiens",  # Human
        "10090": "Mus musculus",  # Mouse
        "10116": "Rattus norvegicus",  # Rat
    }

    # Create a new XML tree for the output
    output_root = ET.Element(
        "uniprot",
        {
            "xmlns": "http://uniprot.org/uniprot",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://uniprot.org/uniprot http://www.uniprot.org/docs/uniprot.xsd",
        },
    )

    # Iterate through each entry
    for entry in root.findall("ns:entry", namespaces):
        for organism in entry.findall("ns:organism", namespaces):
            for db_reference in organism.findall("ns:dbReference", namespaces):
                if db_reference.attrib.get("id") in target_species:
                    # Remove the ns0 namespace
                    for elem in entry.iter():
                        elem.tag = elem.tag.split("}", 1)[-1]
                    output_root.append(entry)
                    break

    # Write the filtered entries to the output XML file
    tree = ET.ElementTree(output_root)
    tree.write(output_xml, encoding="utf-8", xml_declaration=True)


def extract_fields_from_entry(entry):
    namespaces = {"ns": "http://uniprot.org/uniprot"}

    dataset = entry.attrib.get("dataset", "")
    created = entry.attrib.get("created", "")
    modified = entry.attrib.get("modified", "")
    version = entry.attrib.get("version", "")

    # Extract accession
    accessions = entry.findall("ns:accession", namespaces)
    id = f"Uniprot:{accessions[0].text}" if accessions else ""
    xrefs = [f"Uniprot:{acc.text}" for acc in accessions[1:]]

    # Extract name
    name = (
        entry.find("ns:name", namespaces).text
        if entry.find("ns:name", namespaces) is not None
        else ""
    )

    # Extract description
    description = entry.find("ns:protein/ns:recommendedName/ns:fullName", namespaces)
    description = description.text if description is not None else ""

    # Extract gene names
    gene_names = [gene.text for gene in entry.findall("ns:gene/ns:name", namespaces)]
    if gene_names:
        xrefs.extend(gene_names)

    # Extract organism ID
    organism = entry.find(
        "ns:organism/ns:dbReference[@type='NCBI Taxonomy']", namespaces
    )
    organism_id = organism.attrib.get("id") if organism is not None else ""

    # Extract dbReferences
    for db_ref in entry.findall("ns:dbReference", namespaces):
        db_type = db_ref.attrib.get("type")
        db_id = db_ref.attrib.get("id")
        if db_type and db_id:
            xrefs.append(f"{db_type}:{db_id}")

    xrefs_str = "|".join(xrefs)

    # Extract PMIDs
    pmids = [
        citation.attrib.get("id")
        for citation in entry.findall(
            "ns:reference/ns:citation[@type='journal article']/ns:dbReference[@type='PubMed']",
            namespaces,
        )
    ]
    pmids_str = "|".join(pmids)

    return {
        "dataset": dataset,
        "created": created,
        "modified": modified,
        "version": version,
        # Required fields
        "id": id,
        "name": name,
        "description": description,
        "label": "Protein",
        "resource": "Uniprot",
        "xrefs": xrefs_str,
        "pmids": pmids_str,
        "synonyms": "",
        "taxid": organism_id,
    }


def parse_and_extract(input_xml: str) -> pd.DataFrame:
    tree = ET.parse(input_xml)
    root = tree.getroot()

    extracted_data = []
    for entry in root.findall("{http://uniprot.org/uniprot}entry"):
        entry_data = extract_fields_from_entry(entry)
        extracted_data.append(entry_data)

    return pd.DataFrame(extracted_data)


@cli.command(help="Filter uniprot items with specified species.")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output file path")
def filter(input, output):
    if not os.path.isfile(input):
        raise FileNotFoundError(f"Input file '{input}' not found")
    
    if os.path.exists(output):
        raise FileExistsError(f"Output file '{output}' already exists")

    filter_sequences(input, output)


@cli.command(help="Extract uniprot fields and write to a tsv file.")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def entities(input, output):
    if not os.path.isfile(input):
        raise FileNotFoundError(f"Input file '{input}' not found")

    if not os.path.exists(output):
        raise FileNotFoundError(f"Output directory '{output}' not found")

    df = parse_and_extract(input)
    outputfile = os.path.join(output, "uniprot_protein.tsv")
    main_df = df[
        ["id", "name", "description", "label", "resource", "xrefs", "pmids", "synonyms", "taxid"]
    ]

    # Remove all unexpected empty characters, such as leading and trailing spaces
    main_df["description"] = main_df["description"].fillna("")
    main_df["description"] = main_df["description"].apply(
        lambda x: " ".join(x.strip().split())
    )

    # additional_df = df[["id", "dataset", "created", "modified", "version"]]
    # Write the data frame to a tsv file
    main_df.to_csv(outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
