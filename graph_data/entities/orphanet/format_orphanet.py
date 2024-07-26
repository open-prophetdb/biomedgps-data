import click
import re
import os
import rdflib
import pandas as pd


cli = click.Group()

# Define the namespaces (prefixes) used in the OWL file
namespace = {
    "ORDO": "http://www.orpha.net/ORDO/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "efo": "http://www.ebi.ac.uk/efo/",
    "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
}

# Function to get efo:definition for a given entity
def get_definition(g: rdflib.Graph, entity_uri: str) -> str:
    query = f"""
        SELECT ?definition WHERE {{
            <{entity_uri}> efo:definition ?definition .
        }}
    """
    results = g.query(query, initNs=namespace)
    for row in results:
        return str(row.definition) # type: ignore
    return ""

# Function to get efo:definition for a given entity
def get_name(g: rdflib.Graph, entity_uri: str) -> str:
    query = f"""
        SELECT ?label WHERE {{
            <{entity_uri}> rdfs:label ?label .
        }}
    """
    results = g.query(query, initNs=namespace)
    for row in results:
        return str(row.label) # type: ignore
    return ""

def get_metadata(g: rdflib.Graph, entity_uri: str, id_suffix: str) -> list:
    query = f"""
        SELECT ?Orphanet_{id_suffix} WHERE {{
            <{entity_uri}> ORDO:Orphanet_{id_suffix} ?Orphanet_{id_suffix} .
        }}
    """
    results = g.query(query, initNs=namespace)
    m = [str(row[f"Orphanet_{id_suffix}"]) for row in results] # type: ignore
    return m

def get_db_xrefs(g: rdflib.Graph, entity_uri: str) -> list:
    mapping = {
        "MeSH": "MESH",
        "MedDRA": "MedDRA",
        "ICD-10": "ICD-10",
        "ICD-11": "ICD-11",
        "UMLS": "UMLS",
    }
    query = f"""
        SELECT ?db_xrefs WHERE {{
            <{entity_uri}> oboInOwl:hasDbXref ?db_xrefs .
        }}
    """
    results = g.query(query, initNs=namespace)
    db_xrefs = [str(row.db_xrefs) for row in results] # type: ignore
    xrefs = [
        f"{mapping.get(x.split(':')[0], x.split(':')[0])}:{x.split(':')[1]}"
        for x in db_xrefs
    ]
    return xrefs


def parse_ancestors(inputfile: str) -> tuple[rdflib.Graph, dict]:
    # Load the OWL file
    g = rdflib.Graph()
    g.parse(inputfile, format="xml")

    # Query to get all classes with their labels
    label_query = """
        SELECT ?class ?label WHERE {
            ?class rdf:type owl:Class .
            ?class rdfs:label ?label .
        }
    """

    # Execute the query to get top-level categories
    label_results = g.query(label_query, initNs=namespace)
    base_uris = {str(label): class_uri for class_uri, label in label_results if class_uri.startswith("http://www.orpha.net/ORDO/Orphanet_C")} # type: ignore

    base_uris_map = {
        str(class_uri): {"label": label, "definition": get_definition(g, class_uri)} # type: ignore
        for label, class_uri in base_uris.items()
    }

    # SPARQL query to get all entities with their subclasses
    query = """
        SELECT ?entity ?subclass WHERE {
            ?entity rdf:type owl:Class .
            OPTIONAL { ?subclass rdfs:subClassOf ?entity . }
        }
    """

    # Execute the query
    results = g.query(query, initNs=namespace)

    # Dictionaries to hold entities and their subclasses
    entities_with_subclasses = set()
    entities = set()

    for row in results:
        entity = row.entity # type: ignore
        subclass = row.subclass # type: ignore
        entities.add(entity)
        if subclass:
            entities_with_subclasses.add(subclass)

    # Bottom entities are those that are not in entities_with_subclasses
    bottom_entities = [
        entity
        for entity in entities - entities_with_subclasses
        if entity.startswith("http://www.orpha.net/ORDO/Orphanet_C")
    ]

    # Function to recursively build the graph structure
    def build_graph_structure(entity, graph_structure):
        # SPARQL query to get all entities with their subclasses
        query = """
            SELECT ?entity ?parent WHERE {
                ?entity rdf:type owl:Class .
                ?entity rdfs:subClassOf ?parent .
            }
        """

        # Execute the query
        results = g.query(query, initNs=namespace)
        for row in results:
            entity = str(row.entity) # type: ignore
            parent = str(row.parent) # type: ignore
            if entity not in graph_structure:
                graph_structure[entity] = []
            if parent.startswith("http://www.orpha.net/ORDO/Orphanet_"):
                graph_structure[entity].append(parent)
                graph_structure[entity] = list(set(graph_structure[entity]))

    # Dictionary to store the hierarchical structure
    graph_structure = {}

    # Build the graph structure starting from each bottom entity
    for entity in bottom_entities:
        build_graph_structure(entity, graph_structure)

    # Function to find all ancestors of a given node
    def find_all_ancestors(node, graph_structure):
        ancestors = list()
        if node in graph_structure:
            parents = graph_structure[node]
            for parent in parents:
                ancestors.append(parent)
                ancestors.extend(find_all_ancestors(parent, graph_structure))
        return ancestors

    # Dictionary to store each node and its ancestors
    node_ancestors = {
        node: list(find_all_ancestors(node, graph_structure)) for node in graph_structure
    }

    return g, node_ancestors


