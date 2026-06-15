# /// script
# requires-python = ">=3.10"
# dependencies = ["pyarrow>=16"]
# ///
"""Parquet schema for the foundingGIDE bioimaging metadata fields.

The schema is derived 1:1 from ``foundingGIDE_metadata_fields.md``. Each row of
that table is a metadata *component*; here each component becomes one top-level
column of a single wide table whose grain is **one row per dataset/study**.

Design notes
------------
* Most components reference a controlled vocabulary as a (term, id) pair, often
  with a named source ontology. These are modelled with the reusable
  ``ontology_term`` struct so the *which ontology* provenance is never lost.
* Components that can legitimately repeat (authors, genes, organisms, imaging
  methods, ...) are modelled as ``list<...>`` rather than scalars.
* Free text -> ``string``; release date -> timezone-aware ``timestamp`` to honour
  the "ISO 8601 incl. time/time zone" format requirement.
* Field-level ``metadata`` carries the original Description / Format / Access
  Query text from the metadata spec so the Parquet file is self-documenting.
"""

from __future__ import annotations

import pyarrow as pa
import pyarrow.parquet as pq


def ontology_term(*, source: bool = True) -> pa.DataType:
    """A controlled-vocabulary reference: (optional source ontology, id, label)."""
    fields = []
    if source:
        # e.g. "FBbi", "NCBI Taxonomy", "ChEBI", "MONDO" ...
        fields.append(pa.field("ontology_source", pa.string()))
    fields.append(pa.field("term_id", pa.string()))  # e.g. "NCBITaxon:9606"
    fields.append(pa.field("term_label", pa.string()))  # e.g. "Homo sapiens"
    return pa.struct(fields)


def col(name: str, dtype: pa.DataType, *, description: str, fmt: str, query: str) -> pa.Field:
    """Build a field, attaching the metadata spec's documentation as metadata."""
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
        pa.field("first_name", pa.string()),
        pa.field("last_name", pa.string()),
        pa.field("orcid", pa.string()),
        pa.field("credit_roles", pa.list_(pa.string())),  # CRediT contributor roles
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
        pa.field("name", pa.string()),  # Creative Commons + version, e.g. "CC BY 4.0"
        pa.field("url", pa.string()),
    ]
)

gene = pa.struct(
    [
        pa.field("source", pa.string()),  # "Ensembl" | "NCBI Gene"
        pa.field("gene_id", pa.string()),
        pa.field("gene_name", pa.string()),
    ]
)

organism = pa.struct(
    [
        pa.field("ncbi_taxon_id", pa.string()),
        pa.field("term_label", pa.string()),
        pa.field("geographic_location", pa.string()),  # BioSample geo location
    ]
)

antibody = pa.struct(
    [
        pa.field("ontology_source", pa.string()),  # "FBbi" | "ChEBI"
        pa.field("term_id", pa.string()),
        pa.field("term_label", pa.string()),
        pa.field("rrid", pa.string()),  # Research Resource Identifier
    ]
)

channel_biological_entity = pa.struct(
    [
        pa.field("efo_term_id", pa.string()),  # Experimental Factor Ontology
        pa.field("efo_term_label", pa.string()),
        pa.field("uniprot_id", pa.string()),
    ]
)

# A single imaging channel: what it captures (FBbi content) plus the
# biological entity it targets. Datasets can have many channels.
channel = pa.struct(
    [
        pa.field("content", ontology_term(source=False)),  # FBbi
        pa.field("biological_entity", channel_biological_entity),
    ]
)

instrument = pa.struct(
    [
        pa.field("name", pa.string()),  # 4DN-BINA-OME-QUAREP (NBO-Q) compliant
        pa.field("instrument_id", pa.string()),  # PIDInst
    ]
)

# OME-Zarr axes (T, C, Z, Y, X): ordered list of axis descriptors.
axis = pa.struct(
    [
        pa.field("name", pa.string()),  # "t" | "c" | "z" | "y" | "x"
        pa.field("type", pa.string()),  # "time" | "channel" | "space"
        pa.field("size", pa.int64()),  # number of elements along the axis
    ]
)

# Physical size / time resolution, value + unit per spatial/temporal axis.
resolution = pa.struct(
    [
        pa.field("axis", pa.string()),  # "x" | "y" | "z" | "t"
        pa.field("size", pa.float64()),
        pa.field("unit", pa.string()),  # e.g. "micrometer", "second"
    ]
)

study_unique_id = pa.struct(
    [
        pa.field("accession_id", pa.string()),
        pa.field("doi", pa.string()),
    ]
)

analyzed_data = pa.struct(
    [
        pa.field("name", pa.string()),
        pa.field("github_url", pa.string()),  # release URL
        pa.field("doi", pa.string()),  # Zenodo / Figshare
        pa.field("rrid", pa.string()),
        pa.field("dataset_id", pa.string()),
    ]
)


# --- The GIDE schema -------------------------------------------------------

