import pandas as pd
import os
import click

cli = click.Group()

def parse_obo(file_path):
    with open(file_path, 'r') as file:
        obo_data = file.read()

    entries = obo_data.split("[Term]")
    parsed_data = []

    for entry in entries[1:]:  # Skip the first split part as it doesn't contain a term
        lines = entry.strip().split('\n')
        if "HP:0000001" in lines[0]:
            continue

        term_data = {
            "id": None,
            "name": None,
            "label": "Phenotype",
            "description": None,
            "xrefs": [],
            "synonyms": []
        }
        for line in lines:
            if line.startswith("id: "):
                term_data["id"] = line.replace("id: ", "").strip()
            elif line.startswith("name: "):
                term_data["name"] = line.replace("name: ", "").strip()
            elif line.startswith("def: "):
                if term_data["description"] is None:
                    term_data["description"] = line.split('"')[1]
                else:
                    term_data["description"] += " " + line.split('"')[1]
            elif line.startswith("alt_id: "):
                term_data["xrefs"].append(line.replace("alt_id: ", "").strip())
            elif line.startswith("synonym: "):
                synonym = line.split('"')[1]
                term_data["synonyms"].append(synonym)
            elif line.startswith("xref: "):
                xref = line.split(' ')[1]
                term_data["xrefs"].append(xref.replace("_US", ""))
            elif line.startswith("comment: "):
                if term_data["description"] is None:
                    term_data["description"] = line.replace("comment: ", "").strip()
                else:
                    term_data["description"] += " " + line.replace("comment: ", "").strip()

        term_data["xrefs"] = '|'.join(term_data["xrefs"])
        term_data["synonyms"] = '|'.join(term_data["synonyms"])
        term_data["resource"] = "HPO"
        term_data["pmids"] = None
        parsed_data.append(term_data)

    return parsed_data


@cli.command(help="Parse the hpo ontology")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def entities(input, output):
    hpo_obo = parse_obo(input)
    df = pd.DataFrame(hpo_obo)
    outputfile = os.path.join(output, "hpo_phenotype.tsv")
    main_df = df[
        ["id", "name", "description", "label", "resource", "xrefs", "pmids", "synonyms"]
    ]
    # Write the data frame to a tsv file
    main_df.to_csv(outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
