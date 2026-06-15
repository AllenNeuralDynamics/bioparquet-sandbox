# bioparquet

A PyArrow Parquet implementation of the **foundingGIDE** (Global Image Data
Exchange) bioimaging metadata standard. The schema is derived from
[`foundingGIDE_metadata_fields.md`](foundingGIDE_metadata_fields.md).

## Model

One row = one dataset/study. The metadata *components* become 22 top-level
columns:

- **Controlled-vocabulary** fields use a reusable `ontology_term` struct
  (`ontology_source`, `term_id`, `term_label`) so the source ontology
  (FBbi, NCBI Taxonomy, ChEBI, MONDO, UBERON, …) is preserved.
- **Repeatable** components (authors, organisms, genes, imaging methods, …)
  are `list<…>`.
- **Channels** are a single `channels` list of a `channel` struct, pairing the
  channel `content` (FBbi `ontology_term`) with its `biological_entity`
  (Experimental Factor Ontology term + UniProt ID).
- `release_date` is a timezone-aware `timestamp` (ISO 8601 with time/zone).
- Each field carries the original Description / Format / Access Query from the
  metadata spec as Arrow field metadata, so the Parquet file is self-documenting.

## Usage

```bash
uv run bioparquet_schema.py
```

This prints the schema and writes `bioparquet_metadata.parquet` — an empty,
schema-only template you can append rows to.

Import the schema directly:

```python
from bioparquet_schema import BIOPARQUET_SCHEMA
```

## Example

```bash
uv run example_table.py
```

`example_table.py` populates every component with a realistic dataset row
(a fictional human iPSC cardiomyocyte live-imaging study), writes it to
`bioparquet_example.parquet`, and reads it back to confirm the data validates
against `BIOPARQUET_SCHEMA`. It also serves as a reference for how to construct
rows — nested structs as plain dicts, repeatable components as lists:

```python
import pyarrow as pa
from bioparquet_schema import BIOPARQUET_SCHEMA

table = pa.table(ROWS, schema=BIOPARQUET_SCHEMA)  # validates against the schema
```
