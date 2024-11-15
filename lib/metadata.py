import os
import json
import subprocess
from typing import Dict, List


class StepMetadata:
    entity_count_before: int
    entity_count_after: int
    relation_count_before: int
    relation_count_after: int

    def __init__(
        self,
        entity_count_before: int,
        entity_count_after: int,
        relation_count_before: int,
        relation_count_after: int,
    ):
        self.entity_count_before = entity_count_before
        self.entity_count_after = entity_count_after
        self.relation_count_before = relation_count_before
        self.relation_count_after = relation_count_after

    # Make the class serializable
    def to_dict(self) -> Dict:
        return self.__dict__


class Step:
    note: str
    metadata: StepMetadata

    def __init__(self, note: str, metadata: StepMetadata):
        self.note = note
        self.metadata = metadata

    # Make the class serializable
    def to_dict(self) -> Dict:
        return {
            "note": self.note,
            "metadata": self.metadata.to_dict(),
        }


class DatasetMetadata:
    repo_commit_id: str | None = None
    repo_path: str | None = None
    dataset_name: str | None = None
    dataset_version: str | None = None
    # data_files is a dictionary where the key is the file name and the value is the md5 hash of the file
    data_files: Dict[str, str] | None = None
    # metadata is a dictionary that contains any other metadata information that is not covered by the other fields
    steps: List[Step] = []
    filepath: str | None = None

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
        # Remove prefixes which are same for all files
        common_prefix = os.path.commonprefix(data_files)

        def remove_prefix(file_path: str, prefix: str):
            return (
                file_path[len(prefix) :] if file_path.startswith(prefix) else file_path
            )

        self.data_files = {
            remove_prefix(file, common_prefix): calc_md5sum(file) for file in data_files
        }
        self.metadata = metadata
        self.filepath = None
        self.steps = []

    def to_json(self, file_path: str):
        self.filepath = file_path

        with open(file_path, "w") as f:
            _dict = self.__dict__.copy()
            _dict["steps"] = [step.to_dict() for step in self.steps]
            del _dict["filepath"]

            f.write(json.dumps(_dict))

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

    def count_lines(self, file_path: str) -> int:
        result = subprocess.run(["wc", "-l", file_path], capture_output=True, text=True)
        return int(result.stdout.split()[0])

    def add_step(
        self,
        note: str,
        entity_file_before: str | None = None,
        entity_file_after: str | None = None,
        relation_file_before: str | None = None,
        relation_file_after: str | None = None,
    ) -> None:
        step_metadata = StepMetadata(
            entity_count_before=self.count_lines(entity_file_before) if entity_file_before else 0,
            entity_count_after=self.count_lines(entity_file_after) if entity_file_after else 0,
            relation_count_before=self.count_lines(relation_file_before) if relation_file_before else 0,
            relation_count_after=self.count_lines(relation_file_after) if relation_file_after else 0,
        )

        self.steps.append(Step(note=note, metadata=step_metadata))

        if self.filepath and os.path.exists(self.filepath):
            self.to_json(self.filepath)


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
