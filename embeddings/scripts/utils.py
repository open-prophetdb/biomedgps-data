import os
import sys
import pandas as pd

# from sklearn.manifold import TSNE
from fitsne import FItSNE
import numpy as np
import plotly.express as px

package_dir = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(os.path.join(package_dir, "lib"))
# Add the graph module to the system path
from graph import get_color

# Load a data file which is a tsv file and the last column is an embedding vector. The embedding vector is a string of numbers separated by pipes.
def load_data(file_name):
    df = pd.read_csv(file_name, sep="\t")
    df = df.reset_index(drop=True)
    df["embedding"] = df["embedding"].apply(lambda x: x.split("|"))
    return df


# Visualize the data using t-SNE and show node names on the plot when hovering over the nodes.
def get_tsne(df):
    X = np.array(df["embedding"].tolist())
    X = X.astype(np.float64)
    X_2d = FItSNE(X)
    return X_2d


def visualize_entities(df, color_column="entity_type"):
    colors = [get_color(type) for type in set(df["entity_type"])]
    fig = px.scatter(
        df,
        x="x",
        y="y",
        hover_name="entity_name",
        color=color_column,
        color_discrete_sequence=colors,
    )
    return fig


def visualize_relation_types(df, color_column="relation_type"):
    fig = px.scatter(df, x="x", y="y", color=color_column, hover_name="relation_type")
    return fig
