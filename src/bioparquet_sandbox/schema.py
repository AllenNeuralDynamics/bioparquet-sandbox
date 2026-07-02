"""bioparquet: the foundingGIDE bioimaging metadata standard in Parquet.

The schema is derived 1:1 from ``resources/foundingGIDE_metadata_fields.md``.
Each row of
that table is a metadata *component*; here each component becomes one top-level
column of a single wide table whose grain is **one row per data asset**
(a study is composed of many data assets; ``study`` repeats across them).

Design notes
------------
* Most components reference a controlled vocabulary as a (term, id) pair, often
  with a named source ontology. These are modelled with the reusable
  ``ontology_term`` struct so the *which ontology* provenance is never lost.
* Components that can legitimately repeat (authors, genes, organisms,
  acquisition methods, ...) are modelled as ``list<...>`` rather than scalars.
* Free text -> ``string``; release date -> timezone-aware ``timestamp`` to
  honour the "ISO 8601 incl. time/time zone" format requirement.
* Field-level ``metadata`` carries the original Description / Format / Access
  Query text from the metadata spec so the Parquet file is self-documenting.
"""

from __future__ import annotations

import pyarrow as pa
import pyarrow.parquet as pq


def ontology_term(*, source: bool = True, rrid: bool = False) -> pa.DataType:
    """A controlled-vocabulary reference (optional source, id, label, rrid)."""
    fields = []
    if source:
        # e.g. "FBbi", "NCBI Taxonomy", "ChEBI", "MONDO" ...
        fields.append(pa.field("ontology_source", pa.string()))
    fields.append(pa.field("term_id", pa.string()))  # e.g. "NCBITaxon:9606"
    fields.append(pa.field("term_label", pa.string()))  # e.g. "Homo sapiens"
    if rrid:
        # Research Resource Identifier, e.g. an antibody's "AB_2532090".
        fields.append(pa.field("rrid", pa.string()))
    return pa.struct(fields)


def col(
    name: str, dtype: pa.DataType, *, description: str, fmt: str, query: str
) -> pa.Field:
    """Build a field with the spec's documentation attached as metadata."""
    return pa.field(
        name,
        dtype,
        nullable=True,
        metadata={
            "description": description,
            "format": fmt,
            "access_query": query,
        },
    )


# --- Reusable nested types -------------------------------------------------

author = pa.struct(
    [
        pa.field("name", pa.string()),
        pa.field("orcid", pa.string()),
        pa.field(
            "credit_roles", pa.list_(pa.string())
        ),  # CRediT contributor roles
        pa.field("organization_name", pa.string()),
        pa.field("ror", pa.string()),  # Research Organization Registry ID
    ]
)

organization = pa.struct(
    [
        pa.field("name", pa.string()),
        pa.field("url", pa.string()),
        pa.field("ror", pa.string()),
    ]
)

publication = pa.struct(
    [
        pa.field("title", pa.string()),
        pa.field("year", pa.int16()),
        pa.field("doi", pa.string()),
        pa.field("journal", pa.string()),
    ]
)

license_ = pa.struct(
    [
        pa.field(
            "name", pa.string()
        ),  # Creative Commons + version, e.g. "CC BY 4.0"
        pa.field("url", pa.string()),
    ]
)

organism = pa.struct(
    [
        pa.field("organism_id", pa.string()),  # Organism Unique ID
        pa.field("ncbi_taxon_id", pa.string()),
        pa.field("term_label", pa.string()),
        pa.field(
            "genotype",
            pa.string(),
            metadata={
                "description": (
                    "The organism's genetic background (strain, alleles, "
                    "reporter/tagged/knocked-out genes, edits)"
                )
            },
        ),
        pa.field(
            "geographic_location",
            pa.string(),
            metadata={
                "description": (
                    "The place on Earth (e.g. country/region, per BioSample) "
                    "where the organism was collected"
                )
            },
        ),
        pa.field(
            "pathology_disease",
            pa.list_(ontology_term()),  # SNOMED-CT / DOID / ICD-11 / MONDO
            metadata={
                "description": "Pathology/disease affecting the organism"
            },
        ),
        # Free-form extra fields (e.g. strain, sex, developmental stage,
        # BioSample attributes) as a JSON document.
        pa.field("additional_metadata", pa.json_()),
    ]
)

