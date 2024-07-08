# InitDB
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli initdb

# Import Entities
export NEO4J_URL=neo4j://neo4j:password@localhost:7600 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli importdb -D rapex-postgresql-ml:5432 -f /data/rapex/datasets/rapex-20240618/annotated_entities.filtered.tsv -t entity --drop

# Build Entity Metadata
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli --debug importdb -t entity_metadata

# Import Relations
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && bin/biomedgps-cli --debug importdb --annotation-file /data/rapex/datasets/rapex-20240618/relation_types.tsv --dataset PrimeKG -f /data/rapex/datasets/rapex-20240618/formatted_primekg.filtered.tsv -t relation --drop

export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && bin/biomedgps-cli --debug importdb --annotation-file /data/rapex/datasets/rapex-20240618/relation_types.tsv --dataset DRKG -f /data/rapex/datasets/rapex-20240618/formatted_drkg.tsv -t relation --drop

export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && bin/biomedgps-cli --debug importdb --annotation-file /data/rapex/datasets/rapex-20240618/relation_types.tsv --dataset HSDN -f /data/rapex/datasets/rapex-20240618/formatted_hsdn.tsv -t relation --drop

export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && bin/biomedgps-cli --debug importdb --annotation-file /data/rapex/datasets/rapex-20240618/relation_types.tsv --dataset CTD -f /data/rapex/datasets/rapex-20240618/formatted_ctd.filtered.tsv -t relation --drop

# Build Entity Metadata
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli --debug importdb -t relation_metadata -f /data/rapex/datasets/rapex-20240618/relation_types.tsv

# Import KGE model
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli --debug importkge --annotation-file /data/rapex/datasets/rapex-20240618/relation_types.tsv --dataset CTD --dataset PrimeKG --dataset HSDN --dataset DRKG --entity-embedding-file /data/rapex/datasets/rapex-20240618/entity_embeddings.tsv --metadata-file /data/rapex/datasets/rapex-20240618/metadata.json --model-type ComplEx --relation-embedding-file /data/rapex/datasets/rapex-20240618/relation_type_embeddings.tsv --dataset-name biomedgps --dimension 1024 --force --drop

# Cache Table
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli cachetable --relation-types BioMedGPS::Treatment::Compound:Disease,BioMedGPS::Present::Disease:Symptom --table compound-disease-symptom
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli cachetable --relation-types BioMedGPS::Causer::Gene:Disease,BioMedGPS::Present::Disease:Symptom --table gene-disease-symptom
export NEO4J_URL=neo4j://neo4j:password@localhost:7687 && export DATABASE_URL=postgres://postgres:password@localhost:5432/rapex && /data/rapex/bin/biomedgps-cli cachetable --table knowledge-score --db-host rapex-postgresql-ml:5432