def extract(graph: rdflib.Graph, node_ancestors: dict) -> pd.DataFrame:
    nodes = []
    for node, ancestors in node_ancestors.items():
        node_data = {}
        print(f"Handling {node}")

        node_data["id"] = f"Orphanet:{node.split('_')[-1]}"
        node_data["raw_id"] = node
        parent = ancestors[-1] if ancestors else None
        if parent and parent.endswith("C001"):
            node_data["label"] = "Disease"
        else:
            # We don't care about the ancestors that are not diseases
            continue
        node_data["resource"] = "Orphanet"
        node_data["name"] = get_name(graph, node)
        # http://www.orpha.net/ORDO/Orphanet_C016
        # <AnnotationProperty rdf:about="http://www.orpha.net/ORDO/Orphanet_C016">
        #     <efo:definition xml:lang="en">Relationship between a clinical entity and modes of inheritance.</efo:definition>
        #     <rdfs:label>has_inheritance</rdfs:label>
        # </AnnotationProperty>
        node_data["has_inheritance"] = "|".join(get_metadata(graph, node, "C016"))
        # http://www.orpha.net/ORDO/Orphanet_C017
        # <AnnotationProperty rdf:about="http://www.orpha.net/ORDO/Orphanet_C017">
        #     <efo:definition xml:lang="en">Relationship between clinical entity and age of onset.</efo:definition>
        #     <rdfs:label>has_age_of_onset</rdfs:label>
        # </AnnotationProperty>
        node_data["has_age_of_onset"] = "|".join(get_metadata(graph, node, "C017"))
        # http://www.orpha.net/ORDO/Orphanet_C022
        # <AnnotationProperty rdf:about="http://www.orpha.net/ORDO/Orphanet_C022">
        #     <efo:definition xml:lang="en">Relationship between a clinical entity and the geographical area for which epidemiological data (Epidemiology) is available.</efo:definition>
        #     <rdfs:label>present_in</rdfs:label>
        # </AnnotationProperty>
        node_data["present_in"] = "|".join(get_metadata(graph, node, "C022"))
        node_data["description"] = get_definition(graph, node)
        node_data["xrefs"] = "|".join(get_db_xrefs(graph, node))
        node_data["pmids"] = None
        node_data["synonyms"] = None

        nodes.append(node_data)

    df = pd.DataFrame(nodes)
    return df


@cli.command(help="Parse the orphanet ontology")
@click.option("--input", "-i", required=True, help="The input file path")
@click.option("--output", "-o", required=True, help="The output directory path")
def entities(input, output):
    g, node_ancestors = parse_ancestors(input)
    df = extract(g, node_ancestors)
    outputfile = os.path.join(output, "orphanet_disease.tsv")
    main_df = df[["id", "name", "description", "label", "resource", "xrefs", "pmids", "synonyms"]]
    additional_outputfile = os.path.join(output, "orphanet_disease_metadata.tsv")
    additional_columns = ["id", "has_inheritance", "has_age_of_onset", "present_in"]

    # Remove all unexpected empty characters, such as leading and trailing spaces
    main_df["description"] = main_df["description"].fillna("")
    main_df["description"] = main_df["description"].apply(
        lambda x: " ".join(x.strip().split())
    )
    # Write the data frame to a tsv file
    main_df.to_csv(outputfile, sep="\t", index=False)
    df[additional_columns].to_csv(additional_outputfile, sep="\t", index=False)


if __name__ == "__main__":
    cli()
