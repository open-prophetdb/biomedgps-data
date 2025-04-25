"""
# 2-Hop Path Analysis

This notebook analyzes a knowledge graph to generate all possible 2-hop paths between nodes.

## What is a 2-hop path?
A 2-hop path consists of:
- A source node
- A first edge
- An intermediate node
- A second edge
- A target node

## Output Format
The analysis outputs a DataFrame containing all 2-hop paths with the following columns:
- source_id: ID of the starting node
- source_type: Type of the starting node
- first_edge_type: Type of the first edge
- intermediate_id: ID of the middle node
- intermediate_type: Type of the middle node
- second_edge_type: Type of the second edge
- target_id: ID of the ending node
- target_type: Type of the ending node

## Input Data
The notebook requires the following input files:
- graph_data/entities.tsv: Contains node information (ID, type, name)
- graph_data/relation_types.tsv: Contains edge type information
- graph_data/formatted_relations/all_relations.tsv: Contains the actual graph edges
"""

import networkx as nx
import pandas as pd
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import os
import pandas as pd
import networkx as nx
from pathlib import Path
import logging


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(root_dir, "datasets", "biomedgps-v20241115-134f92")

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


    def load_graph_data(dataset_dir):
        """Load the knowledge graph data from TSV files."""
        data_dir = Path(dataset_dir)

        # Load entities
        entities_df = pd.read_csv(data_dir / "knowledge_graph_entities.tsv", sep="\t")

        # Load knowledge graph
        kg_df = pd.read_csv(data_dir / "knowledge_graph.tsv", sep="\t")

        return entities_df, kg_df

    # Load the data
    logger.info("Loading graph data...")
    entities_df, kg_df = load_graph_data(dataset_dir=dataset_dir)

    # Display sample data
    logger.info("\n Entities:")
    logger.info(entities_df.head())

    logger.info("\nKnowledge graph:")
    logger.info(kg_df.head())

    # 构造 entities_df 中所有实体的 ID+类型 标准格式
    entity_set = set(
        f"{row['label']}::{row['id']}" for _, row in entities_df.iterrows()
    )

    # 构造 kg_df 中边涉及的所有实体（source 和 target）
    kg_entities_set = set()
    for _, row in kg_df.iterrows():
        source = f"{row['source_type']}::{row['source_id']}"
        target = f"{row['target_type']}::{row['target_id']}"
        kg_entities_set.add(source)
        kg_entities_set.add(target)

    # 检查哪些实体只出现在kg_df中，但不在entities_df中
    missing_entities = kg_entities_set - entity_set

    logger.info(f"\n实体总数（entities_df）: {len(entity_set)}")
    logger.info(f"边中涉及的实体总数: {len(kg_entities_set)}")
    logger.info(f"⚠️ 边中存在但不在entities_df中的实体数量: {len(missing_entities)}")

    # 若需要查看前几个缺失的实体：
    logger.info("\nMissing entities (sample):")
    logger.info(list(missing_entities)[:10])

    def create_graph(entities_df, kg_df):
        """Create a NetworkX directed graph from the triples data."""
        G = nx.MultiDiGraph()

        # Add nodes with their types
        for _, row in entities_df.iterrows():
            G.add_node(f"{row['label']}::{row['id']}", entity_type=row["label"])

        # Add edges with their types
        for _, row in kg_df.iterrows():
            G.add_edge(
                f"{row['source_type']}::{row['source_id']}",
                f"{row['target_type']}::{row['target_id']}",
                relation=row["relation_type"],
            )

        return G

    # Create the graph
    logger.info("Creating graph...")
    G = create_graph(entities_df, kg_df)

    # logger.info graph statistics
    logger.info(f"Number of nodes: {G.number_of_nodes()}")
    logger.info(f"Number of edges: {G.number_of_edges()}")

    kg_df[
        ["source_id", "source_type", "relation_type", "target_id", "target_type"]
    ].drop_duplicates().shape

    def _process_sources_chunk(G, entity_types, sources):
        paths = []
        for source in sources:
            if not G.succ[source]:
                continue

            source_type = entity_types.get(source, None)
            if source_type is None:
                continue

            for intermediate in G.successors(source):
                intermediate_type = entity_types.get(intermediate, None)
                if intermediate_type is None:
                    continue

                first_hop_edges = G[source][intermediate]
                for k1, edge_data_1 in first_hop_edges.items():
                    first_edge_type = edge_data_1.get("relation", None)
                    if first_edge_type is None:
                        continue

                    for target in G.successors(intermediate):
                        target_type = entity_types.get(target, None)
                        if target_type is None:
                            continue

                        second_hop_edges = G[intermediate][target]
                        for k2, edge_data_2 in second_hop_edges.items():
                            second_edge_type = edge_data_2.get("relation", None)
                            if second_edge_type is None:
                                continue

                            paths.append(
                                {
                                    "source_id": source,
                                    "source_type": source_type,
                                    "first_edge_type": first_edge_type,
                                    "intermediate_id": intermediate,
                                    "intermediate_type": intermediate_type,
                                    "second_edge_type": second_edge_type,
                                    "target_id": target,
                                    "target_type": target_type,
                                }
                            )
        return paths

    def generate_two_hop_paths_parallel(G, num_workers=4):
        entity_types = nx.get_node_attributes(G, "entity_type")
        all_sources = list(G.nodes())
        chunk_size = len(all_sources) // num_workers + 1
        chunks = [
            all_sources[i : i + chunk_size]
            for i in range(0, len(all_sources), chunk_size)
        ]

        with ThreadPool(num_workers) as pool:
            results = pool.map(partial(_process_sources_chunk, G, entity_types), chunks)

        all_paths = [item for sublist in results for item in sublist]
        return pd.DataFrame(all_paths)

    logger.info("Generating 2-hop paths with multiprocessing...")
    paths_df = generate_two_hop_paths_parallel(
        G, num_workers=4
    )  # or omit to auto-detect CPU count

    logger.info("\n2-hop paths (parallel):")
    logger.info(paths_df.head())

    # logger.info statistics
    logger.info(f"Total number of 2-hop paths: {len(paths_df)}")
    logger.info(f"Number of unique source nodes: {paths_df['source_id'].nunique()}")
    logger.info(
        f"Number of unique intermediate nodes: {paths_df['intermediate_id'].nunique()}"
    )
    logger.info(f"Number of unique target nodes: {paths_df['target_id'].nunique()}")

    # Save results to TSV
    output_path = Path(os.path.join(root_dir, "graph_analysis", "2hops_paths.tsv"))
    paths_df.to_csv(output_path, sep="\t", index=False)
    logger.info(f"\nSaved results to {output_path}")
