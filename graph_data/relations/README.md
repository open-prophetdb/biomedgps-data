## For Users
### Download all databases and put them in the `graph_data/relations` folder

```bash
graph_data/relations
    |-- ctd
    |-- drkg
    |-- hmdb
    |-- hsdn
    |-- primekg
```

### Format the databases

We have already implemented a python package [graph-builder](https://github.com/open-prophetdb/graph-builder) to download, extract, format and build the knowledge graph from the several databases, such as [ctd](http://ctdbase.org/), [drkg](https://github.com/gnn4dr/DRKG), [hsdn](https://www.nature.com/articles/ncomms5212), [primekg](https://github.com/mims-harvard/PrimeKG) etc.

If you want to build a knowledge graph for BioMedGPS project step by step by yourself, you can follow the instructions in the [KG_README.md](./graph_data/KG_README.md) file.


## For Developers

### How to add a new database

If you want to add a new database to the knowledge graph, you need to finish the following two steps:

1. Create a new folder in the `graph_data/relations` folder, and write a main.ipynb files to introduce the database and show how to extract/convert the database to the BioMedGPS format.

    > You need to write codes to download, extract, convert the database to the BioMedGPS format in the main.ipynb file. You can refer to the existing main.ipynb files in the `graph_data/relations` folder as examples.
    > 
    > The main.ipynb file should read the raw data from the database and write the processed data to the database folder in the BioMedGPS format. The output files should be named as `processed_xxx.tsv` or `invalid_xxx.tsv`, where `xxx` is the name of the database. These files will be added to the git repository.
    > 
    > Also, if possible, you can write descriptions about the database, the data source, the data license, the data usage, etc. in the main.ipynb file.

2. Add a new parser in the `graph-builder` package to mapping the entities and relation_types in the new database to the entities.tsv and relation_types.tsv files that are used in the BioMedGPS project.

