## Download all databases and put them in the `graph_data/relations` folder

```bash
graph_data/relations
    |-- ctd
    |-- drkg
    |-- hmdb
    |-- hsdn
    |-- primekg
```

We have already implemented a python package [graph-builder](https://github.com/open-prophetdb/graph-builder) to download, extract, format and build the knowledge graph from the above databases [ctd](http://ctdbase.org/), [drkg](https://github.com/gnn4dr/DRKG), [hsdn](https://www.nature.com/articles/ncomms5212), [primekg](https://github.com/mims-harvard/PrimeKG).

TODO: Add the [hmdb](https://hmdb.ca/) database.

If you want to build a knowledge graph for BioMedGPS project step by step by yourself, you can follow the instructions in the [KG_README.md](./graph_data/KG_README.md) file.