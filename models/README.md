## ID Format

### Entity ID

We use `entity_id` to represent an entity. It is a string of the following format:

```
<entity_type>:<database_id>
```

such as `Gene::ENTREZ:1234`, `Disease::OMIM:1234`, `Drug::DRUGBANK:DB1234`.

### Relation ID

We use `relation_id` to represent a relation. It is a string of the following format:

```
<resource>::<relation_type>::<source_entity_type>:<target_entity_type>
```

such as `STRING::INTERACTS_WITH::Gene:Gene`, `STRING::INTERACTS_WITH::Gene:Disease`.

## Data Format

### Entity File

### Relation File

## Directory Structure