### Dataset

You can use the following commands to prepare the training/validation/test datasets. 

- Merge all formatted relation files into a single file, such as `formatted_relations.tsv`

    ```bash
    # Merge formatted relation files in the formatted_relations folder into one file
    python graph_data/scripts/merge_relations.py -i graph_data/formatted_relations -o graph_data/relations.tsv

    # Or merge a set of formatted relation files into one file
    python lib/data.py merge-files --input graph_data/formatted_relations/drkg/formatted_drkg.tsv --input graph_data/formatted_relations/ctd/formatted_ctd.tsv --input graph_data/formatted_relations/hsdn/formatted_hsdn.tsv --input datasets/custom/formatted_custom_all_v20240119.tsv --output datasets/formatted_relations.tsv
    ```

- Convert the relations file into the hrt format, such as `formatted_relations.tsv` to `formatted_relations_hrt.tsv`

    ```bash
    python lib/data.py hrt --input datasets/formatted_relations.tsv --output datasets/formatted_relations_hrt.tsv

    python lib/data.py hrt --input graph_data/formatted_relations/drkg/unformatted_drkg.tsv --output datasets/unformatted_drkg_hrt.tsv
    ```

- Split `formatted_relations_hrt.tsv` into train/test files, such as `train_hrt.tsv` and `test_hrt.tsv`

    ```bash
    python lib/data.py split --input datasets/formatted_relations_hrt.tsv --output-1 datasets/train_hrt.tsv --output-2 datasets/test_hrt.tsv --ratio 0.95
    ```

- Merge `train_hrt.tsv` and other formatted & unformatted files into `train_hrt.tsv`

    ```bash
    cat datasets/train_hrt.tsv datasets/unformatted_drkg_hrt.tsv > datasets/train_hrt.tsv
    ```

- Split `train_hrt.tsv` into `train.tsv` and `valid.tsv`

    ```bash
    python lib/data.py split --input datasets/train_hrt.tsv --output-1 datasets/train.tsv --output-2 datasets/valid.tsv --ratio 0.95
    ```

- Copy the `test_hrt.tsv` to `test.tsv`

    ```bash
    cp datasets/test_hrt.tsv datasets/test.tsv
    ```

### Example

The [prepare_data.ipynb](../datasets/prepare_data.ipynb) is an example to prepare a training dataset for the KGE model.
