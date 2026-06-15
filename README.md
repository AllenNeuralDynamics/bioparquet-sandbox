# foundingGIDE metadata — Parquet schema

A PyArrow Parquet schema derived from `foundingGIDE_metadata_fields.xlsx`
(sheet *GIDE Metadata Fields*), the founding Global Image Data Exchange (GIDE)
bioimaging metadata specification.

## Model

One row = one dataset/study. Each of the 23 spreadsheet *components* becomes a
top-level column:

- **Controlled-vocabulary** fields use a reusable `ontology_term` struct
  (`ontology_source`, `term_id`, `term_label`) so the source ontology
  (FBbi, NCBI Taxonomy, ChEBI, MONDO, UBERON, …) is preserved.
- **Repeatable** components (authors, organisms, genes, imaging methods, …)
  are `list<…>`.
- `release_date` is a timezone-aware `timestamp` (ISO 8601 with time/zone).
- Each field carries the original spreadsheet Description / Format / Access
  Query as Arrow field metadata, so the Parquet file is self-documenting.

## Usage

```bash
uv run gide_schema.py
```

This prints the schema and writes `gide_metadata.parquet` — an empty,
schema-only template you can append rows to.

Import the schema directly:

```python
from gide_schema import GIDE_SCHEMA
```

## Example

```bash
uv run example_table.py
```

`example_table.py` populates every component with a realistic dataset row
(a fictional human iPSC cardiomyocyte live-imaging study), writes it to
`gide_example.parquet`, and reads it back to confirm the data validates
against `GIDE_SCHEMA`. It also serves as a reference for how to construct
rows — nested structs as plain dicts, repeatable components as lists:

```python
import pyarrow as pa
from gide_schema import GIDE_SCHEMA

table = pa.table(ROWS, schema=GIDE_SCHEMA)  # validates against the schema
```
