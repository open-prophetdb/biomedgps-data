import csv
import os
import click
import warnings
import logging
import colorlog
import polars as pl


def is_library_imported(library_name):
    """Check if a library is imported.
    """
    return library_name in globals()


# Use a colorful log format
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])


class BaseExtractor:
    def __init__(self, basedir=".", output_dir=".") -> None:
        self.database_name = "CTD"
        self.basedir = basedir
        self.output_dir = output_dir

    def _load_data(self):
        if not hasattr(self, "filepath"):
            raise ValueError(
                "The subclass should have a self.filepath attribute.")

        self.headers = self._find_fields(self.filepath)
        logging.info("Found headers %s in %s" % (self.headers, self.filepath))
        self.data = self._read_data(self.filepath, self.headers)
        logging.info("Read %s rows from %s." %
                     (self.data.shape[0], self.filepath))

    def _check_file_exists(self, filepath):
        """Check if a file exists.
        """
        return os.path.exists(filepath)

    def write(self, df, output_file, sep="\t"):
        """Write the extracted entities to a csv file.
        """
        outputpath = os.path.join(self.output_dir, output_file)
        df.write_csv(outputpath, separator=sep)
        logging.info(
            "Done! The extracted entities are saved in %s.\n" % outputpath)

    def _read_data(self, csv_file, headers=[]):
        """Skip rows that start with '#' in a csv file.
        """
        sep = "," if csv_file.endswith(".csv") else "\t"
        df = pl.read_csv(csv_file, has_header=False, infer_schema_length=0,
                         new_columns=headers, comment_char='#', separator=sep)

        return df

    def _find_fields(self, csv_file):
        """Find the columns that contain a certain field.
        """
        with open(csv_file, newline='') as csvfile:
            sep = "," if csv_file.endswith(".csv") else "\t"
            reader = csv.reader(csvfile, delimiter=sep)

            fields = []
            for line in reader:
                content = line[0]
                if content.startswith("# Fields:"):
                    header = next(reader)
                    fields = [field.strip("# ") for field in header]
                    break

            return fields


class EntityExtractor(BaseExtractor):
    def __init__(self, entity_type, basedir=".", output_dir=".") -> None:
        super().__init__(basedir, output_dir)

        self.default_entities = {
            "Anatomy": "CTD_anatomy.csv",
            "Compound": "CTD_chemicals.csv",
            "Gene": "CTD_genes.csv",
            "Disease": "CTD_diseases.csv",
            "Pathway": "CTD_pathways.csv",
            "BiologicalProcess": "CTD_chem_go_enriched.csv",
            "CellularComponent": "CTD_chem_go_enriched.csv",
            "MolecularFunction": "CTD_chem_go_enriched.csv",
        }

        if entity_type not in self.default_entities.keys():
            raise ValueError(f"Entity type {entity_type} not supported.")

        self.entity_type = entity_type
        self.filepath = os.path.join(
            self.basedir, self.default_entities[entity_type])

        if self._check_file_exists(self.filepath) is False:
            self.filepath = self.filepath.replace(".csv", ".tsv")

        if self._check_file_exists(self.filepath) is False:
            raise ValueError(f"File {self.filepath}/.tsv not found.")

    def extract(self):
        """Extract entities from the data.
        """
        # TODO: Add dtype for some columns, now it's string by default.
        self._load_data()

        entity_type = self.entity_type.lower()
        method_name = f"_extract_{entity_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(self.data)
        else:
            raise ValueError(f"Entity type {entity_type} not supported.")

    def _extract_entity(self, df, default_extracted_columns, renamed_columns, label):
        for column in default_extracted_columns:
            if column not in df.columns:
                raise ValueError(
                    f"Column {column} not found in the dataframe.")

        df = df.select(default_extracted_columns)
        df = df.rename({old: new
                        for old, new in zip(default_extracted_columns, renamed_columns)})
        new_df = pl.DataFrame(
            {
                "label": [label] * df.shape[0],
                "resource": [self.database_name] * df.shape[0],
            }
        )
        df = df.hstack(new_df)

        logging.info("Extract %s valid entities from %s..." %
                     (df.shape[0], self.filepath))
        df = df.unique()
        logging.warning(
            "Drop duplicates, and %s entities are left." % df.shape[0])

        return df

    def _extract_anatomy(self, df):
        """Extract anatomy entities from CTD_anatomy.csv
        """
        default_extracted_columns = ["AnatomyID", "AnatomyName", "Definition"]
        renamed_columns = ["id", "name", "description"]
        label = "Anatomy"

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)

    def _extract_compound(self, df):
        """Extract compound entities from CTD_chemicals.csv
        """
        default_extracted_columns = [
            "ChemicalID", "ChemicalName", "Definition"]
        renamed_columns = ["id", "name", "description"]
        label = "Compound"

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)

    def _extract_gene(self, df):
        """Extract gene entities from CTD_genes.csv
        """
        default_extracted_columns = ["GeneID", "GeneSymbol", "GeneName", "Synonyms"]
        renamed_columns = ["id", "name", "description", "synonyms"]
        label = "Gene"
        df = df.with_columns(pl.col("GeneID").apply(lambda x: "ENTREZ:" + x))

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)

    def _extract_disease(self, df):
        """Extract disease entities from CTD_diseases.csv
        """
        default_extracted_columns = ["DiseaseID", "DiseaseName", "Definition"]
        renamed_columns = ["id", "name", "description"]
        label = "Disease"

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)

    def _extract_pathway(self, df):
        """Extract pathway entities from CTD_pathways.csv
        """
        default_extracted_columns = ["PathwayID", "PathwayName"]
        renamed_columns = ["id", "name"]
        label = "Pathway"

        df = self._extract_entity(df, default_extracted_columns, renamed_columns, label)
        taxname = df["id"].apply(lambda x: "Home sapiens" if "hsa" in x or "HSA" in x else "")
        taxid = df["id"].apply(lambda x: "9606" if "hsa" in x or "HSA" in x else "")
        df = df.with_columns(taxname=taxname, taxid=taxid)
        return df

    def _extract_biologicalprocess(self, df):
        """Extract biological process entities from CTD_chem_go_enriched.csv
        """
        default_extracted_columns = ["GOTermID", "GOTermName"]
        renamed_columns = ["id", "name"]
        label = "BiologicalProcess"

        df = df.filter(pl.col("Ontology") == "Biological Process")

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)

    def _extract_cellularcomponent(self, df):
        """Extract cellular component entities from CTD_chem_go_enriched.csv
        """
        default_extracted_columns = ["GOTermID", "GOTermName"]
        renamed_columns = ["id", "name"]
        label = "CellularComponent"

        df = df.filter(pl.col("Ontology") == "Cellular Component")

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)

    def _extract_molecularfunction(self, df):
        """Extract molecular function entities from CTD_chem_go_enriched.csv
        """
        default_extracted_columns = ["GOTermID", "GOTermName"]
        renamed_columns = ["id", "name"]
        label = "MolecularFunction"

        df = df.filter(pl.col("Ontology") == "Molecular Function")

        return self._extract_entity(df, default_extracted_columns, renamed_columns, label)


