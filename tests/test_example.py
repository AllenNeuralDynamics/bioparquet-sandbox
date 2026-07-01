"""Tests for the bioparquet_sandbox.example module."""

import os
import tempfile
import unittest

import pyarrow.parquet as pq

from bioparquet_sandbox import example
from bioparquet_sandbox.schema import BIOPARQUET_SCHEMA


class ExampleTest(unittest.TestCase):
    """Tests the example table builder."""

    def test_build_example_table_validates(self):
        """The example row validates against BIOPARQUET_SCHEMA."""
        table = example.build_example_table()
        self.assertEqual(table.num_rows, 1)
        self.assertTrue(
            table.schema.equals(BIOPARQUET_SCHEMA, check_metadata=False)
        )

    def test_example_populates_organism(self):
        """The example populates the added organism fields."""
        organism = example.build_example_table().to_pylist()[0]["organisms"][0]
        self.assertEqual(organism["organism_id"], "SAMN00000001")
        self.assertIn("strain", organism["additional_metadata"])

    def test_main_writes_parquet(self):
        """main writes a readable one-row Parquet file."""
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                example.main()
                back = pq.read_table(
                    os.path.join("resources", "bioparquet_example.parquet")
                )
            finally:
                os.chdir(cwd)
        self.assertEqual(back.num_rows, 1)


if __name__ == "__main__":
    unittest.main()