GIDE_SCHEMA = pa.schema(
    [
        col(
            "study_description",
            pa.string(),
            description="Description of the study",
            fmt="Text",
            query="Free text",
        ),
        col(
            "authors",
            pa.list_(author),
            description="Information about the authors",
            fmt="First name and Last name; Affiliation, ORCID",
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
            description="Information about the dataset's license",
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
            "imaging_methods",
            pa.list_(ontology_term()),  # FBbi / EDAM Bioimaging
            description="The method used to obtain image data",
            fmt="FBbi, EDAM Bioimaging Ontology term and ID",
            query="FBbi or EDAM Bioimaging Ontology ID, term",
        ),
        col(
            "cell_lines",
            pa.list_(ontology_term(source=False)),  # CLO
            description="Information about the cell line",
            fmt="Cell Line Ontology term and ID",
            query="CLO ID, term",
        ),
        col(
            "organisms",
            pa.list_(organism),
            description="Information about the organism studied",
            fmt="NCBI Taxonomy term and ID, BioSample (geographic location)",
            query="NCBI Taxonomy ID, term",
        ),
        col(
            "genes",
            pa.list_(gene),
            description="Information about related genes",
            fmt="Ensembl Gene or NCBI Gene name or ID",
            query="Gene ID, name",
        ),
        col(
            "compounds",
            pa.list_(ontology_term()),  # ChEBI / PubChem
            description="Information about the compound",
            fmt="ChEBI or PubChem term and ID",
            query="Compound ID, term",
        ),
        col(
            "antibodies",
            pa.list_(antibody),
            description="Information about the antibody used",
            fmt="FBbi or ChEBI term and ID, RRID",
            query="Antibody ID, term",
        ),
        col(
            "channels",
            pa.list_(channel),
            description="Information about the imaging channels (content and biological entity)",
            fmt="FBbi term and ID (content); Experimental Factor Ontology term and UniProt ID (biological entity)",
            query="Channel content ID/term, Biological entity ID/term",
        ),
        col(
            "instrument",
            instrument,
            description="Information about the instrument used",
            fmt="Compliant with 4DN-BINA-OME-QUAREP (NBO-Q) standards, PIDInst",
            query="Instrument name, ID",
        ),
        col(
            "dimensions",
            pa.list_(axis),
            description="Information about data dimensions",
            fmt="Compliant with OME-Zarr axes info. (T, C, Z, Y, X)",
            query="Dimension specification",
        ),
        col(
            "resolution",
            pa.list_(resolution),
            description="Size of the pixels or voxels, Time interval",
            fmt="Pixel/Voxel size and time interval stored with units",
            query="Pixel/voxel size, Time interval",
        ),
        col(
            "study_unique_id",
            study_unique_id,
            description="Unique ID for the study",
            fmt="Accession ID, DOI",
            query="Accession ID, DOI",
        ),
        col(
            "dataset_unique_id",
            pa.string(),
            description="Unique ID for the dataset",
            fmt="Accession ID",
            query="Accession ID",
        ),
        col(
            "pathology_disease",
            pa.list_(ontology_term()),  # SNOMED-CT / DOID / ICD-11 / MONDO
            description="Pathology/Disease related to the biological entity",
            fmt="SNOMED-CT, DOID, ICD-11 or MONDO",
            query="Pathology/Disease ID, term",
        ),
        col(
            "phenotype",
            pa.list_(ontology_term()),  # CMPO / MPO / HPO
            description="Phenotypic data related to the analysis",
            fmt="Cell Morphology Phenotype Ontology, MPO, or HPO",
            query="Phenotype ID, term",
        ),
        col(
            "organ",
            pa.list_(ontology_term()),  # UBERON / RadLex
            description="Information about anatomical entities",
            fmt="UBERON, RadLex Ontology",
            query="UBERON ID, term",
        ),
        col(
            "analyzed_data",
            pa.list_(analyzed_data),
            description="Information about software, workflow, annotation data",
            fmt="GitHub URL (release), DOI (Zenodo, Figshare), RRID, Dataset ID",
            query="Name, DOI",
        ),
    ],
    metadata={
        "source": "foundingGIDE_metadata_fields.md",
        "grain": "one row per dataset/study",
    },
)


def main() -> None:
    print(GIDE_SCHEMA.to_string(show_field_metadata=False))
    print(f"\n{len(GIDE_SCHEMA)} top-level components.")

    # Write an empty, schema-only Parquet file as a reusable template.
    out = "gide_metadata.parquet"
    empty = GIDE_SCHEMA.empty_table()
    pq.write_table(empty, out)

    # Round-trip to prove the schema is valid and persisted intact. Parquet adds
    # its own "ARROW:schema" metadata on write, so compare structure (types)
    # strictly and confirm the field-level documentation survived separately.
    back = pq.read_schema(out)
    assert back.equals(GIDE_SCHEMA, check_metadata=False), "schema round-trip mismatch"
    assert back.field("study_description").metadata[b"description"] == b"Description of the study"
    print(f"Wrote schema-only template -> {out} (round-trip OK, field docs preserved)")


if __name__ == "__main__":
    main()
