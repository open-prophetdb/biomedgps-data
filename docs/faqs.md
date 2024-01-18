---
hide:
  - navigation
---

## FAQs and Steps

1. How to prepare a full list of all ontology terms used in the real world? [Complete Ontology List]

    More details on https://github.com/yjcyxky/biomedical-knowledgebases. Keep curating ontology terms from different databases / papers and integrate them into a full list.

    If we found a new database which contains new terms, we can download the database and format it into our standard format (more details on `graph_data/databases` directory), then we can use the `ontology-matcher` to match the new terms with the full list. If some of the items are not in the full list, they will be added into the full list.

2. How to deal with the terms from different databases but with the same meaning? [ID Integration / Reconciliation]

    Dealing with the same meaning terms from different databases is a very important issue in the knowledge integration. More details on https://github.com/yjcyxky/ontology-matcher

3. How to integrate knowledges from different databases? [ID Mapping]

    More details on https://github.com/yjcyxky/biomedical-knowledgebases. Keep curating knowledges from different databases / papers and integrate them into our knowledge graph.

    If we found a new database which contains new knowledges, we can download the database and format it into our standard format (more details on `graph_data/databases` directory), then we can use the `ontology-matcher` to convert the start id and end id into our standard id. If these ids can be converted, we can add the new knowledges into our knowledge graph.

4. How to merge relationship types from different databases? [Relationship Mapping]

    Define a set of relationship types and map the relationship types from different databases to the set.

5. How to extract the knowledge from the literature? [Text Mining]

    More details on https://github.com/yjcyxky/text2knowledge