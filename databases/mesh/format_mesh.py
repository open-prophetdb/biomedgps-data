import click
import re
import os
import pandas as pd

cli = click.Group()


@cli.command(help="Parse the mesh ontology")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def entities(input, output):
    # Read a csv.gz file and convert it to a data frame
    df = pd.read_csv(
        input, compression="gzip", header=0, sep=",", quotechar='"', dtype=str
    )

    # Fill the nan values with empty string
    df = df.fillna("")

    # Select only the columns that we need
    df = df[
        ["Class ID", "Preferred Label", "Synonyms", "Definitions", "Semantic Types"]
    ]

    # Format the id column by using regex to replace the ".*MESH/" prefix with "MESH:". Must use the regex pattern
    df.loc[:, "Class ID"] = df["Class ID"].apply(
        lambda x: re.sub(r".*MESH/", "MESH:", x)
    )

    # Rename the columns
    df = df.rename(
        columns={
            "Class ID": "id",
            "Preferred Label": "name",
            "Synonyms": "synonyms",
            "Definitions": "description",
            "Semantic Types": "semantic_types",
        }
    )

    # Format the semantic_types column
    df.loc[:, "semantic_types"] = df["semantic_types"].apply(
        lambda x: "|".join(map(lambda y: re.sub(r".*STY/", "", y), x.split("|")))
    )

    # Preferred label map, I need to collect the disease, symptom, anatomy, compound, gene, pathway, pharmacologic class, side effect, molecular function, biological process, cellular component etc.
    label_map = {
        # More details on https://bioportal.bioontology.org/ontologies/STY/
        # Disease
        "T047": ["Disease or Syndrome", "Disease"],
        "T191": ["Neoplastic Process", "Disease"],
        "T050": ["Experimental Model of Disease", "Disease"],
        "T048": ["Mental or Behavioral Dysfunction", "Disease"],
        "T049": ["Cell or Molecular Dysfunction", "Disease"],
        "T046": ["Pathologic Function", "Disease"],
        "T190": ["Anatomical Abnormality", "Disease"],
        "T020": ["Acquired Abnormality", "Disease"],
        "T019": ["Congenital Abnormality", "Disease"],
        # Anatomy
        "T018": ["Embryonic Structure", "Anatomy"],
        "T023": ["Body Part, Organ, or Organ Component", "Anatomy"],
        "T024": ["Tissue", "Anatomy"],
        "T025": ["Cell", "Anatomy"],
        # Compound
        "T103": ["Compound", "Compound"],
        "T120": ["Compound Viewed Functionally", "Compound"],
        "T123": ["Biologically Active Substance", "Compound"],
        "T126": ["Enzyme", "Compound"],
        "T125": ["Hormone", "Compound"],
        "T129": ["Immunologic Factor", "Compound"],
        "T192": ["Receptor", "Compound"],
        "T127": ["Vitamin", "Compound"],
        "T122": ["Biomedical or Dental Material", "Compound"],
        "T131": ["Hazardous or Poisonous Substance", "Compound"],
        "T130": ["Indicator, Reagent, or Diagnostic Aid", "Compound"],
        "T121": ["Pharmacologic Substance", "Compound"],
        "T195": ["Antibiotic", "Compound"],
        "T104": ["Compound Viewed Structurally", "Compound"],
        "T196": ["Element, Ion, or Isotope", "Compound"],
        "T197": ["Inorganic Compound", "Compound"],
        "T109": ["Organic Compound", "Compound"],
        "T116": ["Amino Acid, Peptide, or Protein", "Compound"],
        "T114": ["Nucleic Acid, Nucleoside, or Nucleotide", "Compound"],
    }

    # Add resource column
    df["resource"] = "MESH"

    def keep(lst):
        lst = list(lst)
        if len(lst) == 0:
            return "Unknown"
        else:
            if "Disease" in lst:
                return "Disease"
            elif "Anatomy" in lst:
                return "Anatomy"
            elif "Compound" in lst:
                return "Compound"
            else:
                return "Unknown"
            
    print("Several semantic types are created: %s" % df)

    # Add a new column based on the category column
    df["label"] = df["semantic_types"].apply(
        # Any matched semantic type will be used as the label
        lambda x: keep(
            map(
                lambda y: label_map[y][1] if "%s" % y in label_map.keys() else "Unknown",
                x.split("|"),
            )
        )
    )

    grouped = df.groupby("label")
    print("Several groups are created: %s" % grouped.groups.keys())
    for label in grouped.groups.keys():
        if label == "Unknown":
            continue

        data = grouped.get_group(label)
        outputfile = os.path.join(output, "mesh_%s.tsv" % label.lower())
        # Write the data frame to a tsv file
        print("\tWriting to %s" % outputfile)
        data.to_csv(outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
