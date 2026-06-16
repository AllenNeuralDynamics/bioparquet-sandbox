# /// script
# requires-python = ">=3.10"
# dependencies = ["pyarrow>=19"]
# ///
"""Build an example bioparquet metadata table conforming to ``BIOPARQUET_SCHEMA``.

Populates one realistic data asset row (a fictional human iPSC live-imaging study)
across every component, writes it to Parquet, then reads it back to confirm the
data validates against the schema.
"""

from __future__ import annotations

import datetime as dt
import json

import pyarrow as pa
import pyarrow.parquet as pq

from bioparquet_schema import BIOPARQUET_SCHEMA, build_table

# One row, given as a column-name -> list-of-values mapping (one element per
# row). Nested structs are plain dicts; lists are Python lists. Any component
# may be omitted/None — the schema is fully nullable.
ROWS = {
    "description": [
        "Live confocal imaging of mitochondrial dynamics in human iPSC-derived "
        "cardiomyocytes under metabolic stress."
    ],
    "authors": [
        [
            {
                "name": "Ada Lovelace",
                "orcid": "0000-0002-1825-0097",
                "credit_roles": ["Conceptualization", "Writing – original draft"],
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
        [{"name": "Allen Institute for Cell Science", "url": "https://www.allencell.org", "ror": "03cpe7c52"}]
    ],
    "publications": [
        [
            {
                "title": "Mitochondrial remodelling in stressed cardiomyocytes",
                "year": 2025,
                "doi": "10.1038/s41586-025-00000-0",
                "journal": "Nature",
            }
        ]
    ],
    "license": [{"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}],
    "release_date": [dt.datetime(2025, 11, 3, 9, 0, tzinfo=dt.timezone.utc)],
    "methods": [
        [{"ontology_source": "FBbi", "term_id": "FBbi:00000251", "term_label": "confocal microscopy"}]
    ],
    "cell_lines": [
        [{"term_id": "CLO:0037317", "term_label": "WTC-11 human induced pluripotent stem cell line"}]
    ],
    "organisms": [
        [{"ncbi_taxon_id": "NCBITaxon:9606", "term_label": "Homo sapiens", "geographic_location": "USA: Washington"}]
    ],
    "genes": [
        [
            {"source": "Ensembl", "gene_id": "ENSG00000198888", "gene_name": "MT-ND1"},
            {"source": "NCBI Gene", "gene_id": "4535", "gene_name": "ND1"},
        ]
    ],
    "compounds": [
        [{"ontology_source": "ChEBI", "term_id": "CHEBI:28748", "term_label": "doxorubicin"}]
    ],
    "antibodies": [
        [
            {
                "ontology_source": "ChEBI",
                "term_id": "CHEBI:52214",
                "term_label": "anti-TOM20 antibody",
                "rrid": "AB_2207533",
            }
        ]
    ],
    "channels": [
        [
            {
                "probe": {"ontology_source": "ChEBI", "term_id": "CHEBI:87173", "term_label": "Alexa Fluor 488"},
                "target": {"ontology_source": "UniProt", "term_id": "Q15388", "term_label": "TOMM20"},
            }
        ]
    ],
    "instrument": [
        {
            "name": "Zeiss LSM 980",
            "description": "Inverted laser scanning confocal microscope (NBO-Q compliant)",
            "additional_metadata": json.dumps(
                {"pidinst": "21.T11998/instrument-lsm980", "objective": "63x/1.4 oil", "lasers_nm": [488, 561]}
            ),
        }
    ],
    "axes": [
        [
            {"name": "t", "type": "time", "size": 120, "spacing": 30.0, "unit": "second"},
            {"name": "c", "type": "channel", "size": 2, "spacing": None, "unit": None},
            {"name": "z", "type": "space", "size": 40, "spacing": 0.29, "unit": "micrometer"},
            {"name": "y", "type": "space", "size": 1024, "spacing": 0.108, "unit": "micrometer"},
            {"name": "x", "type": "space", "size": 1024, "spacing": 0.108, "unit": "micrometer"},
        ]
    ],
    "study_id": [{"accession_id": "S-BIAD1234", "doi": "10.6019/S-BIAD1234"}],
    "data_asset_id": ["S-BIAD1234-1"],
    "pathology_disease": [
        [{"ontology_source": "MONDO", "term_id": "MONDO:0005267", "term_label": "heart disorder"}]
    ],
    "phenotype": [
        [{"ontology_source": "CMPO", "term_id": "CMPO:0000425", "term_label": "fragmented mitochondria phenotype"}]
    ],
    "anatomical_location": [
        [{"ontology_source": "UBERON", "term_id": "UBERON:0000948", "term_label": "heart"}]
    ],
    # What produced THIS data asset: the raw images were compressed on write.
    "processing": [
        [
            {
                "name": "Blosc2 zstd compression",
                "url": "https://github.com/Blosc/c-blosc2/releases/tag/v2.13.0",
                "rrid": None,
                "version": "2.13.0",
            }
        ]
    ],
    # A separate, downstream data asset derived from this one. Whatever produced
    # it (e.g. a segmentation tool) is described in that asset's own processing.
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


def main() -> None:
    table = build_table(ROWS)
    assert table.schema.equals(BIOPARQUET_SCHEMA, check_metadata=False)

    out = "bioparquet_example.parquet"
    pq.write_table(table, out)

    back = pq.read_table(out)
    print(f"Wrote {out}: {back.num_rows} row(s) x {back.num_columns} columns")
    print(back.to_pandas().T.to_string()) if _has_pandas() else _print_plain(back)


def _has_pandas() -> bool:
    try:
        import pandas  # noqa: F401

        return True
    except ImportError:
        return False


def _print_plain(table: pa.Table) -> None:
    row = table.to_pylist()[0]
    for key, value in row.items():
        print(f"\n{key}:\n  {value}")


if __name__ == "__main__":
    main()