class RelationshipExtractor(BaseExtractor):
    def __init__(self, relationship_type, basedir=".", output_dir=".") -> None:
        super().__init__(basedir, output_dir)

        self.default_relationships = {
            "Chemical_Gene": "CTD_chem_gene_ixns.csv",
            "Chemical_Disease": "CTD_chemicals_diseases.csv",
            "Chemical_Pathway": "CTD_chem_pathways_enriched.csv",
            "Gene_Disease": "CTD_genes_diseases.csv",
            "Gene_Pathway": "CTD_genes_pathways.csv",
            "Disease_BiologicalProcess": "CTD_Phenotype-Disease_biological_process_associations.csv",
            "Disease_CellularComponent": "CTD_Phenotype-Disease_cellular_component_associations.csv",
            "Disease_MolecularFunction": "CTD_Phenotype-Disease_molecular_function_associations.csv",
            "Disease_Pathway": "CTD_diseases_pathways.csv",
        }

        if relationship_type not in self.default_relationships.keys():
            raise ValueError(
                f"Entity type {relationship_type} is not supported.")

        self.relationship_type = relationship_type
        self.filepath = os.path.join(
            basedir, self.default_relationships[relationship_type])

        if self._check_file_exists(self.filepath) is False:
            self.filepath = self.filepath.replace(".csv", ".tsv")

        if self._check_file_exists(self.filepath) is False:
            raise ValueError(f"File {self.filepath}/.tsv not found.")

        self.relationship_label = "IS_ASSOCIATED_WITH"

    def extract(self):
        """Extract relationships from the data.
        """
        # TODO: Add dtype for some columns, now it's string by default.
        self._load_data()

        relationship_type = self.relationship_type.lower()
        method_name = f"_extract_{relationship_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(self.data)
        else:
            raise ValueError(
                f"Relationship type {relationship_type} is not supported.")

    def _extract_relationship(self, df, default_extracted_columns, renamed_columns, label,
                              groupby_columns=[], merge_funcs={}):
        for column in default_extracted_columns:
            if column not in df.columns:
                raise ValueError(
                    f"Column {column} not found in the dataframe.")

        df = df.select(default_extracted_columns)
        df = df.rename({old: new
                        for old, new in zip(default_extracted_columns, renamed_columns)})
        new_df = pl.DataFrame(
            {
                "relation_type": [label] * df.shape[0],
                "source_type": [self.relationship_type.split("_")[0]] * df.shape[0],
                "target_type": [self.relationship_type.split("_")[1]] * df.shape[0],
                "resource": [self.database_name] * df.shape[0],
            }
        )
        df = df.hstack(new_df)

        logging.info("Extract %s relationships from %s..." %
                     (df.shape[0], self.filepath))
        logging.info("Keep %s columns: %s" %
                     (len(default_extracted_columns), default_extracted_columns))
        logging.info("Rename columns to: %s" % renamed_columns)

        if groupby_columns and merge_funcs:
            # Add default columns which are not in groupby_columns but defined in current function.
            if sorted(groupby_columns) == sorted(["source_id", "target_id"]):
                groupby_columns = ["source_id", "target_id", "relation_type", 
                                   "source_type", "target_type", "resource"]
            df = df.groupby(groupby_columns).agg(merge_funcs)
            logging.info("After groupby, %s relationships are left." %
                         df.shape[0])
        else:
            df = df.unique()
            logging.info(
                "Drop duplicates in place, and %s relationships are left." % df.shape[0])

        return df

    def _extract_chemical_gene(self, df):
        """Extract chemical-gene relationships from CTD_chem_gene_ixns.csv
        """
        default_extracted_columns = ["ChemicalID", "GeneID"]
        renamed_columns = ["source_id", "target_id"]
        label = "CTD::IS_ASSOCIATED_WITH"
        df = df.with_columns(pl.col("GeneID").apply(lambda x: "ENTREZ:" + x))
        df = df.with_columns(pl.col("ChemicalID").apply(lambda x: "MESH:" + x))

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_chemical_disease(self, df):
        """Extract chemical-disease relationships from CTD_chemicals_diseases.csv
        """
        default_extracted_columns = ["ChemicalID", "DiseaseID"]
        renamed_columns = ["source_id", "target_id"]
        df = df.with_columns(pl.col("ChemicalID").apply(lambda x: "MESH:" + x))
        label = "CTD::IS_ASSOCIATED_WITH"

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_chemical_pathway(self, df):
        """Extract chemical-pathway relationships from CTD_chem_pathways_enriched.csv
        """
        default_extracted_columns = ["ChemicalID", "PathwayID"]
        renamed_columns = ["source_id", "target_id"]
        df = df.with_columns(pl.col("ChemicalID").apply(lambda x: "MESH:" + x))
        label = "CTD::IS_ASSOCIATED_WITH"

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_gene_disease(self, df):
        """Extract gene-disease relationships from CTD_genes_diseases.csv
        """
        default_extracted_columns = ["GeneID", "DiseaseID", "DirectEvidence",
                                     "InferenceScore", "InferenceChemicalName", "PubMedIDs"]
        renamed_columns = ["source_id", "target_id", "evidence",
                           "degree", "induced_by", "pmids"]
        label = "CTD::IS_ASSOCIATED_WITH"
        df = df.with_columns(pl.col("GeneID").apply(lambda x: "ENTREZ:" + x))
        df = df.with_columns(pl.col("InferenceScore").cast(pl.Float64))

        merge_funcs = [
            pl.col("evidence").filter(pl.col("evidence") != "").unique().str.concat("|"),
            pl.col("degree").max(),
            pl.col("induced_by").filter(pl.col("induced_by") != "").unique().str.concat("|"),
            # TODO: Any deduplicated pmids exist after unique()?
            pl.col("pmids").filter(pl.col("pmids") != "").unique().str.concat("|"),
        ]

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label,
                                          groupby_columns=["source_id", "target_id"],
                                          merge_funcs=merge_funcs)

    def _extract_gene_pathway(self, df):
        """Extract gene-pathway relationships from CTD_genes_pathways.csv
        """
        default_extracted_columns = ["GeneID", "PathwayID"]
        renamed_columns = ["source_id", "target_id"]
        label = "CTD::IS_ASSOCIATED_WITH"
        df = df.with_columns(pl.col("GeneID").apply(lambda x: "ENTREZ:" + x))

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_disease_biologicalprocess(self, df):
        """Extract disease-biological process relationships from CTD_Phenotype-Disease_biological_process_associations.csv
        """
        default_extracted_columns = ["DiseaseID", "GOID"]
        renamed_columns = ["source_id", "target_id"]
        label = "CTD::IS_ASSOCIATED_WITH"

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_disease_cellularcomponent(self, df):
        """Extract disease-cellular component relationships from CTD_Phenotype-Disease_cellular_component_associations.csv
        """
        default_extracted_columns = ["DiseaseID", "GOID"]
        renamed_columns = ["source_id", "target_id"]
        label = "CTD::IS_ASSOCIATED_WITH"

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_disease_molecularfunction(self, df):
        """Extract disease-molecular function relationships from CTD_Phenotype-Disease_molecular_function_associations.csv
        """
        default_extracted_columns = ["DiseaseID", "GOID"]
        renamed_columns = ["source_id", "target_id"]
        label = "CTD::IS_ASSOCIATED_WITH"

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)

    def _extract_disease_pathway(self, df):
        """Extract disease-pathway relationships from CTD_diseases_pathways.csv
        """
        default_extracted_columns = ["DiseaseID", "PathwayID"]
        renamed_columns = ["source_id", "target_id"]
        label = "CTD::IS_ASSOCIATED_WITH"

        return self._extract_relationship(df, default_extracted_columns, renamed_columns, label)