# The biological specimen / model system imaged. Generalizes the spec's "Cell
# Line" component beyond cell lines to any specimen (primary culture, tissue,
# organoid, ...), so ``specimen_type`` spans several ontologies (CLO, CL, BTO,
# OBI) and keeps the ontology source. Its ``anatomical_location`` is where in
# the organism the specimen was taken from (UBERON/RadLex) -- the same concept
# as the asset-level ``anatomical_location`` component (the region the data
# depicts), scoped to the specimen. ``genotype`` records modifications that
# define an engineered specimen (e.g. a reporter cell line), and ``treatments``
# the compounds applied to it (drugs, perturbations).
specimen = pa.struct(
    [
        pa.field("specimen_id", pa.string()),
        pa.field(
            "specimen_type",
            ontology_term(),  # CLO / CL / BTO / OBI
            metadata={
                "description": (
                    "The kind of biological material imaged (cell line, "
                    "cell type, tissue, organoid, ...)"
                )
            },
        ),
        pa.field(
            "anatomical_location",
            ontology_term(),  # UBERON / RadLex
            metadata={
                "description": (
                    "The anatomical site in the organism the specimen was "
                    "taken from"
                )
            },
        ),
        pa.field(
            "genotype",
            pa.string(),
            metadata={
                "description": (
                    "Genetic modifications defining the specimen (reporter, "
                    "tag, knock-in/out, edits)"
                )
            },
        ),
        pa.field(
            "treatments",
            pa.list_(ontology_term()),  # ChEBI / PubChem
            metadata={
                "description": (
                    "Compounds applied to the specimen as a "
                    "treatment/perturbation"
                )
            },
        ),
        pa.field(
            "protocol_doi",
            pa.string(),  # e.g. a protocols.io DOI
            metadata={
                "description": (
                    "DOI of the protocol describing how the specimen was "
                    "prepared"
                )
            },
        ),
        # Free-form extra fields (e.g. passage number, donor sex/age, disease
        # state, culture conditions) as a JSON document.
        pa.field("additional_metadata", pa.json_()),
    ]
)

# A single channel: the probe used to visualize and the target it detects,
# each a controlled-vocabulary term (probe from ChEBI/FBbi, target from
# UniProt/EFO/... -- hence the ontology source is kept). The probe also carries
# an ``rrid`` so an antibody-based probe records its Research Resource
# Identifier. The target may be a gene/transcript (Ensembl or NCBI Gene as the
# ontology source) when imaging gene expression (FISH, in situ hybridization,
# spatial transcriptomics). Data assets can have many channels.
channel = pa.struct(
    [
        pa.field(
            "probe",
            ontology_term(rrid=True),  # e.g. an antibody, with its RRID
            metadata={"description": "The label/reagent applied or expressed"},
        ),
        pa.field(
            "target",
            ontology_term(),  # UniProt/EFO protein, or Ensembl/NCBI gene
            metadata={
                "description": (
                    "The biological molecule or structure detected; a "
                    "gene/transcript (Ensembl/NCBI Gene) when imaging "
                    "gene expression"
                )
            },
        ),
    ]
)

instrument = pa.struct(
    [
        pa.field("name", pa.string()),  # 4DN-BINA-OME-QUAREP (NBO-Q) compliant
        pa.field("description", pa.string()),
        # Free-form extra fields (e.g. PIDInst, NBO-Q details) as a JSON
        # document.
        pa.field("additional_metadata", pa.json_()),
    ]
)

# OME-Zarr axis descriptor (T, C, Z, Y, X): one entry per axis combining its
# identity and extent (the spec's Dimension component) with its physical pixel/
# voxel spacing or time interval (the spec's Pixel/Voxel Size / Time resolution
# component). ``spacing``/``unit`` are null for axes without a resolution
# (e.g. the channel axis).
axis = pa.struct(
    [
        pa.field("name", pa.string()),  # "t" | "c" | "z" | "y" | "x"
        pa.field("type", pa.string()),  # "time" | "channel" | "space"
        pa.field("size", pa.int64()),  # number of elements along the axis
        pa.field("spacing", pa.float64()),  # pixel/voxel size or time interval
        pa.field("unit", pa.string()),  # e.g. "micrometer", "second"
    ]
)

