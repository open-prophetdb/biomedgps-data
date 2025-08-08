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
    "Phenotype",
    "PharmacologicClass",
    "BiologicalProcess",
    "SideEffect",
    "CellularComponent",
    "MolecularFunction",
]

relation_type_map = {
    "inhibited_by::Gene:Compound": "DGIDB::INHIBITOR::Gene:Compound",
    "increased_by::Gene:Compound": "GNBR::E+::Compound:Gene",
    "increased_by::BiologicalProcess:Disease": None,
    "associated_with::Pathway:Disease": "CTD::IS_ASSOCIATED_WITH::Disease:Pathway",
    "increased_by::Metabolite:Compound": None,
    "associated_with::Pathway:Metabolite": None,
    "reduced_by::Gene:Compound": "GNBR::E-::Compound:Gene",
    "associated_with::Anatomy:Compound": "biolink::related_to::Anatomy:Compound",
    "associated_with::Disease:Gene": "PrimeKG::associated_with::Disease:Gene",
    "increased_by::Gene:Gene": "GNBR::E+::Gene:Gene",
    "activated_by::Pathway:Gene": "PrimeKG::interacts_with::Pathway:Gene",
    "associated_with::Compound:Disease": "CTD::IS_ASSOCIATED_WITH::Compound:Disease",
    "associated_with::Gene:Compound": "INTACT::ASSOCIATION::Compound:Gene",
    "reduced_by::BiologicalProcess:Disease": "biolink::disrupts::Disease:BiologicalProcess",
    "reduced_by::Gene:Disease": "Hetionet::DdG::Disease:Gene",
    "associated_with::Disease:Compound": "CTD::IS_ASSOCIATED_WITH::Compound:Disease",
    "increased_by::Compound:Disease": "GNBR::J::Compound:Disease",
    "induced_by::Disease:Compound": "PrimeKG::indication::Disease:Compound",
    "activated_by::Pathway:Compound": "biolink::participates_in::Compound:Pathway",
    "increased_by::Disease:Compound": "GNBR::J::Compound:Disease",
    "upregulated_in::Gene:Gene": "GNBR::E+::Gene:Gene",
    "alleviated_by::Compound:Disease": "GNBR::Pa::Compound:Disease",
    "associated_with::Phenotype:Disease": "biolink::related_to::Phenotype:Disease",
    "downregulated_in::Gene:Compound": "Hetionet::CdG::Compound:Gene",
    "induced_by::Pathway:Compound": "biolink::participates_in::Compound:Pathway",
    "upregulated_in::Gene:Compound": "Hetionet::CuG::Compound:Gene",
    "inhibited_by::Pathway:Compound": "biolink::participates_in::Compound:Pathway",
    "associated_with::Metabolite:Disease": None,
    "treats::Compound:Pathway": "CTD::IS_ASSOCIATED_WITH::Compound:Pathway",
    "induced_by::Compound:Disease": "PrimeKG::indication::Compound:Disease",
    "associated_with::Disease:Metabolite": None,
    "downregulated_in::Compound:Pathway": "biolink::participates_in::Compound:Pathway",
    "associated_with::BiologicalProcess:Disease": "CTD::IS_ASSOCIATED_WITH::Disease:BiologicalProcess",
    "biomarker::Compound:Disease": "GNBR::Mp::Compound:Disease",
    "reduced_by::Metabolite:Compound": None,
    "associated_with::Gene:Phenotype": "biolink::has_phenotype::Gene:Phenotype",
    "reduced_by::Compound:Gene": "GNBR::A-::Compound:Gene",
    "associated_with::Metabolite:Compound": None,
    "associated_with::BiologicalProcess:Gene": "PrimeKG::interacts_with::Gene:BiologicalProcess",
    "activated_by::Compound:Pathway": "biolink::participates_in::Compound:Pathway",
    "biomarker::Metabolite:Pathway": None,
    "associated_with::Phenotype:Gene":  "biolink::has_phenotype::Gene:Phenotype",
    "biomarker::Metabolite:Disease": None,
    "inhibited_by::BiologicalProcess:Disease": "biolink::disrupts::Disease:BiologicalProcess",
    "associated_with::Anatomy:Disease":None,
    "biomarker::Gene:Disease": "CTD::marker/mechanism|therapeutic::Gene:Disease",
    "associated_with::BiologicalProcess:Compound": "biolink::related_to::BiologicalProcess:Compound",   
    "biomarker::BiologicalProcess:Disease": "biolink::caused_by::Disease:BiologicalProcess",
    "biomarker::CellularComponent:Disease": "biolink::caused_by::Disease:CellularComponent",
    "associated_with::Phenotype:BiologicalProcess": "biolink::related_to::Phenotype:BiologicalProcess",
    "biomarker::Disease:BiologicalProcess": "biolink::caused_by::Disease:BiologicalProcess",
    "associated_with::Pathway:BiologicalProcess": None,
    "associated_with::BiologicalProcess:BiologicalProcess": "biolink::related_to::BiologicalProcess:BiologicalProcess",
    "associated_with::CellularComponent:Disease": None,
    "biomarker::MolecularFunction:Phenotype": "biolink::related_to::Phenotype:MolecularFunction",
    "increased_by::Gene:Disease": "GNBR::X::Gene:Disease",
    "associated_with::BiologicalProcess:Metabolite": None,
    "upregulated_in::Compound:Gene": "Hetionet::CuG::Compound:Gene",
    "treats::Compound:BiologicalProcess": "biolink::related_to::BiologicalProcess:Compound",
    "associated_with::Pathway:Compound": "CTD::IS_ASSOCIATED_WITH::Compound:Pathway",
    "biomarker::BiologicalProcess:Phenotype": "biolink::related_to::Phenotype:BiologicalProcess",
    "associated_with::BiologicalProcess:Anatomy": "biolink::related_to::BiologicalProcess:Anatomy",
    "associated_with::Metabolite:Phenotype": None,
    "associated_with::BiologicalProcess:Phenotype": "biolink::related_to::Phenotype:BiologicalProcess",
    "biomarker::Gene:Phenotype": "biolink::has_phenotype::Gene:Phenotype",
    "treats::Compound:Disease": "DRUGBANK::treats::Compound:Disease",
    "associated_with::Metabolite:BiologicalProcess": None,
    "reduced_by::Disease:Compound": "GNBR::Pa::Compound:Disease",
    "activated_by::Compound:Gene": "CTD::increases^activity::Compound:Gene",
    "associated_with::Gene:BiologicalProcess": "PrimeKG::interacts_with::Gene:BiologicalProcess",
    "treats::Metabolite:Disease": None,
    "treats::Compound:Phenotype": "biolink::related_to::Phenotype:Compound",
    "associated_with::Pathway:Phenotype": None,
    "biomarker::Pathway:Disease": "CTD::IS_ASSOCIATED_WITH::Disease:Pathway",
    "associated_with::Disease:Pathway": "CTD::IS_ASSOCIATED_WITH::Disease:Pathway",
    "associated_with::Disease:Disease": "biolink::related_to::Disease:Disease",
    "associated_with::Gene:Pathway": "CTD::IS_ASSOCIATED_WITH::Gene:Pathway",
    "activated_by::Gene:Compound": "DGIDB::ACTIVATOR::Gene:Compound",
    "associated_with::Disease:BiologicalProcess": "CTD::IS_ASSOCIATED_WITH::Disease:BiologicalProcess",
    "increased_by::Metabolite:Gene": None,
    "alleviated_by::Disease:Compound": "GNBR::Pa::Compound:Disease",
    "increased_by::Pathway:Compound": "CTD::IS_ASSOCIATED_WITH::Compound:Pathway",
    "reduced_by::Metabolite:Disease": None,
    "associated_with::Compound:Compound": "biolink::related_to::Compound:Compound",
    "activated_by::Gene:Gene": "GNBR::V+::Gene:Gene",
    "associated_with::Gene:Disease": "CTD::IS_ASSOCIATED_WITH::Gene:Disease",
    "alleviated_by::Pathway:Compound": "biolink::participates_in::Compound:Pathway",
    "increased_by::Compound:Pathway":"biolink::participates_in::Compound:Pathway",
    "induced_by::Compound:Pathway": "biolink::participates_in::Compound:Pathway",
    "downregulated_in::Compound:Compound": "DRUGBANK::ddi-interactor-in::Compound:Compound",
    "induced_by::Disease:Disease": "biolink::related_to::Disease:Disease",
    "reduced_by::Gene:Pathway": "Hetionet::GpPW::Gene:Pathway",
    "associated_with::Phenotype:Anatomy": "biolink::related_to::Phenotype:Anatomy",
    "inhibited_by::Pathway:Gene": "PrimeKG::interacts_with::Pathway:Gene",
    "increased_by::Compound:Gene": "GNBR::E+::Compound:Gene",
    "upregulated_in::Gene:Disease": "Hetionet::DuG::Disease:Gene",
    "induced_by::BiologicalProcess:Disease": "biolink::caused_by::Disease:BiologicalProcess",
    "associated_with::Gene:Metabolite": None,
    "treats::Metabolite:Phenotype": None,
    "caused_by::Disease:Compound": "PrimeKG::contraindication::Disease:Compound",
    "inhibited_by::Gene:Gene": "STRING::INHIBITION::Gene:Gene",
    "inhibited_by::Pathway:Pathway": None,
    "associated_with::Metabolite:Anatomy": None,
    "biomarker::Gene:Anatomy": "biolink::expressed_in::Gene:Anatomy",
    "activated_by::Disease:Compound": "PrimeKG::indication::Compound:Disease",
    "biomarker::Gene:Compound": "PrimeKG::target::Gene:Compound",
    "associated_with::Gene:Gene": "INTACT::ASSOCIATION::Gene:Gene",
    "alleviated_by::Gene:Disease": "CTD::therapeutic::Gene:Disease",
    "induced_by::Gene:Compound": "DGIDB::ACTIVATOR::Gene:Compound",
    "induced_by::Disease:Metabolite": None,
    "upregulated_in::Pathway:Disease": "CTD::IS_ASSOCIATED_WITH::Disease:Pathway",
    "activated_by::Gene:Pathway": "biolink::participates_in::Gene:Pathway",
    "reduced_by::Compound:Metabolite": None,
    "associated_with::Compound:Anatomy": "biolink::related_to::Anatomy:Compound",
    "inhibited_by::Compound:BiologicalProcess": "biolink::related_to::BiologicalProcess:Compound",
    "upregulated_in::Pathway:Compound": "biolink::participates_in::Compound:Pathway",
    "associated_with::Compound:Pathway": "CTD::IS_ASSOCIATED_WITH::Compound:Pathway",
    "downregulated_in::Pathway:Compound": "biolink::participates_in::Compound:Pathway",
    "reduced_by::Compound:Disease": "GNBR::Pa::Compound:Disease",
    "biomarker::Metabolite:Compound": None,
    "reduced_by::Disease:Gene": "Hetionet::DdG::Disease:Gene",
    "biomarker::Compound:Metabolite":None,
    "increased_by::Phenotype:Gene": "biolink::has_phenotype::Gene:Phenotype",
    "biomarker::Disease:Gene": "CTD::marker/mechanism|therapeutic::Gene:Disease",
    "inhibited_by::Compound:Pathway": "CTD::IS_ASSOCIATED_WITH::Compound:Pathway",
    "increased_by::Phenotype:Disease": "biolink::related_to::Phenotype:Disease",
    "increased_by::Gene:Phenotype": "biolink::has_phenotype::Gene:Phenotype",
    "associated_with::Anatomy:Phenotype": "biolink::related_to::Anatomy:Phenotype",
    "caused_by::Compound:Compound": "DRUGBANK::ddi-interactor-in::Compound:Compound",
    "increased_by::Compound:Phenotype": "biolink::related_to::Phenotype:Compound",
    "associated_with::Phenotype:Phenotype":  "biolink::subclass_of::Phenotype:Phenotype",
    "biomarker::Anatomy:Disease": "biolink::disease_has_location::Disease:Anatomy",
    "reduced_by::Pathway:Disease": "CTD::IS_ASSOCIATED_WITH::Disease:Pathway",
    "increased_by::Metabolite:Disease": None,
    "reduced_by::Metabolite:Phenotype": None,
    "increased_by::Metabolite:Phenotype": None,
    "downregulated_in::Metabolite:Disease": None,
    "caused_by::Gene:Disease": "biolink::contributes_to::Gene:Disease",
    "inhibited_by::Compound:Compound": "DRUGBANK::ddi-interactor-in::Compound:Compound",
    "increased_by::Anatomy:Disease": "biolink::disease_has_location::Disease:Anatomy",
    "associated_with::Compound:CellularComponent": "biolink::related_to::CellularComponent:Compound",
    "induced_by::Phenotype:Disease": "biolink::has_phenotype::Disease:Phenotype",
    "associated_with::Compound:BiologicalProcess": "biolink::related_to::CellularComponent:Compound",
    "induced_by::Pathway:BiologicalProcess": None,
    "induced_by::Compound:BiologicalProcess": "biolink::related_to::BiologicalProcess:Compound",
    "increased_by::Compound:BiologicalProcess": "biolink::related_to::BiologicalProcess:Compound",
    "inhibited_by::Disease:Compound": "GNBR::Pa::Compound:Disease",
    "activated_by::Disease:Pathway": "CTD::IS_ASSOCIATED_WITH::Disease:Pathway",
    "associated_with::Compound:Gene": "INTACT::ASSOCIATION::Compound:Gene",
    "Unknown::Gene:Compound": None,
    "increased_by::Compound:Compound": "DRUGBANK::ddi-interactor-in::Compound:Compound",
    "induced_by::BiologicalProcess:Compound": "biolink::related_to::BiologicalProcess:Compound",
    "associated_with::Compound:Phenotype": "biolink::related_to::Phenotype:Compound",
    "biomarker::Phenotype:BiologicalProcess": "biolink::related_to::Phenotype:BiologicalProcess",
    "reduced_by::Metabolite:Pathway": None,
    "associated_with::Gene:Anatomy": "biolink::related_to::Anatomy:Protein",
    "treats::BiologicalProcess:Compound": "biolink::related_to::BiologicalProcess:Compound",
}


@click.command(help="Format the relation types for the customdb")
@click.option("--input-file", "-i", help="Input file path", required=True)
@click.option("--output-file", "-o", help="Output file path", required=True)
def format_customdb(input_file, output_file):
    df = pd.read_csv(input_file, sep="\t")
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
    df["resource"] = "CustomDB"

    print(f"Total relations: {df.shape[0]}")
    df = df.drop(columns=["idx"])
    df.to_csv(output_file, index=False, sep="\t")


if __name__ == "__main__":
    format_customdb()