def to_snake_case(text):
    """Convert a string to snake case. The string is such as "ChemicalGene".
    """
    snake_case_string = ""
    for i, char in enumerate(text):
        if char.isupper() and i != 0:
            snake_case_string += "_" + char.lower()
        else:
            snake_case_string += char.lower()
    return snake_case_string


@click.group()
def cli():
    pass


@cli.command()
@click.option("--entity-type", "-e", type=click.Choice(["Anatomy", "Compound", "Gene", "Disease", "Pathway", "BiologicalProcess", "CellularComponent", "MolecularFunction"]), required=True, help="The type of entities to be extracted.")
@click.option("--base-dir", "-b", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The base directory of the data files.")
@click.option("--output-dir", "-o", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The output directory of the extracted entities.")
def extract_entity(entity_type, base_dir, output_dir):
    """Extract entities from CTD.
    """
    extractor = EntityExtractor(entity_type, base_dir, output_dir)
    filename = f"{extractor.database_name.lower()}_{to_snake_case(entity_type)}.tsv"

    if os.path.isfile(os.path.join(output_dir, filename)):
        logging.info("File %s already exists, so skip it.\n" % filename)
        return

    df = extractor.extract()
    extractor.write(df, filename)


@cli.command()
@click.option("--relationship-type", "-r", type=click.Choice(["Chemical_Gene", "Chemical_Disease", "Chemical_Pathway", "Gene_Disease", "Gene_Pathway", "Disease_BiologicalProcess", "Disease_CellularComponent", "Disease_MolecularFunction", "Disease_Pathway"]), required=True, help="The type of relationships to be extracted.")
@click.option("--base-dir", "-b", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The base directory of the data files.")
@click.option("--output-dir", "-o", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The output directory of the extracted relationships.")
def extract_relationship(relationship_type, base_dir, output_dir):
    """Extract relationships from CTD.
    """
    extractor = RelationshipExtractor(relationship_type, base_dir, output_dir)
    filename = f"{extractor.database_name.lower()}_{extractor.relationship_label.lower()}_{relationship_type.lower()}.tsv"

    if os.path.isfile(os.path.join(output_dir, filename)):
        logging.info("File %s already exists, so skip it.\n" % filename)
        return

    df = extractor.extract()
    extractor.write(df, filename)


@cli.command()
@click.option("--base-dir", "-b", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The base directory of the data files.")
@click.option("--output-dir", "-o", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The output directory of the extracted entities and relationships.")
def extract_all_entities(base_dir, output_dir):
    """Extract all entities from CTD.
    """
    for entity_type in ["Anatomy", "Compound", "Gene", "Disease", "Pathway", "BiologicalProcess", "CellularComponent", "MolecularFunction"]:
        extractor = EntityExtractor(entity_type, base_dir, output_dir)
        filename = f"{extractor.database_name.lower()}_{to_snake_case(entity_type)}.tsv"

        if os.path.isfile(os.path.join(output_dir, filename)):
            logging.info("File %s already exists, so skip it.\n" % filename)
            continue

        df = extractor.extract()
        extractor.write(df, filename)


@cli.command()
@click.option("--base-dir", "-b", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The base directory of the data files.")
@click.option("--output-dir", "-o", default=".", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help="The output directory of the extracted entities and relationships.")
def extract_all_relationships(base_dir, output_dir):
    """Extract all relationships from CTD.
    """
    for relationship_type in ["Chemical_Gene", "Chemical_Disease", "Chemical_Pathway", "Gene_Disease", "Gene_Pathway", "Disease_BiologicalProcess", "Disease_CellularComponent", "Disease_MolecularFunction", "Disease_Pathway"]:
        extractor = RelationshipExtractor(
            relationship_type, base_dir, output_dir)
        filename = f"{extractor.database_name.lower()}_{extractor.relationship_label.lower()}_{relationship_type.lower()}.tsv"

        if os.path.isfile(os.path.join(output_dir, filename)):
            logging.info("File %s already exists, so skip it. \n" % filename)
            continue

        df = extractor.extract()
        extractor.write(df, filename)


if __name__ == "__main__":
    cli()