study = pa.struct(
    [
        pa.field("accession_id", pa.string()),
        pa.field("doi", pa.string()),
    ]
)

# The spec's grab-bag "Analyzed Data" component is split by what is referenced:
# the software/workflow that produced THIS data asset (``processing``) vs. the
# separate data assets derived FROM it (``derived_data``). Each derived asset
# describes its own processing in its own row.
processing = pa.struct(
    [
        pa.field("name", pa.string()),
        pa.field("url", pa.string()),  # e.g. source repo or release URL
        pa.field(
            "rrid", pa.string()
        ),  # Research Resource Identifier (e.g. SCR_)
        pa.field("version", pa.string()),
    ]
)

derived_data = pa.struct(
    [
        pa.field("name", pa.string()),
        pa.field("doi", pa.string()),  # Zenodo / Figshare
        pa.field("data_asset_id", pa.string()),  # another data asset
    ]
)


# --- The bioparquet schema -------------------------------------------------

BIOPARQUET_SCHEMA = pa.schema(
    [
        col(
            "description",
            pa.string(),
            description="Description of the data asset",
            fmt="Text",
            query="Free text",
        ),
        col(
            "authors",
            pa.list_(author),
            description="Information about the authors",
            fmt="Name; Affiliation, ORCID",
            query="Author name, ORCID, CRediT, Organization name, ROR",
        ),
        col(
            "organizations",
            pa.list_(organization),
            description="Information about the organization",
            fmt="Name URL, ROR",
            query="Name, ROR",
        ),
        col(
            "publications",
            pa.list_(publication),
            description="Information on the related publication",
            fmt="Text (Title), Publication year, DOI (Journal)",
            query="DOI",
        ),
        col(
            "license",
            license_,
            description="Information about the data asset's license",
            fmt="Creative Commons with the version and URL",
            query="CC version, URL",
        ),
        col(
            "release_date",
            pa.timestamp("us", tz="UTC"),
            description="The release date of the data",
            fmt="ISO 8601 format (including time/time zone)",
            query="Release date, range search",
        ),
        col(
            "acquisition_methods",
            pa.list_(ontology_term()),  # FBbi / EDAM Bioimaging
            description="The method used to acquire the data",
            fmt="FBbi, EDAM Bioimaging Ontology term and ID",
            query="FBbi or EDAM Bioimaging Ontology ID, term",
        ),
        col(
            "specimens",
            pa.list_(specimen),  # CLO/CL/BTO/OBI (+ UBERON/RadLex origin)
            description=(
                "The biological specimen or model system imaged (cell line, "
                "primary culture, tissue, organoid, ...)"
            ),
            fmt=(
                "CLO, CL, BTO, or OBI term and ID; anatomical location "
                "(UBERON/RadLex); genotype; treatments (ChEBI/PubChem)"
            ),
            query="Specimen ID, type, anatomical location, treatment",
        ),
        col(
            "organisms",
            pa.list_(organism),
            description="Information about the organism studied",
            fmt="NCBI Taxonomy term and ID, BioSample (geographic location)",
            query="NCBI Taxonomy ID, term",
        ),
        col(
            "channels",
            pa.list_(channel),
            description="Information about the channels (probe and target)",
            fmt=(
                "Ontology term and ID for the probe (with RRID) and the "
                "target"
            ),
            query="Probe ID/term/RRID, Target ID/term",
        ),
        col(
            "instrument",
            instrument,
            description="Information about the instrument used",
            fmt=(
                "Compliant with 4DN-BINA-OME-QUAREP (NBO-Q) standards, "
                "PIDInst"
            ),
            query="Instrument name, ID",
        ),
        col(
            "axes",
            pa.list_(axis),
            description=(
                "Information about data dimensions, including pixel/voxel "
                "size and time interval"
            ),
            fmt=(
                "Compliant with OME-Zarr axes info. (T, C, Z, Y, X); "
                "pixel/voxel size and time interval stored with units"
            ),
            query="Dimension specification, Pixel/voxel size, Time interval",
        ),
        col(
            "study",
            study,
            description="The study this data asset belongs to",
            fmt="Accession ID, DOI",
            query="Accession ID, DOI",
        ),
        col(
            "data_asset_id",
            pa.string(),
            description="Unique ID for the data asset",
            fmt="Accession ID",
            query="Accession ID",
        ),
        col(
            "phenotype",
            pa.list_(ontology_term()),  # CMPO / MPO / HPO
            description="Phenotypic data related to the analysis",
            fmt="Cell Morphology Phenotype Ontology, MPO, or HPO",
            query="Phenotype ID, term",
        ),
        col(
            "anatomical_location",
            pa.list_(ontology_term()),  # UBERON / RadLex
            description="The anatomical region depicted by the data asset",
            fmt="UBERON, RadLex Ontology",
            query="UBERON ID, term",
        ),
        col(
            "processing",
            pa.list_(processing),
            description="Software/workflow that produced this data asset",
            fmt="Name, URL (e.g. source repo or release), RRID, version",
            query="Name, RRID",
        ),
        col(
            "derived_data",
            pa.list_(derived_data),
            description=(
                "Data assets derived from this one (each describes its "
                "own processing)"
            ),
            fmt="Name, DOI (Zenodo, Figshare), Data asset ID",
            query="Name, DOI",
        ),
    ],
    metadata={
        "source": "resources/foundingGIDE_metadata_fields.md",
        "grain": "one row per data asset",
    },
)


