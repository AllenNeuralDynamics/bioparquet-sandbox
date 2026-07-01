"""Tests for the bioparquet_sandbox.visualize module."""

import os
import tempfile
import unittest

import pyarrow as pa

from bioparquet_sandbox import visualize
from bioparquet_sandbox.schema import BIOPARQUET_SCHEMA
from bioparquet_sandbox.visualize import (
    _escape,
    _field_rows,
    _meta,
    _subfields,
    _type_label,
    render_markdown,
)


class TypeLabelTest(unittest.TestCase):
    """Tests the concise type-label rendering."""

    def test_scalar(self):
        """Scalars fall back to Arrow's own string form."""
        self.assertEqual(_type_label(pa.string()), "string")

    def test_struct(self):
        """Structs collapse to a bare 'struct' label."""
        self.assertEqual(
            _type_label(pa.struct([pa.field("a", pa.int8())])), "struct"
        )

    def test_list_recurses(self):
        """Lists render their value type recursively."""
        self.assertEqual(_type_label(pa.list_(pa.string())), "list<string>")

    def test_large_list(self):
        """large_list is labelled like list."""
        self.assertEqual(
            _type_label(pa.large_list(pa.string())), "list<string>"
        )

    def test_extension(self):
        """Extension types show their extension name."""
        self.assertEqual(_type_label(pa.json_()), "arrow.json")


class MetaTest(unittest.TestCase):
    """Tests metadata extraction from fields."""

    def test_present(self):
        """A present metadata key is decoded to a string."""
        field = pa.field("x", pa.string(), metadata={"description": "hi"})
        self.assertEqual(_meta(field, "description"), "hi")

    def test_absent(self):
        """A missing metadata key returns None."""
        field = pa.field("x", pa.string())
        self.assertIsNone(_meta(field, "description"))


class SubfieldsTest(unittest.TestCase):
    """Tests unwrapping of nested subfields."""

    def test_scalar_has_none(self):
        """A scalar type has no subfields."""
        self.assertEqual(_subfields(pa.string()), [])

    def test_list_unwraps_to_value(self):
        """A list of struct unwraps to the struct's fields."""
        dtype = pa.list_(pa.struct([pa.field("a", pa.int8())]))
        self.assertEqual([f.name for f in _subfields(dtype)], ["a"])


class EscapeTest(unittest.TestCase):
    """Tests escaping of table-breaking characters."""

    def test_escapes_pipe(self):
        """A pipe is backslash-escaped so it stays inside its cell."""
        self.assertEqual(_escape("a | b"), "a \\| b")

    def test_flattens_newline(self):
        """A newline becomes a space so the row stays on one line."""
        self.assertEqual(_escape("a\nb"), "a b")


class FieldRowsTest(unittest.TestCase):
    """Tests rendering of a field and its subfields as table rows."""

    def test_top_level_is_bold(self):
        """A depth-0 field name is emphasised in bold."""
        rows = _field_rows(pa.field("x", pa.string()))
        self.assertTrue(rows[0].startswith("| **`x`** | `string` |"))

    def test_subfields_indented_below_parent(self):
        """Subfield rows follow the parent, indented and with description."""
        dtype = pa.struct(
            [pa.field("a", pa.string(), metadata={"description": "note"})]
        )
        rows = _field_rows(pa.field("parent", dtype))
        self.assertEqual(len(rows), 2)
        self.assertIn("&nbsp;", rows[1])
        self.assertIn("`a`", rows[1])
        self.assertIn("note", rows[1])


class RenderMarkdownTest(unittest.TestCase):
    """Tests the full Markdown document render."""

    def test_documents_every_top_level_field(self):
        """Every top-level component gets a bold row in the table."""
        md = render_markdown()
        for field in BIOPARQUET_SCHEMA:
            self.assertIn(f"| **`{field.name}`** |", md)

    def test_has_table_header(self):
        """The document renders a single table with the expected columns."""
        md = render_markdown()
        self.assertIn("| Field | Type | Description | Format |", md)
        self.assertIn("| --- | --- | --- | --- | --- |", md)

    def test_reports_component_count(self):
        """The header reports the top-level component count."""
        md = render_markdown()
        self.assertIn(f"{len(BIOPARQUET_SCHEMA)} top-level components", md)

    def test_renders_nested_subfields(self):
        """Nested subfields (channels.probe.term_id) are indented rows."""
        md = render_markdown()
        self.assertIn("&nbsp;&nbsp;&nbsp;&nbsp;`probe` | `struct`", md)
        self.assertIn(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id`", md
        )

    def test_ends_with_single_newline(self):
        """The document ends with exactly one trailing newline."""
        md = render_markdown()
        self.assertTrue(md.endswith("\n"))
        self.assertFalse(md.endswith("\n\n"))


class MainTest(unittest.TestCase):
    """Tests the file-writing entry point."""

    def test_writes_output_file(self):
        """main writes the visualization to the expected path."""
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                os.makedirs("resources")
                visualize.main()
                with open(visualize.OUTPUT_PATH, encoding="utf-8") as fh:
                    content = fh.read()
            finally:
                os.chdir(cwd)
        self.assertEqual(content, render_markdown())


if __name__ == "__main__":
    unittest.main()
