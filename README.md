# bioparquet-sandbox

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/python->=3.10-blue?logo=python)

A PyArrow Parquet implementation of the **foundingGIDE** (Global Image Data
Exchange) bioimaging metadata standard. The schema is derived from
[`foundingGIDE_metadata_fields.md`](resources/foundingGIDE_metadata_fields.md).

## Installation
To use the software, in the root directory, run
```bash
pip install -e .
```

To develop the code, run
```bash
pip install -e . --group dev
```
Note: --group flag is available only in pip versions >=25.1

Alternatively, if using [uv](https://docs.astral.sh/uv/), run
```bash
uv sync
```

## Model

One row = one data asset (a study is composed of many data assets, so `study_id`
repeats across them). The metadata *components* become 22 top-level columns:

- **Controlled-vocabulary** fields use a reusable `ontology_term` struct
  (`ontology_source`, `term_id`, `term_label`) so the source ontology
  (FBbi, NCBI Taxonomy, ChEBI, MONDO, UBERON, …) is preserved.
- **Repeatable** components (authors, organisms, genes, acquisition methods, …)
  are `list<…>`.
- **Channels** are a single `channels` list of a `channel` struct, pairing the
  `probe` (the label/reagent applied or expressed) with the `target` (the
  biological molecule or structure detected) — each an `ontology_term`.
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

[`foundingGIDE_metadata_fields.md`](resources/foundingGIDE_metadata_fields.md) mirrors the
standard verbatim. The schema deliberately renames a few components for clearer,
collision-free column names — the descriptions still carry the original wording:

| Spec component | Schema column | Note |
| --- | --- | --- |
| Study Description | `description` | Describes the data asset (the row grain), not the study. |
| Imaging Method | `acquisition_methods` | Generalized beyond imaging; still FBbi/EDAM ontology terms. |
| Organ | `anatomical_location` | Generalized beyond organs; still UBERON/RadLex terms. |
| Study Unique ID | `study_id` | Dropped "unique" from the name. |
| Dataset Unique ID | `data_asset_id` | "Dataset" → "data asset"; dropped "unique". |
| _(none)_ | `organisms.organism_id` | Added a unique identifier for the organism (the spec has none); named to match the `study_id`/`data_asset_id` convention (no "unique" in the name). |
| Organism | `organisms.additional_metadata` | Added a JSON field (Arrow's `arrow.json`) for free-form organism metadata (strain, sex, developmental stage, BioSample attributes, …) beyond the spec's taxon/geographic fields. Requires pyarrow ≥ 19. |
| Analyzed Data → Dataset ID | `derived_data.data_asset_id` | "Dataset" → "data asset". |
| Channel – Content + Channel – Biological Entity | `channels` | Merged the two channel components into one `probe`/`target` entity (see below). |
| Dimension + Pixel/Voxel Size/Time resolution | `axes` | Merged the two per-axis components into one entity (see below). |
| Analyzed Data | `processing` + `derived_data` | Split the grab-bag component into two coherent entities (see below). |

The grain follows from this: one row per **data asset**, with `study_id`
repeating across the data assets that belong to the same study.

The spec lists two separate channel components — *Channel – Content* and
*Channel – Biological Entity* — but they describe the same thing: a channel. We
model a channel as a single `channel` struct with two `ontology_term` fields —
`probe` (the label/reagent applied or expressed) and `target` (the biological
molecule or structure detected) — exposed as `channels: list<channel>`. This
keeps a channel's probe and target together as one entity instead of two
parallel, position-coupled lists.

Similarly, the spec's *Dimension* and *Pixel/Voxel Size/Time resolution*
components are both keyed per axis. We model an axis as a single `axis` struct
combining its identity and extent (`name`, `type`, `size`) with its physical
`spacing` and `unit`, exposed as `axes: list<axis>`. `spacing`/`unit` are null
for axes that have no resolution (e.g. the channel axis).

Conversely, the spec's *Analyzed Data* component is a grab-bag — it mixes the
software/workflow that produced a result with the derived/annotation data
products themselves, so any single row leaves most fields null and can't say
what it describes. We split it by *direction* relative to the current row:
`processing` (`name`, `url`, `rrid`, `version`) records what produced
**this** data asset (e.g. the compression applied on write), while
`derived_data` (`name`, `doi`, `data_asset_id`) points to separate data assets
derived **from** this one. A derived asset describes its own `processing` in its
own row, so the producing step lives with the asset it produced — not here.

## Usage

Print the schema and write `bioparquet_metadata.parquet` — an empty,
schema-only template you can append rows to:

```bash
uv run python -m bioparquet_sandbox.schema
```

Import the schema directly:

```python
from bioparquet_sandbox.schema import BIOPARQUET_SCHEMA
```

Build the example table (a fictional human iPSC cardiomyocyte live-imaging
study), write it to `resources/bioparquet_example.parquet`, and read it back
to confirm it validates against `BIOPARQUET_SCHEMA`:

```bash
uv run python -m bioparquet_sandbox.example
```

`example.py` also serves as a reference for how to construct rows — nested
structs as plain dicts, repeatable components as lists, JSON fields as JSON
strings:

```python
from bioparquet_sandbox.schema import build_table

# build_table types the data as BIOPARQUET_SCHEMA, handling arrow.json fields
# (supply them as JSON strings).
table = build_table(ROWS)
```

## Level of Support
Please indicate a level of support:
 - [ ] Supported: We are releasing this code to the public as a tool we expect others to use. Issues are welcomed, and we expect to address them promptly; pull requests will be vetted by our staff before inclusion.
 - [x] Occasional updates: We are planning on occasional updating this tool with no fixed schedule. Community involvement is encouraged through both issues and pull requests.
 - [ ] Unsupported: We are not currently supporting this code, but simply releasing it to the community AS IS but are not able to provide any guarantees of support. The community is welcome to submit issues, but you should not expect an active response.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for linting, testing, and documentation
guidelines.
