# bioparquet

A PyArrow Parquet implementation of the **foundingGIDE** (Global Image Data
Exchange) bioimaging metadata standard. The schema is derived from
[`foundingGIDE_metadata_fields.md`](foundingGIDE_metadata_fields.md).

## Model

One row = one data asset (a study is composed of many data assets, so `study_id`
repeats across them). The metadata *components* become 22 top-level columns:

- **Controlled-vocabulary** fields use a reusable `ontology_term` struct
  (`ontology_source`, `term_id`, `term_label`) so the source ontology
  (FBbi, NCBI Taxonomy, ChEBI, MONDO, UBERON, …) is preserved.
- **Repeatable** components (authors, organisms, genes, imaging methods, …)
  are `list<…>`.
- **Channels** are a single `channels` list of a `channel` struct, pairing the
  channel `content` (FBbi `ontology_term`) with its `biological_entity`
  (an EFO `ontology_term` plus a `uniprot_id` cross-reference).
- **Axes** are a single `axes` list of an `axis` struct, carrying each axis's
  identity/extent (`name`, `type`, `size`) together with its physical `spacing`
  and `unit`.
- **Instrument** is a `struct<name, description, additional_metadata>`, where
  `additional_metadata` is a JSON document (Arrow's canonical `arrow.json`
  extension type) for free-form, instrument-specific fields (PIDInst, objective,
  lasers, …). Requires pyarrow ≥ 19.
- `release_date` is a timezone-aware `timestamp` (ISO 8601 with time/zone).
- Each field carries the original Description / Format / Access Query from the
  metadata spec as Arrow field metadata, so the Parquet file is self-documenting.

## Deviations from the spec

[`foundingGIDE_metadata_fields.md`](foundingGIDE_metadata_fields.md) mirrors the
standard verbatim. The schema deliberately renames a few components for clearer,
collision-free column names — the descriptions still carry the original wording:

| Spec component | Schema column | Note |
| --- | --- | --- |
| Study Description | `description` | Describes the data asset (the row grain), not the study. |
| Study Unique ID | `study_id` | Dropped "unique" from the name. |
| Dataset Unique ID | `data_asset_id` | "Dataset" → "data asset"; dropped "unique". |
| Analyzed Data → Dataset ID | `derived_data.data_asset_id` | "Dataset" → "data asset". |
| Channel – Content + Channel – Biological Entity | `channels` | Merged the two channel components into one entity (see below). |
| Dimension + Pixel/Voxel Size/Time resolution | `axes` | Merged the two per-axis components into one entity (see below). |
| Analyzed Data | `processing` + `derived_data` | Split the grab-bag component into two coherent entities (see below). |

The grain follows from this: one row per **data asset**, with `study_id`
repeating across the data assets that belong to the same study.

The spec lists two separate channel components — *Channel – Content* and
*Channel – Biological Entity* — but they describe the same thing: an imaging
channel. We model a channel as a single `channel` struct that pairs `content`
(FBbi `ontology_term`) with `biological_entity` (an EFO `ontology_term` plus a
`uniprot_id` cross-reference), and expose the repeatable column as `channels:
list<channel>`. This keeps a channel's content and biological entity together as
one entity instead of two parallel, position-coupled lists.

Similarly, the spec's *Dimension* and *Pixel/Voxel Size/Time resolution*
components are both keyed per axis. We model an axis as a single `axis` struct
combining its identity and extent (`name`, `type`, `size`) with its physical
`spacing` and `unit`, exposed as `axes: list<axis>`. `spacing`/`unit` are null
for axes that have no resolution (e.g. the channel axis).

Conversely, the spec's *Analyzed Data* component is a grab-bag — it mixes the
software/workflow that produced a result with the derived/annotation data
products themselves, so any single row leaves most fields null and can't say
what it describes. We split it by *direction* relative to the current row:
`processing` (`name`, `github_url`, `rrid`, `version`) records what produced
**this** data asset (e.g. the compression applied on write), while
`derived_data` (`name`, `doi`, `data_asset_id`) points to separate data assets
derived **from** this one. A derived asset describes its own `processing` in its
own row, so the producing step lives with the asset it produced — not here.

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

`example_table.py` populates every component with a realistic data asset row
(a fictional human iPSC cardiomyocyte live-imaging study), writes it to
`bioparquet_example.parquet`, and reads it back to confirm the data validates
against `BIOPARQUET_SCHEMA`. It also serves as a reference for how to construct
rows — nested structs as plain dicts, repeatable components as lists, JSON
fields as JSON strings:

```python
from bioparquet_schema import build_table

# build_table types the data as BIOPARQUET_SCHEMA, handling arrow.json fields
# (supply them as JSON strings).
table = build_table(ROWS)
```
