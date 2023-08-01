1. Download the latest CTDbase from [here](http://ctdbase.org/downloads/) and extract the files into `data` directory.

```bash
cd databases/ctd
bash download.sh
```

2. Run the following command to format the data.

```bash
python format_ctd.py extract-all-entities --base-dir data --output-dir output/
```

```bash
python format_ctd.py extract-all-relationships --base-dir data --output-dir output/relationships
```