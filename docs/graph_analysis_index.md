---
hide:
	- navigation
---

## Analyze your relation file

In this jupyter notebook, we will build a graph based on your relation file and do some analysis on it. Such as the number of nodes, the number of edges, the number of subgraphs, and so on. Based on the metrics, you can know whether your relation file is valid for training or not. If your relation file have too many subgraphs and no any subgraph is large enough (e.g. the percent of the number of nodes and edges in a subgraph is no more than 90% of the total number of nodes and edges in the graph.), you may need to consider to add more relations to your relation file.

In our opinion, the number of subgraphs should be as small as possible, and the number of nodes and edges in a subgraph should be as large as possible. In this way, the model can learn more information from the graph.

Please refer to the [graph_anaysis.ipynb](https://github.com/open-prophetdb/biomedgps-data/blob/main/graph_analysis/graph_anaysis.ipynb) for more details.

## Stat & Visualize your relation file

In this jupyter notebook, we will process and visualize statistical data related to entities and relations. Utilizing the Plotly library, it creates charts & tables that showcase statistical information about various types of entities and relationships. These charts & tables are intended to provide users with a quick and comprehensive understanding of the data.

Node Count: Displays the count of different types of entities. Each row represents a type of entity, with columns including the resources associated with the entity and their respective counts.

Relationship Count: Shows the count of different types of relationships. Each row represents a type of relationship, with columns detailing the resources associated with the relationship and their counts.

Please refer to the [visualize.ipynb](https://github.com/open-prophetdb/biomedgps-data/blob/main/graph_analysis/visualize.ipynb) for more details.