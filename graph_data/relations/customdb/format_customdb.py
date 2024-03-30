import click
import pandas as pd

valid_entity_types = [
    "Compound",
    "Disease",
    "Gene",
    "Metabolite",
    "Pathway",
    "Anatomy",
    "Symptom",
    "PharmacologicClass",
    "BiologicalProcess",
    "SideEffect",
    "CellularComponent",
    "MolecularFunction",
]

relation_type_map = {
    "increased_by::BiologicalProcess:Disease": "BioMedGPS::E+::Disease:BiologicalProcess",
    "associated_with::Pathway:Disease": "BioMedGPS::AssociatedWith::Pathway:Disease",
    "reduced_by::BiologicalProcess:Disease": "BioMedGPS::E-::Disease:BiologicalProcess",
    "reduced_by::Gene:Disease": "Hetionet::DdG::Disease:Gene",
    "associated_with::Compound:Disease": "GNBR::C::Compound:Disease",
    "associated_with::Symptom:Disease": "HSDN::has_symptom::Disease:Symptom",
    "associated_with::Metabolite:Disease": "BioMedGPS::AssociatedWith::Metabolite:Disease",
    "associated_with::BiologicalProcess:Disease": "BioMedGPS::AssociatedWith::BiologicalProcess:Disease",
    "biomarker::Compound:Disease": "GNBR::Mp::Compound:Disease",
    "biomarker::Metabolite:Disease": "BioMedGPS::Biomarker::Metabolite:Disease",
    "inhibited_by::BiologicalProcess:Disease": "BioMedGPS::E-::Disease:BiologicalProcess",
    "associated_with::Anatomy:Disease": "Hetionet::Aa::Anatomy:Disease",
    "biomarker::Gene:Disease": "GNBR::Md::Gene:Disease",
    "biomarker::BiologicalProcess:Disease": None,
    "biomarker::CellularComponent:Disease": None,
    "biomarker::Disease:BiologicalProcess": None,
    "associated_with::CellularComponent:Disease": "BioMedGPS::AssociatedWith::CellularComponent:Disease",
    "treats::Compound:Disease": "DRUGBANK::treats::Compound:Disease",
    "treats::Metabolite:Disease": "DRUGBANK::treats::Metabolite:Disease",
    "associated_with::Disease:Compound": "GNBR::C::Compound:Disease",
    "biomarker::Pathway:Disease": "BioMedGPS::AssociatedWith::Pathway:Disease",
    "associated_with::Disease:BiologicalProcess": "BioMedGPS::AssociatedWith::Disease:BiologicalProcess",
    "reduced_by::Metabolite:Disease": "BioMedGPS::E-::Disease:Metabolite",
    "induced_by::BiologicalProcess:Disease": "BioMedGPS::E+::Disease:BiologicalProcess",
    "increased_by::Symptom:Disease": "HSDN::has_symptom::Disease:Symptom",
    "biomarker::Anatomy:Disease": None,
    "reduced_by::Pathway:Disease": "BioMedGPS::E-::Disease:Pathway",
    "increased_by::Metabolite:Disease": "BioMedGPS::E+::Disease:Metabolite",
    "downregulated_in::Metabolite:Disease": "BioMedGPS::E-::Disease:Metabolite",
    "increased_by::Anatomy:Disease": None,
    "reduced_by::Compound:Disease": "GNBR::C::Compound:Disease",
}


@click.command(help="Format the relation types for the customdb")
@click.option("--input-file", "-i", help="Input file path", required=True)
@click.option("--output-file", "-o", help="Output file path", required=True)
def format_customdb(input_file, output_file):
    df = pd.read_csv(input_file, sep=",")
    # Filter all the rows with Unknown:Unknown values in the target_id or source_id columns
    df = df[~df["target_id"].str.contains("Unknown:Unknown")]
    df = df[~df["source_id"].str.contains("Unknown:Unknown")]
    df["idx"] = df.index

    # Join the source_type, target_type and relation_type columns
    valid_relations = df[
        df["relation_type"].str.contains(".*:+[a-zA-Z]+:[a-zA-Z]+$", regex=True)
        & (
            df["source_type"].apply(lambda x: x in valid_entity_types)
            & df["target_type"].apply(lambda x: x in valid_entity_types)
        )
    ]
    print(f"Valid relations: {valid_relations.shape[0]}")
    invalid_relations = df[df["idx"].apply(lambda x: x not in valid_relations.index)]
    print(f"Invalid relations: {invalid_relations.shape[0]}")

    invalid_relations = invalid_relations.copy()
    # Replace 'Protein' with 'Gene' in 'source_type' and 'target_type' columns
    invalid_relations["source_type"] = invalid_relations["source_type"].replace(
        "Protein", "Gene"
    )
    invalid_relations["target_type"] = invalid_relations["target_type"].replace(
        "Protein", "Gene"
    )

    # Remove all rows which have a invalid source_type or target_type
    invalid_relations = invalid_relations[
        (invalid_relations["source_type"].apply(lambda x: x in valid_entity_types))
        & (invalid_relations["target_type"].apply(lambda x: x in valid_entity_types))
    ].copy()

    print(f"Invalid relations need to be fixing: {invalid_relations.shape[0]}")

    invalid_relations["relation_type"] = invalid_relations.apply(
        lambda x: x["relation_type"] + "::" + x["source_type"] + ":" + x["target_type"],
        axis=1,
    )

    # Format all relation types
    invalid_relations["relation_type"] = invalid_relations["relation_type"].apply(
        lambda x: relation_type_map.get(x, None)
    )
    invalid_relations = invalid_relations.dropna(subset=["relation_type"])

    print(f"Fixed relations: {invalid_relations.shape[0]}")

    # Concatenate the valid and fixed relations
    df = pd.concat([valid_relations, invalid_relations])

    print(f"Total relations: {df.shape[0]}")
    df = df.drop(columns=["idx"])
    df.to_csv(output_file, index=False, sep="\t")


if __name__ == "__main__":
    format_customdb()
