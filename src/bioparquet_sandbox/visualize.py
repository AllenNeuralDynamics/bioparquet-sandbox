"""Render a Markdown visualization of the bioparquet schema.

The schema in :mod:`bioparquet_sandbox.schema` has grown nested ``struct`` and
``list`` types beyond the flat component table in
``resources/foundingGIDE_metadata_fields.md``. That table can no longer show
subfields such as ``channels.probe.term_id`` or ``axes.spacing``, so it is
no longer a faithful picture of the schema.

This module walks ``BIOPARQUET_SCHEMA`` and renders every field, its nested
subfields, and the Description / Format / Access Query documentation carried in
Arrow field metadata to a Markdown document
(``resources/bioparquet_schema.md``) you can browse on GitHub. It is generated
from the schema itself, so it stays in step as the schema evolves.
"""

from __future__ import annotations

import pyarrow as pa

from bioparquet_sandbox.schema import BIOPARQUET_SCHEMA

# Output relative to the current working directory, matching schema.main().
OUTPUT_PATH = "resources/bioparquet_schema.md"


def _type_label(dtype: pa.DataType) -> str:
    """A concise, human-readable label for an Arrow type.

    Structs collapse to ``struct`` (their subfields are rendered separately);
    lists render as ``list<value>`` recursively; extension types show their
    extension name (e.g. ``arrow.json``); everything else uses Arrow's own
    string form (e.g. ``string``, ``timestamp[us, tz=UTC]``).
    """
    if isinstance(dtype, pa.BaseExtensionType):
        return dtype.extension_name
    if pa.types.is_struct(dtype):
        return "struct"
    if pa.types.is_large_list(dtype) or pa.types.is_list(dtype):
        return f"list<{_type_label(dtype.value_type)}>"
    return str(dtype)


def _meta(field: pa.Field, key: str) -> str | None:
    """Read one decoded metadata value from a field (``None`` if absent)."""
    md = field.metadata or {}
    val = md.get(key.encode())
    return val.decode() if val is not None else None


def _subfields(dtype: pa.DataType) -> list[pa.Field]:
    """The child fields of a struct, unwrapping lists to their value type."""
    if pa.types.is_struct(dtype):
        return list(dtype)
    if pa.types.is_large_list(dtype) or pa.types.is_list(dtype):
        return _subfields(dtype.value_type)
    return []


def _render_subfields(dtype: pa.DataType, indent: int = 0) -> list[str]:
    """Bulleted, indented Markdown lines for a field's nested subfields."""
    lines: list[str] = []
    for field in _subfields(dtype):
        pad = "  " * indent
        desc = _meta(field, "description")
        suffix = f" — {desc}" if desc else ""
        lines.append(
            f"{pad}- `{field.name}` `{_type_label(field.type)}`{suffix}"
        )
        lines.extend(_render_subfields(field.type, indent + 1))
    return lines


def render_markdown(schema: pa.Schema = BIOPARQUET_SCHEMA) -> str:
    """Render ``schema`` as a Markdown document of fields and subfields."""
    lines = [
        "# bioparquet schema",
        "",
        "_Generated from `BIOPARQUET_SCHEMA` in "
        "`src/bioparquet_sandbox/schema.py` by "
        "`bioparquet_sandbox.visualize`. Do not edit by hand — run "
        "`python -m bioparquet_sandbox.visualize`._",
        "",
        f"One row = one data asset. {len(schema)} top-level components.",
        "",
    ]
    for field in schema:
        lines.append(f"## {field.name}")
        lines.append("")
        lines.append(f"`{_type_label(field.type)}`")
        lines.append("")

        desc = _meta(field, "description")
        if desc:
            lines.append(desc)
            lines.append("")

        fmt = _meta(field, "format")
        query = _meta(field, "access_query")
        if fmt:
            lines.append(f"- **Format:** {fmt}")
        if query:
            lines.append(f"- **Access query:** {query}")
        if fmt or query:
            lines.append("")

        subs = _render_subfields(field.type)
        if subs:
            lines.append("**Fields:**")
            lines.append("")
            lines.extend(subs)
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    """Write the schema visualization to ``resources/bioparquet_schema.md``."""
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_markdown())
    print(f"Wrote schema visualization -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
