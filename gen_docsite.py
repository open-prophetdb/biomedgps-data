import os
import re

docsite_url = "https://open-prophetdb.github.io/biomedgps-data/"
domain = "https://github.com/open-prophetdb/biomedgps-data/blob/main"
path_name_map = {
    "README.md": "index.md",
    "graph_data/README.md": "graph_data_index.md",
    "graph_data/KG_README.md": "graph_data_kg.md",
    "datasets/README.md": "datasets_index.md",
    "wandb/README.md": "wandb_index.md",
    "graph_analysis/README.md": "graph_analysis_index.md",
    "examples/README.md": "examples_index.md",
    "embeddings/README.md": "embeddings_index.md",
    "embedding_analysis/README.md": "embedding_analysis_index.md",
    "benchmarks/README.md": "benchmarks_index.md",
    "prediction/README.md": "prediction_index.md",
    "FAQs.md": "faqs.md",
}

no_navigations = [
    "index.md",
    "datasets_index.md",
    "graph_analysis_index.md",
    "prediction_index.md",
    "faqs.md",
]


def is_valid(filepath):
    return not (
        filepath.startswith("http")
        or filepath.startswith("https")
        or filepath.startswith("www")
        or filepath.startswith("ftp")
        or filepath.startswith("sftp")
        or filepath.startswith("ssh")
        or filepath.startswith("#")
    )


def is_doc(filepath):
    paths = path_name_map.keys()

    for path in paths:
        if filepath.endswith(path):
            return path

    return ""


def normalize_path(filepath):
    path = is_doc(filepath)
    relative_path = os.path.relpath(filepath, os.getcwd())
    url_path = path_name_map.get(relative_path)
    if url_path:
        return os.path.join(
            docsite_url, url_path.replace(".md", "")
        )
    else:
        return filepath


# Copy files and rename
def copy_files():
    if os.path.exists("docs"):
        # Remove all markdown files in docs
        for file in os.listdir("docs"):
            if file.endswith(".md"):
                os.remove(os.path.join("docs", file))

    for path, name in path_name_map.items():
        if not os.path.exists(path):
            continue

        destpath = os.path.join("docs", name)

        # Replace all relative links to absolute links in the markdown file
        with open(path, "r") as f:
            content = f.readlines()
            for i in range(len(content)):
                # Extract the relative file path using regex
                line = content[i]
                filepaths = re.findall(r"\]\((?!http)([^)]+)\)", line)
                dirpath = os.path.dirname(os.path.abspath(path))
                fixed_filepaths = [
                    os.path.normpath(os.path.join(dirpath, filepath))
                    if is_valid(filepath)
                    else filepath
                    for filepath in filepaths
                ]

                urls = [
                    filepath.replace(os.getcwd(), domain)
                    if is_valid(filepath) and not is_doc(filepath)
                    else normalize_path(filepath)
                    for filepath in fixed_filepaths
                ]
                zipped = list(zip(filepaths, fixed_filepaths, urls))
                if len(zipped) > 0:
                    print(f"Replace {zipped} in {path}")
                for j in range(len(filepaths)):
                    line = line.replace(filepaths[j], urls[j])
                content[i] = line

        header = ""

        if name in no_navigations:
            header = """---\nhide:\n  - navigation\n---\n\n"""
        content = header + "".join(content)
        with open(destpath, "w") as f:
            f.writelines(content)


if __name__ == "__main__":
    copy_files()
