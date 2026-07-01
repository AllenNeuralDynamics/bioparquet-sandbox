"""Tests for the bioparquet_sandbox.schema module."""

import os
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from bioparquet_sandbox import schema
from bioparquet_sandbox.schema import (
    BIOPARQUET_SCHEMA,
    _storage_type,
    build_table,
    storage_schema,
)


class SchemaTest(unittest.TestCase):
    """Tests the bioparquet schema definition and helpers."""

    def test_top_level_component_count(self):
        """The schema exposes 22 top-level components."""
        self.assertEqual(len(BIOPARQUET_SCHEMA), 22)

    def test_organism_fields(self):
        """The organism struct carries the added identifier and JSON."""
        organism = BIOPARQUET_SCHEMA.field("organisms").type.value_type
        names = [f.name for f in organism]
        self.assertIn("organism_id", names)
        self.assertIn("additional_metadata", names)
        json_field = organism.field("additional_metadata")
        self.assertIsInstance(json_field.type, pa.JsonType)

    def test_storage_schema_replaces_extensions(self):
        """storage_schema swaps arrow.json for its string storage type."""
        organism = storage_schema().field("organisms").type.value_type
        json_field = organism.field("additional_metadata")
        self.assertFalse(isinstance(json_field.type, pa.BaseExtensionType))
        self.assertTrue(pa.types.is_string(json_field.type))

    def test_storage_type_large_list(self):
        """_storage_type recurses through large_list value types."""
        large = pa.large_list(pa.field("item", pa.json_()))
        result = _storage_type(large)
        self.assertTrue(pa.types.is_large_list(result))
        self.assertTrue(pa.types.is_string(result.value_type))

    def test_build_table_types_as_schema(self):
        """build_table returns a table typed as BIOPARQUET_SCHEMA."""
        rows = {f.name: [None] for f in BIOPARQUET_SCHEMA}
        table = build_table(rows)
        self.assertTrue(
            table.schema.equals(BIOPARQUET_SCHEMA, check_metadata=False)
        )

    def test_main_writes_and_round_trips(self):
        """main writes a schema-only template that round-trips."""
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                schema.main()
                back = pq.read_schema("bioparquet_metadata.parquet")
            finally:
                os.chdir(cwd)
        self.assertTrue(back.equals(BIOPARQUET_SCHEMA, check_metadata=False))


if __name__ == "__main__":
    unittest.main()
