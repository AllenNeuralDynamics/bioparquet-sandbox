"""Build an example bioparquet metadata table conforming to the schema.

Populates one realistic data asset row (a fictional human iPSC live-imaging
study) across every component, writes it to Parquet, then reads it back to
confirm the data validates against ``BIOPARQUET_SCHEMA``.
"""

from __future__ import annotations

import datetime as dt
import json
import os

import pyarrow as pa
import pyarrow.parquet as pq

from bioparquet_sandbox.schema import BIOPARQUET_SCHEMA, build_table

# One row, given as a column-name -> list-of-values mapping (one element per
# row). Nested structs are plain dicts; lists are Python lists. Any component
# may be omitted/None -- the schema is fully nullable.
ROWS = {
    "description": [
        "Live confocal imaging of mitochondrial dynamics in human "
        "iPSC-derived cardiomyocytes under metabolic stress."
    ],
    "authors": [
        [
            {
                "name": "Ada Lovelace",
                "orcid": "0000-0002-1825-0097",
                "credit_roles": [
                    "Conceptualization",
                    "Writing - original draft",
                ],
                "organization_name": "Allen Institute for Cell Science",
                "ror": "03cpe7c52",
            },
            {
                "name": "Grace Hopper",
                "orcid": "0000-0001-2345-6789",
                "credit_roles": ["Data curation", "Formal analysis"],
                "organization_name": "Allen Institute for Cell Science",
                "ror": "03cpe7c52",
            },
        ]
    ],
    "organizations": [
        [
            {
                "name": "Allen Institute for Cell Science",
                "url": "https://www.allencell.org",
                "ror": "03cpe7c52",
            }
        ]
    ],
    "publications": [
        [
            {
                "title": "Mitochondrial remodelling in cardiomyocytes",
                "year": 2025,
                "doi": "10.1038/s41586-025-00000-0",
                "journal": "Nature",
            }
        ]
    ],
    "license": [
        {
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
        }
    ],
    "release_date": [dt.datetime(2025, 11, 3, 9, 0, tzinfo=dt.timezone.utc)],
    "acquisition_methods": [
        [
            {
                "ontology_source": "FBbi",
                "term_id": "FBbi:00000251",
                "term_label": "confocal microscopy",
            }
        ]
    ],
    "specimens": [
        [
            {
                "specimen_id": "WTC-11-CM-001",
                "specimen_type": {
                    "ontology_source": "CLO",
                    "term_id": "CLO:0037317",
                    "term_label": "WTC-11 human iPSC line",
                },
                "anatomical_location": {
                    "ontology_source": "UBERON",
                    "term_id": "UBERON:0000948",
                    "term_label": "heart",
                },
                "genotype": "mEGFP-TOMM20 knock-in (AICS-0011)",
                "treatments": [
                    {
                        "ontology_source": "ChEBI",
                        "term_id": "CHEBI:28748",
                        "term_label": "doxorubicin",
                    }
                ],
                "protocol_doi": "10.17504/protocols.io.abc123",
                "additional_metadata": json.dumps(
                    {"differentiation": "cardiomyocyte", "passage": 12}
                ),
            }
        ]
    ],
    "organisms": [
        [
            {
                "organism_id": "SAMN00000001",
                "ncbi_taxon_id": "NCBITaxon:9606",
                "term_label": "Homo sapiens",
                "geographic_location": "USA: Washington",
                "pathology_disease": [
                    {
                        "ontology_source": "MONDO",
                        "term_id": "MONDO:0005267",
                        "term_label": "heart disorder",
                    }
                ],
                "additional_metadata": json.dumps(
                    {
                        "strain": "WTC-11",
                        "sex": "male",
                        "developmental_stage": "adult",
                    }
                ),
            }
        ]
    ],
    "channels": [
        [
            {
                "probe": {
                    "ontology_source": "ChEBI",
                    "term_id": "CHEBI:52214",
                    "term_label": "anti-TOM20 antibody",
                    "rrid": "AB_2207533",
                },
                "target": {
                    "ontology_source": "UniProt",
                    "term_id": "Q15388",
                    "term_label": "TOMM20",
                },
            }
        ]
    ],
    "instrument": [
        {
            "name": "Zeiss LSM 980",
            "description": "Inverted laser scanning confocal (NBO-Q)",
            "additional_metadata": json.dumps(
                {
                    "pidinst": "21.T11998/instrument-lsm980",
                    "objective": "63x/1.4 oil",
                    "lasers_nm": [488, 561],
                }
            ),
        }
    ],
    "axes": [
        [
            {
                "name": "t",
                "type": "time",
                "size": 120,
                "spacing": 30.0,
                "unit": "second",
            },
            {
                "name": "c",
                "type": "channel",
                "size": 2,
                "spacing": None,
                "unit": None,
            },
            {
                "name": "z",
                "type": "space",
                "size": 40,
                "spacing": 0.29,
                "unit": "micrometer",
            },
            {
                "name": "y",
                "type": "space",
                "size": 1024,
                "spacing": 0.108,
                "unit": "micrometer",
            },
            {
                "name": "x",
                "type": "space",
                "size": 1024,
                "spacing": 0.108,
                "unit": "micrometer",
            },
        ]
    ],
    "study": [{"accession_id": "S-BIAD1234", "doi": "10.6019/S-BIAD1234"}],
    "data_asset_id": ["S-BIAD1234-1"],
    "phenotype": [
        [
            {
                "ontology_source": "CMPO",
                "term_id": "CMPO:0000425",
                "term_label": "fragmented mitochondria phenotype",
            }
        ]
    ],
    "anatomical_location": [
        [
            {
                "ontology_source": "UBERON",
                "term_id": "UBERON:0000948",
                "term_label": "heart",
            }
        ]
    ],
    # What produced THIS data asset: the raw images were compressed on write.
    "processing": [
        [
            {
                "name": "Blosc2 zstd compression",
                "url": "https://github.com/Blosc/c-blosc2",
                "rrid": None,
                "version": "2.13.0",
            }
        ]
    ],
    # A separate, downstream data asset derived from this one. Whatever
    # produced it (e.g. a segmentation tool) is described in that asset's
    # own processing.
    "derived_data": [
        [
            {
                "name": "mitochondria segmentation masks",
                "doi": "10.5281/zenodo.9999999",
                "data_asset_id": "S-BIAD1234-2",
            }
        ]
    ],
}


def build_example_table() -> pa.Table:
    """Build the example table, typed as ``BIOPARQUET_SCHEMA``.

    Returns
    -------
    pa.Table

    """
    return build_table(ROWS)


def main() -> None:
    """Build the example table, write it to Parquet, and read it back."""
    table = build_example_table()
    assert table.schema.equals(BIOPARQUET_SCHEMA, check_metadata=False)

    out = os.path.join("resources", "bioparquet_example.parquet")
    os.makedirs("resources", exist_ok=True)
    pq.write_table(table, out)

    back = pq.read_table(out)
    print(f"Wrote {out}: {back.num_rows} row(s) x {back.num_columns} columns")


if __name__ == "__main__":
    main()
