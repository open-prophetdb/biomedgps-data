import os
import json
import subprocess
from typing import Dict


class DatasetMetadata:
    repo_commit_id: str | None = None
    repo_path: str | None = None
    dataset_name: str | None = None
    dataset_version: str | None = None
    # data_files is a dictionary where the key is the file name and the value is the md5 hash of the file
    data_files: Dict[str, str] | None = None
    # metadata is a dictionary that contains any other metadata information that is not covered by the other fields

    def __init__(
        self,
        repo_commit_id: str,
        repo_path: str,
        dataset_name: str,
        dataset_version: str,
        data_files: list[str],
        metadata: Dict | None = None,
    ):
        self.repo_commit_id = repo_commit_id
        self.repo_path = repo_path
        self.dataset_name = dataset_name
        self.dataset_version = dataset_version
        self.data_files = {
            os.path.basename(file): calc_md5sum(file) for file in data_files
        }
        self.metadata = metadata

    def to_json(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(json.dumps(self.__dict__))

    @staticmethod
    def _from_json(json_str: str) -> "DatasetMetadata":
        obj = json.loads(json_str)
        return DatasetMetadata(
            repo_commit_id=obj["repo_commit_id"],
            repo_path=obj["repo_path"],
            dataset_name=obj["dataset_name"],
            dataset_version=obj["dataset_version"],
            data_files=obj["data_files"],
            metadata=obj["metadata"],
        )

    @staticmethod
    def from_json(file_path: str) -> "DatasetMetadata":
        with open(file_path, "r") as f:
            return DatasetMetadata._from_json(f.read())


def check_repo_clean(file_suffix: str = ".py", raise_error: bool = True) -> list[str]:
    # Check if the repository is clean
    # If the repository is not clean, return a list of modified files
    status_result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    modified_files = status_result.stdout.splitlines()

    if file_suffix != ".py":
        python_files = [
            line[3:] for line in modified_files if line.endswith(file_suffix)
        ]
    else:
        python_files = [line[3:] for line in modified_files if line.endswith(".py")]

    if raise_error and len(python_files) > 0:
        raise Exception(
            f"Repository is not clean. The following files are modified:\n{python_files}. If you want to do the next step, please commit the changes."
        )

    return python_files


def calc_md5sum(file_path: str) -> str:
    if not file_path:
        raise ValueError("file_path is empty or None")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Calculate the md5 hash of a file
    md5_result = subprocess.run(["md5sum", file_path], capture_output=True, text=True)
    return md5_result.stdout.split()[0]