def _storage_type(t: pa.DataType) -> pa.DataType:
    """Replace every extension type (e.g. ``arrow.json``) with its storage.

    ``pa.array`` cannot build extension types like ``arrow.json`` from Python
    objects, so callers construct those fields using their storage type (a
    string for JSON) and the table is cast to the real schema afterwards.
    Recurses through structs and lists so extension fields at any depth are
    handled.
    """
    if isinstance(t, pa.BaseExtensionType):
        return _storage_type(t.storage_type)
    if pa.types.is_struct(t):
        return pa.struct([f.with_type(_storage_type(f.type)) for f in t])
    if pa.types.is_large_list(t):
        return pa.large_list(
            t.value_field.with_type(_storage_type(t.value_type))
        )
    if pa.types.is_list(t):
        return pa.list_(t.value_field.with_type(_storage_type(t.value_type)))
    return t


def storage_schema() -> pa.Schema:
    """``BIOPARQUET_SCHEMA`` with extensions replaced by storage types.

    Use this to construct data (``pa.array`` can't build extension types from
    Python objects), then ``cast`` the result to ``BIOPARQUET_SCHEMA``.
    """
    return pa.schema(
        [f.with_type(_storage_type(f.type)) for f in BIOPARQUET_SCHEMA],
        metadata=BIOPARQUET_SCHEMA.metadata,
    )


def build_table(rows) -> pa.Table:
    """Build a table from a ``column -> values`` mapping as the schema.

    JSON (``arrow.json``) fields are supplied as JSON strings; they are built
    against the extension's string storage type and cast up to the real schema,
    since ``pa.array`` can't construct extension types from Python objects.
    """
    return pa.table(rows, schema=storage_schema()).cast(BIOPARQUET_SCHEMA)


def main() -> None:
    """Print the schema and write a schema-only Parquet template."""
    print(BIOPARQUET_SCHEMA.to_string(show_field_metadata=False))
    print(f"\n{len(BIOPARQUET_SCHEMA)} top-level components.")

    # Write an empty, schema-only Parquet file as a reusable template.
    # Build the empty table from the storage schema and cast up, since
    # extension types (arrow.json) can't be materialised directly.
    out = "bioparquet_metadata.parquet"
    empty = storage_schema().empty_table().cast(BIOPARQUET_SCHEMA)
    pq.write_table(empty, out)

    # Round-trip to prove the schema is valid and persisted intact.
    # Parquet adds its own "ARROW:schema" metadata on write, so compare
    # structure (types) strictly and confirm the field-level documentation
    # survived separately.
    back = pq.read_schema(out)
    assert back.equals(
        BIOPARQUET_SCHEMA, check_metadata=False
    ), "schema round-trip mismatch"
    assert (
        back.field("description").metadata[b"description"]
        == b"Description of the data asset"
    )
    print(f"Wrote schema-only template -> {out} (round-trip OK)")


if __name__ == "__main__":
    main()
