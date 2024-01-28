## Benchmark dataset description
**Full-DTIs-LC-Benchmark**
A benchmark dataset containing Drug-Target Interation (DTI) data of Lung Cancer (LC). This dataset avoided information that is only generated automatically, through text mining, and focused on most trustworthy sources, namely DrugBank, KEGG, DGIdb and TTD data. The union of DrugBank, KEGG, DGIdb and TTD provided 44,169 positive drug-gene interactions in total, with 1931 of those related on one side (drug) or the other (gene) to Lung Cancer (LC). As for the negative drug-gene pairs, there are 627,971 pairs, for which no interaction is reported in any of the above databases.

- [Paper](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-023-05373-2)
- [Code](https://github.com/fotais/drug-gene-interactions/tree/main)
- [Data](https://github.com/fotais/drug-gene-interactions/blob/main/Full-DTIs-LC-Benchmark.csv)

## Add evaluation metrics
Here, MRR is the default metric. If you want to add new evaluation metrics, please define a function containing the following arguments:
- _predicts:dict_, prediction results
- _positives:dict_, positive relationships of benchmark dataset
- _negatives:dict_, negative relationships of benchmark dataset
- other arguments if needed.

When call **lc.evaluate** with the prediction results, _positives_ and _negatives_ are automatically passed by benchmark.

As an example, we added hits@k for k=10,000.
