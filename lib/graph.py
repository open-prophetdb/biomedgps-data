import os
import pandas as pd
import networkx as nx
from check import check_file_exists, check_columns
from typing import Tuple

# Union of all the types of graphs
Graph = nx.MultiGraph | nx.Graph | nx.MultiDiGraph | nx.DiGraph
DirectedGraph = nx.MultiDiGraph | nx.DiGraph
UndirectedGraph = nx.MultiGraph | nx.Graph


def gen_cytoscape(
    formatted_df,
    xgmml_file,
    allowed_types=[
        "Gene",
        "Compound",
        "Disease",
        "Symptom",
        "Pathway",
        "Anatomy",
        "Metabolite",
        "MolecularFunction",
        "BiologicalProcess",
        "CellularComponent",
    ],
):
    # Convert the df to a file which is compatible with cytoscape
    # Prompt: I have a data frame which contains seven columns: 'source_id', 'source_type', 'source_name', 'target_id', 'target_type', 'target_name', 'relation_type', how to convert the data frame into a xgmml file.
    colors = [
        "#e60049",
        "#0bb4ff",
        "#50e991",
        "#e6d800",
        "#9b19f5",
        "#ffa300",
        "#dc0ab4",
        "#b3d4ff",
        "#00bfa0",
        "#ff6e00",
    ]

    node_type_colors = {}
    for node_type, color in zip(allowed_types, colors):
        node_type_colors[node_type] = color

    nodes_df = formatted_df[["source_id", "source_name", "source_type"]].rename(
        columns={"source_id": "id", "source_name": "name", "source_type": "type"}
    )
    nodes_df = pd.concat(
        [
            nodes_df,
            formatted_df[["target_id", "target_name", "target_type"]].rename(
                columns={
                    "target_id": "id",
                    "target_name": "name",
                    "target_type": "type",
                }
            ),
        ],
        axis=0,
    )
    nodes_df = nodes_df.drop_duplicates(subset=["id", "type"])

    edges_df = formatted_df[["source_id", "target_id", "relation_type"]].rename(
        columns={"source_id": "source", "target_id": "target", "relation_type": "label"}
    )

    # Create an XGMML template with additional attributes
    xgmml_template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <!DOCTYPE graph PUBLIC "-//John Punin//DTD graph description//EN" "http://www.cs.rpi.edu/~puninj/XGMML/xgmml.dtd">
    <graph label="Knowledge Graph" directed="1">
    {nodes}
    {edges}
    </graph>
    """

    # Create node and edge elements with additional attributes
    node_lst = [
        f"""
        <node id="{id}" label="{name}">
            <att name="id" type="string" value="{id}" />
            <att name="name" type="string" value="{name}" />
            <att name="type" type="string" value="{type}" />
            <att name="node_shape" type="string" value="ellipse" />
            <att name="node_color" type="string" value="{node_type_colors[type]}" />
        </node>
        """
        for id, name, type in zip(nodes_df["id"], nodes_df["name"], nodes_df["type"])
    ]
    nodes = "\n".join(node_lst)

    edge_lst = [
        f"""
        <edge source="{source}" target="{target}" label="{label}" cy:directed="1">
            <att name="relation_type" type="string" value="{label}" />
            <att name="shared name" value="{label}" type="string"
            cy:type="String" />
            <att name="shared interaction" value="" type="string" cy:type="String" />
            <att name="name" value="{label}" type="string" cy:type="String" />
            <att name="selected" value="0" type="boolean" cy:type="Boolean" />
            <att name="interaction" value="" type="string" cy:type="String" />
            <att name="relation_type" value="{label}" type="string"
            cy:type="String" />
        </edge>
        """
        for source, target, label in zip(
            edges_df["source"], edges_df["target"], edges_df["label"]
        )
    ]
    edges = "\n".join(edge_lst)

    # Populate the XGMML template
    xgmml_content = xgmml_template.format(nodes=nodes, edges=edges)

    with open(xgmml_file, "w") as f:
        f.write(xgmml_content)


def create_graph(
    relation_file,
    entity_file=None,
    allowed_types=[],
    directed=False,
    allow_multiple_edges=False,
) -> Graph:
    """Create a graph from the relations file and annotate the nodes with the entity file.

    Args:
        relation_file (str): path to the relations file
        entity_file (str, optional): path to the entities file. Defaults to None. If the entity file is not provided, the nodes will not be annotated.
        allowed_types (list, optional): list of node types to include in the graph. If not provided, all node types will be included. Such as [ "Gene", "Compound", "Disease", "Symptom", "Pathway", "Anatomy", "Metabolite", "MolecularFunction", "BiologicalProcess", "CellularComponent"].

    Returns:
        Graph: graph with nodes and edges, if directed is True, the graph will be directed, otherwise it will be undirected. if allow_multiple_edges is True, the graph will allow multiple edges between the same nodes, otherwise it will not.
    """
    # Get all paths with length <= 3 and one node as a start point.
    # > Prompt:
    # > If I have a file which contains the following columns: source_id, source_type, target_id, target_type, relation_type. and any node will be treated as a uniq node, if its id:type is different from others. I would like to use one specified node as a start point and get a subgraph which all nodes linked with it and the length of paths <= 3, how to do it? In the meanwhile, please save the paths as a file which contains five columns: source_id, source_type, relation_type, target_id, target_type.
    # Read the data from the file into a DataFrame
    df = pd.read_csv(relation_file, sep="\t", dtype=str)

    if entity_file and os.path.exists(entity_file):
        entities = pd.read_csv(entity_file, sep="\t", dtype=str)

        # Join the df and the entites to get the label of each node and add name field from the entites to the df
        df = df.merge(
            entities[["id", "name", "label"]],
            left_on=["source_id", "source_type"],
            right_on=["id", "label"],
            how="left",
        )
        df = df.rename(columns={"name": "source_name"})

        df = df.merge(
            entities[["id", "name", "label"]],
            left_on=["target_id", "target_type"],
            right_on=["id", "label"],
            how="left",
        )
        df = df.rename(columns={"name": "target_name"})
    else:
        # TODO: Add the name field from the all entities where the id matches the source_id and target_id
        df["source_name"] = df["source_id"]
        df["target_name"] = df["target_id"]
        pass

    # Create a directed graph to represent the relationships
    # It might contain multiple edges between the same nodes, so we need to use MultiDiGraph instead of DiGraph
    if allow_multiple_edges:
        if directed:
            G = nx.MultiDiGraph()
        else:
            G = nx.MultiGraph()
    else:
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()

    # Add nodes and edges to the graph
    for _, row in df.iterrows():
        source_id = row["source_id"]
        source_type = row["source_type"]
        source_name = row["source_name"]
        target_id = row["target_id"]
        target_type = row["target_type"]
        target_name = row["target_name"]
        relation_type = row["relation_type"]
        formatted_relation_type = row["formatted_relation_type"]

        if allowed_types:
            if source_type not in allowed_types or target_type not in allowed_types:
                continue

        # Add nodes for source and target with node type as an attribute
        G.add_node((source_id, source_type), name=source_name, node_type=source_type)
        G.add_node((target_id, target_type), name=target_name, node_type=target_type)

        # Add directed edge from source to target
        G.add_edge(
            (source_id, source_type),
            (target_id, target_type),
            relation=relation_type,
            formatted_relation=formatted_relation_type,
            source_name=source_name,
            target_name=target_name,
        )

    return G


def remove_nodes(G, start_node, n_hops=3, types_to_remove=[]):
    subgraph = G.copy()
    nodes_to_remove = []
    # Create the subgraph containing nodes within n hops of the specified node
    for node in subgraph.nodes():
        if node == start_node:
            continue

        try:
            if (
                nx.shortest_path_length(subgraph, start_node, node) > n_hops
                or subgraph.nodes[node]["node_type"] in types_to_remove
            ):
                nodes_to_remove.append(node)
        except nx.NetworkXNoPath:
            nodes_to_remove.append(node)

    print("Number of nodes in the subgraph: ", len(subgraph.nodes()))
    print("Number of edges in the subgraph: ", len(subgraph.edges()))

    if len(nodes_to_remove) > 0:
        # Remove the nodes from the subgraph
        print("Number of nodes to remove: ", len(nodes_to_remove))
        subgraph.remove_nodes_from(nodes_to_remove)
        print(
            "Number of nodes in the subgraph after removing nodes: ",
            len(subgraph.nodes()),
        )

    # Create a list to store the paths in the desired format, keeping only the n_hops layers
    formatted_paths = []

    for source_node, target_node, edge_attrs in subgraph.edges(data=True):
        relation_type = edge_attrs.get("relation", None)
        source_name = subgraph.nodes[source_node].get("name", None)
        target_name = subgraph.nodes[target_node].get("name", None)

        formatted_paths.append(
            (
                source_node[0],
                source_node[1],
                relation_type,
                target_node[0],
                target_node[1],
                source_name,
                target_name,
            )
        )

    # Create a DataFrame from the formatted paths
    formatted_df = pd.DataFrame(
        formatted_paths,
        columns=[
            "source_id",
            "source_type",
            "relation_type",
            "target_id",
            "target_type",
            "source_name",
            "target_name",
        ],
    )

    print("Number of edges in the subgraph: ", formatted_df.shape[0])

    return formatted_df


def search_subgraph(G, start_node, end_node, n_hops=2):
    """Search for a subgraph containing the start and end nodes within n_hops

    Args:
        G (Graph): generated from create_graph
        start_node (tuple): (id, type), such as ('DrugBank::DB00394', 'Compound')
        end_node (tuple): (id, type), such as ('DrugBank::DB00394', 'Compound')
        n_hops (int): default is 2
    """
    # Get all path between the two nodes
    all_paths = nx.all_simple_paths(
        G, source=start_node, target=end_node, cutoff=n_hops
    )

    # Create a list to store the paths in the desired format
    formatted_paths = []

    # Iterate through the paths and store them
    for path in all_paths:
        # Iterate through the edges in the path and store them
        for i in range(len(path) - 1):
            source_node = path[i]
            target_node = path[i + 1]
            relation_type = G.edges[source_node, target_node]["relation"]
            source_name = G.nodes[source_node]["name"]
            target_name = G.nodes[target_node]["name"]

            formatted_paths.append(
                (
                    source_node[0],
                    source_node[1],
                    relation_type,
                    target_node[0],
                    target_node[1],
                    source_name,
                    target_name,
                )
            )

    # Create a DataFrame from the formatted paths
    formatted_df = pd.DataFrame(
        formatted_paths,
        columns=[
            "source_id",
            "source_type",
            "relation_type",
            "target_id",
            "target_type",
            "source_name",
            "target_name",
        ],
    )

    return formatted_df


def get_relation_file(dataset_name):
    # dataset_name = "drkg-hsdn-custom-malacards-filtered-all"
    data_dir = os.path.join(os.getcwd(), dataset_name, "data")
    relation_file = os.path.join(data_dir, "%s.tsv" % dataset_name)
    check_file_exists(relation_file)

    return relation_file


def load_relations(dataset_name):
    relation_file = get_relation_file(dataset_name)
    relations = pd.read_csv(relation_file, sep="\t", dtype=str)

    return relations


def load_entities(data_dir):
    """Load entities from the entities.tsv file

    Args:
        data_dir (str): default is graph_data directory in the current working directory

    Returns:
        DataFrame: entities
    """
    entity_file = os.path.join(data_dir, "entities.tsv")
    check_file_exists(entity_file)
    entities = pd.read_csv(entity_file, sep="\t", dtype=str)
    return entities


def get_relation_types(relations):
    columns = ["source_id", "relation_type", "target_id"]
    check_columns(relations, columns)
    relations = relations[columns]

    return list(set(relations["relation_type"].to_list()))


def group_relations(relations):
    df = pd.DataFrame()
    df["resource"] = relations["relation_type"].apply(lambda x: x.split("::")[0])
    df["source_type"] = relations["source_id"].apply(lambda x: x.split(":")[0])
    df["target_type"] = relations["target_id"].apply(lambda x: x.split(":")[0])
    df["source_target"] = df["source_type"] + ":" + df["target_type"]

    # source_type:target_type might be same with target_type:source_type, merge them
    df["source_target"] = df["source_target"].apply(
        lambda x: x.split(":")[0] + ":" + x.split(":")[1]
        if x.split(":")[0] > x.split(":")[1]
        else x.split(":")[1] + ":" + x.split(":")[0]
    )

    # Plot only the rows where matched source and target types are in the list
    filtered_df = df[
        df["source_type"].isin(["Disease", "Gene", "Compound", "Symptom", "Pathway"])
        & df["target_type"].isin(["Disease", "Gene", "Compound", "Symptom", "Pathway"])
    ]

    # Group the data by 'label' and 'resource' and count the rows
    grouped_df = (
        filtered_df.groupby(["source_target", "resource"])
        .size()
        .reset_index(name="count")
    )

    # resource = ['bioarx', 'DGIDB', 'DRUGBANK', 'GNBR', 'Hetionet', 'INTACT', 'STRING', 'HSDN']
    # # Please specify the colors in the same order as the resource list
    # colors = [
    #     "#FF0000",  # Red
    #     "#008000",  # Green
    #     "#0000FF",  # Blue
    #     "#FFFF00",  # Yellow
    #     "#800080",  # Purple
    #     "#FFA500",  # Orange
    #     "#FFC0CB",  # Pink
    #     "#00FFFF"   # Cyan
    # ]

    # # Generate a list of colors for each resource
    # colors = grouped_df['resource'].apply(lambda x: colors[resource.index(x)])

    return grouped_df


def get_num_nodes(G: Graph) -> int:
    """Get the number of nodes in a graph

    Args:
        G (Graph): graph

    Returns:
        int: number of nodes
    """
    return len(G.nodes())


def get_num_edges(G: Graph) -> int:
    """Get the number of edges in a graph

    Args:
        G (Graph): graph

    Returns:
        int: number of edges
    """
    return len(G.edges())


def get_num_subgraphs(G: Graph) -> int:
    """Get the number of subgraphs in a graph

    Args:
        G (Graph): graph

    Returns:
        int: number of subgraphs
    """
    if type(G) == nx.MultiGraph or type(G) == nx.Graph:
        return len(list(nx.connected_components(G)))
    elif type(G) == nx.MultiDiGraph or type(G) == nx.DiGraph:
        return len(list(nx.weakly_connected_components(G)))


def get_subgraph(G: Graph, start_node: Tuple[str, str]) -> Graph:
    """Get the subgraph containing the start node

    Args:
        G (Graph): graph
        start_node (Tuple[str, str]): node to start from, such as ('DrugBank::DB00394', 'Compound')

    Returns:
        Graph: subgraph
    """
    if type(G) == nx.MultiGraph or type(G) == nx.Graph:
        return G.subgraph(list(nx.node_connected_component(G, start_node)))
    elif type(G) == nx.MultiDiGraph or type(G) == nx.DiGraph:
        return G.subgraph(list(nx.descendants(G, start_node)))


def make_wide_format(array, key1, key2, vkey):
    wide_data = {}
    for item in array:
        formatted_key1 = snake_case(item[key1])
        if formatted_key1 not in wide_data:
            wide_data[formatted_key1] = {key1: item[key1]}
        formatted_key2 = snake_case(item[key2])
        wide_data[formatted_key1][formatted_key2] = item[vkey]
    return list(wide_data.values())


def transposed_array(array):
    transposed = []
    for i in range(len(array[0])):
        transposed_row = [array[j][i] for j in range(len(array))]
        transposed.append(transposed_row)
    return transposed


def snake_case(string):
    return string.lower().replace(" ", "_")


def gen_layout(title, xaxis_title, yaxis_title, showlegend):
    return {
        "title": title,
        "xaxis": {"title": xaxis_title},
        "yaxis": {"title": yaxis_title},
        "showlegend": showlegend,
    }


def biomedgps2stat(
    entities: pd.DataFrame, relations: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Convert the biomedgps format to stat format

    Args:
        entities (pd.DataFrame): entities
        relations (pd.DataFrame): relations

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: entities, relations
    """
    node_stat = entities.groupby(["label", "resource"]).size().reset_index(name="count")
    node_stat.rename(
        columns={
            "label": "entity_type",
            "count": "entity_count",
            "resource": "resource",
        },
        inplace=True,
    )

    edge_stat = (
        relations.groupby(["relation_type", "source_type", "target_type", "resource"])
        .size()
        .reset_index(name="count")
    )
    edge_stat.rename(
        columns={
            "relation_type": "relation_type",
            "source_type": "start_entity_type",
            "target_type": "end_entity_type",
            "count": "relation_count",
            "resource": "resource",
        },
        inplace=True,
    )

    return node_stat, edge_stat
