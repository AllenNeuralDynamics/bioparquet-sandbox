# bioparquet schema

_Generated from `BIOPARQUET_SCHEMA` in `src/bioparquet_sandbox/schema.py` by `bioparquet_sandbox.visualize`. Do not edit by hand — run `python -m bioparquet_sandbox.visualize`._

One row = one data asset. 22 top-level components.

## description

`string`

Description of the data asset

- **Format:** Text
- **Access query:** Free text

## authors

`list<struct>`

Information about the authors

- **Format:** Name; Affiliation, ORCID
- **Access query:** Author name, ORCID, CRediT, Organization name, ROR

**Fields:**

- `name` `string`
- `orcid` `string`
- `credit_roles` `list<string>`
- `organization_name` `string`
- `ror` `string`

## organizations

`list<struct>`

Information about the organization

- **Format:** Name URL, ROR
- **Access query:** Name, ROR

**Fields:**

- `name` `string`
- `url` `string`
- `ror` `string`

## publications

`list<struct>`

Information on the related publication

- **Format:** Text (Title), Publication year, DOI (Journal)
- **Access query:** DOI

**Fields:**

- `title` `string`
- `year` `int16`
- `doi` `string`
- `journal` `string`

## license

`struct`

Information about the data asset's license

- **Format:** Creative Commons with the version and URL
- **Access query:** CC version, URL

**Fields:**

- `name` `string`
- `url` `string`

## release_date

`timestamp[us, tz=UTC]`

The release date of the data

- **Format:** ISO 8601 format (including time/time zone)
- **Access query:** Release date, range search

## acquisition_methods

`list<struct>`

The method used to acquire the data

- **Format:** FBbi, EDAM Bioimaging Ontology term and ID
- **Access query:** FBbi or EDAM Bioimaging Ontology ID, term

**Fields:**

- `ontology_source` `string`
- `term_id` `string`
- `term_label` `string`

## cell_lines

`list<struct>`

Information about the cell line

- **Format:** Cell Line Ontology term and ID
- **Access query:** CLO ID, term

**Fields:**

- `term_id` `string`
- `term_label` `string`

## organisms

`list<struct>`

Information about the organism studied

- **Format:** NCBI Taxonomy term and ID, BioSample (geographic location)
- **Access query:** NCBI Taxonomy ID, term

**Fields:**

- `organism_id` `string`
- `ncbi_taxon_id` `string`
- `term_label` `string`
- `geographic_location` `string`
- `additional_metadata` `arrow.json`

## genes

`list<struct>`

Information about related genes

- **Format:** Ensembl Gene or NCBI Gene name or ID
- **Access query:** Gene ID, name

**Fields:**

- `source` `string`
- `gene_id` `string`
- `gene_name` `string`

## compounds

`list<struct>`

Information about the compound

- **Format:** ChEBI or PubChem term and ID
- **Access query:** Compound ID, term

**Fields:**

- `ontology_source` `string`
- `term_id` `string`
- `term_label` `string`

## antibodies

`list<struct>`

Information about the antibody used

- **Format:** FBbi or ChEBI term and ID, RRID
- **Access query:** Antibody ID, term

**Fields:**

- `ontology_source` `string`
- `term_id` `string`
- `term_label` `string`
- `rrid` `string`

## channels

`list<struct>`

Information about the channels (probe and target)

- **Format:** Ontology term and ID for the probe and the target
- **Access query:** Probe ID/term, Target ID/term

**Fields:**

- `probe` `struct` — The label/reagent applied or expressed
  - `ontology_source` `string`
  - `term_id` `string`
  - `term_label` `string`
- `target` `struct` — The biological molecule or structure detected
  - `ontology_source` `string`
  - `term_id` `string`
  - `term_label` `string`

## instrument

`struct`

Information about the instrument used

- **Format:** Compliant with 4DN-BINA-OME-QUAREP (NBO-Q) standards, PIDInst
- **Access query:** Instrument name, ID

**Fields:**

- `name` `string`
- `description` `string`
- `additional_metadata` `arrow.json`

## axes

`list<struct>`

Information about data dimensions, including pixel/voxel size and time interval

- **Format:** Compliant with OME-Zarr axes info. (T, C, Z, Y, X); pixel/voxel size and time interval stored with units
- **Access query:** Dimension specification, Pixel/voxel size, Time interval

**Fields:**

- `name` `string`
- `type` `string`
- `size` `int64`
- `spacing` `double`
- `unit` `string`

## study_id

`struct`

Unique ID for the study

- **Format:** Accession ID, DOI
- **Access query:** Accession ID, DOI

**Fields:**

- `accession_id` `string`
- `doi` `string`

## data_asset_id

`string`

Unique ID for the data asset

- **Format:** Accession ID
- **Access query:** Accession ID

## pathology_disease

`list<struct>`

Pathology/Disease related to the biological entity

- **Format:** SNOMED-CT, DOID, ICD-11 or MONDO
- **Access query:** Pathology/Disease ID, term

**Fields:**

- `ontology_source` `string`
- `term_id` `string`
- `term_label` `string`

## phenotype

`list<struct>`

Phenotypic data related to the analysis

- **Format:** Cell Morphology Phenotype Ontology, MPO, or HPO
- **Access query:** Phenotype ID, term

**Fields:**

- `ontology_source` `string`
- `term_id` `string`
- `term_label` `string`

## anatomical_location

`list<struct>`

Information about anatomical entities

- **Format:** UBERON, RadLex Ontology
- **Access query:** UBERON ID, term

**Fields:**

- `ontology_source` `string`
- `term_id` `string`
- `term_label` `string`

## processing

`list<struct>`

Software/workflow that produced this data asset

- **Format:** Name, URL (e.g. source repo or release), RRID, version
- **Access query:** Name, RRID

**Fields:**

- `name` `string`
- `url` `string`
- `rrid` `string`
- `version` `string`

## derived_data

`list<struct>`

Data assets derived from this one (each describes its own processing)

- **Format:** Name, DOI (Zenodo, Figshare), Data asset ID
- **Access query:** Name, DOI

**Fields:**

- `name` `string`
- `doi` `string`
- `data_asset_id` `string`
