#!/usr/bin/env python3
"""Compose the Hugo thin-client API reference from extractor JSONs + groups.yaml + overlay/.

Emits Hugo markdown with Docsy `{{< tabpane >}}` shortcodes to the path given
by --output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml


BINDINGS = ("go", "rust", "python")
TAB_LABEL = {"go": "Go", "rust": "Rust", "python": "Python"}

PINNED_VERSIONS_PLACEHOLDER = "<!-- PINNED_VERSIONS_TABLE -->"

DATA_TYPES_PLACEHOLDER = "<!-- DATA_TYPES_TABLE -->"


def _one_line(text: str) -> str:
    """Collapse a multi-line doc comment to a single table-cell line."""
    return " ".join(part.strip() for part in text.split()) if text else ""


def render_data_types(go_syms: dict[str, dict], spec: list) -> str:
    """Render a field reference for the curated Go return/parameter structs.

    `spec` is the parsed data-types.yaml: a list of entries, each either
    a bare struct name or a mapping with `struct:` and optional `title:`
    and `note:`. The Go reference structs are authoritative; the Rust
    and Python bindings carry the same data under snake_case names.
    """
    blocks: list[str] = []
    for entry in spec:
        if isinstance(entry, str):
            name, title, note = entry, entry, ""
        else:
            name = entry["struct"]
            title = entry.get("title") or name
            note = entry.get("note") or ""
        sym = go_syms.get(name)
        if sym is None:
            blocks.append(f"### {title}\n\n_(unresolved: Go struct "
                          f"`{name}` not found)_")
            continue
        lines = [f"### {title}"]
        doc = strip_structured_sections((sym.get("doc") or "").strip())
        if doc:
            lines.append("")
            lines.append(doc.rstrip())
        if note:
            lines.append("")
            lines.append(note.rstrip())
        fields = sym.get("fields") or []
        if fields:
            lines.append("")
            lines.append("| Field | Type | Description |")
            lines.append("|---|---|---|")
            for f in fields:
                desc = _one_line(f.get("doc") or "")
                ftype = f.get("type", "").replace("|", "\\|")
                lines.append(f"| `{f['name']}` | `{ftype}` | {desc} |")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def render_pinned_versions_table(katzenpost_tag: str, thinclient_tag: str) -> str:
    kp = "https://github.com/katzenpost/katzenpost"
    tc = "https://github.com/katzenpost/thin_client"
    return (
        "| Binding | Repository | Tag |\n"
        "| --- | --- | --- |\n"
        f"| Go reference | [katzenpost/client/thin]({kp}/tree/{katzenpost_tag}/client/thin) "
        f"| [{katzenpost_tag}]({kp}/releases/tag/{katzenpost_tag}) |\n"
        f"| Rust | [thin_client/src]({tc}/tree/{thinclient_tag}/src) "
        f"| [{thinclient_tag}]({tc}/releases/tag/{thinclient_tag}) |\n"
        f"| Python | [thin_client/katzenpost_thinclient]({tc}/tree/{thinclient_tag}/katzenpost_thinclient) "
        f"| [{thinclient_tag}]({tc}/releases/tag/{thinclient_tag}) |"
    )


def load_symbols(path: Path) -> dict[str, dict]:
    """Return a dict keyed by 'Receiver.Name' (or just 'Name' if no receiver)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for sym in data.get("symbols", []):
        name = sym["name"]
        recv = sym.get("receiver") or ""
        key = f"{recv}.{name}" if recv else name
        out[key] = sym
        # Also expose a receiver-less key as fallback, prefixed with a sentinel
        # so later conflicts don't silently shadow, unless the receiver-less
        # entry is actually unambiguous.
    return out


def load_overlay(overlay_dir: Path) -> dict[str, list[str]]:
    """Partition overlay fragments by placement rule.

    Placement is encoded in the filename:
      - `NN-<name>.md` where NN < "80" → before all groups
      - `NN-<name>.md` where NN >= "80" → after all groups
      - `after-<section-slug>.md`      → after the group section whose name
        slugifies to <section-slug>
    """
    result: dict = {
        "top": [],           # rendered before all groups
        "post": [],          # rendered after all groups
        "before_section": {},  # slug -> list of bodies, rendered after the H2 heading but before its groups
        "after_section": {},   # slug -> list of bodies, rendered after all groups of a section
    }
    for path in sorted(overlay_dir.glob("*.md")):
        stem = path.stem
        body = path.read_text(encoding="utf-8")
        if stem.startswith("after-"):
            slug = stem[len("after-"):]
            result["after_section"].setdefault(slug, []).append(body)
            continue
        if stem.startswith("before-"):
            slug = stem[len("before-"):]
            result["before_section"].setdefault(slug, []).append(body)
            continue
        if stem < "80":
            result["top"].append(body)
        else:
            result["post"].append(body)
    return result


def slugify_section(section: str) -> str:
    """Reduce a section name to a filename-safe slug.

    Example: "Pigeonhole: Copy Command Transport" → "pigeonhole-copy-command-transport"
    """
    out = []
    for ch in section.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def resolve_symbol(
    symbols: dict[str, dict],
    key: str,
) -> dict | None:
    """Look up a symbol by 'Receiver::method' / 'Receiver.method' / 'name' key."""
    # Normalise 'Receiver::method' (Rust-style) to 'Receiver.method'.
    normalised = key.replace("::", ".")
    return symbols.get(normalised)


DOCSTRING_SECTION_HEADERS = (
    "Parameters:",
    "Returns:",
    "Arguments:",
    "Args:",
    "Errors:",
    "Raises:",
    "Throws:",
    "Example:",
    "Examples:",
    "Panics:",
    "Requirements:",
)


def strip_structured_sections(doc: str) -> str:
    """Truncate a docstring at the first structured trailing section.

    Looks for any of the conventional Go / Rust / Python doc section
    headers (case-sensitive, optionally preceded by whitespace) and
    drops everything from that line onwards. The narrative paragraphs
    that precede the first header are preserved verbatim. Type and
    error information conveyed by those sections is already shown in
    the signature pane immediately below the prose, so removing it
    here avoids restating it.
    """
    lines = doc.splitlines()
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        for header in DOCSTRING_SECTION_HEADERS:
            if stripped.startswith(header):
                return "\n".join(lines[:i]).rstrip()
    return doc.rstrip()


def resolve_prose(
    group: dict,
    go_syms: dict[str, dict],
    rust_syms: dict[str, dict],
    py_syms: dict[str, dict],
) -> str:
    """Choose the prose paragraph that introduces a group's method.

    Preference order: the Go docstring, then Rust, then Python; trailing
    structured sections (Parameters:, Returns:, Example:, etc.) are
    stripped before returning. If no binding has a non-empty docstring,
    the curated `summary:` field of the group entry is used as a last
    resort.
    """
    for syms, key_field in (
        (go_syms, "go"),
        (rust_syms, "rust"),
        (py_syms, "python"),
    ):
        key = group.get(key_field)
        if not key:
            continue
        sym = resolve_symbol(syms, key)
        if sym is None:
            continue
        doc = (sym.get("doc") or "").strip()
        if doc:
            return strip_structured_sections(doc)
    return (group.get("summary") or "").strip()


def render_group(
    group: dict,
    go_syms: dict[str, dict],
    rust_syms: dict[str, dict],
    py_syms: dict[str, dict],
    unresolved: list[str],
) -> str:
    lines: list[str] = []
    title = group.get("title") or group.get("group")
    lines.append(f"### {title}\n")

    prose = resolve_prose(group, go_syms, rust_syms, py_syms)
    if prose:
        lines.append(prose.rstrip() + "\n")

    notes = group.get("notes")
    if notes:
        lines.append(notes.rstrip() + "\n")

    # Tab pane
    tabs: list[tuple[str, str, str]] = []  # (binding, lang_tag, signature)
    for binding, syms, lang_tag in (
        ("go", go_syms, "go"),
        ("rust", rust_syms, "rust"),
        ("python", py_syms, "python"),
    ):
        key = group.get(binding)
        if not key:
            continue
        sym = resolve_symbol(syms, key)
        if sym is None:
            unresolved.append(f"{group.get('group')}: {binding} symbol '{key}' not found")
            tabs.append((binding, lang_tag, f"// UNRESOLVED: {key}"))
        else:
            tabs.append((binding, lang_tag, sym["signature"]))

    if tabs:
        lines.append("{{< tabpane >}}")
        for binding, lang_tag, sig in tabs:
            lines.append(f'{{{{< tab header="{TAB_LABEL[binding]}" lang="{lang_tag}" >}}}}')
            lines.append(sig.rstrip())
            lines.append("{{< /tab >}}")
        lines.append("{{< /tabpane >}}")
        lines.append("")

    # Error table reference
    errors_ref = group.get("errors")
    if errors_ref:
        # We don't inline; emit a pointer that the overlay fragments handle.
        # This is a soft hook; overlay/80-transport-errors.md etc. carry the tables.
        pass

    return "\n".join(lines) + "\n"


def render_document(
    groups: list[dict],
    overlay: dict,
    go_syms: dict[str, dict],
    rust_syms: dict[str, dict],
    py_syms: dict[str, dict],
    strict: bool,
    katzenpost_tag: str,
    thinclient_tag: str,
    data_types_spec: list,
) -> tuple[str, list[str]]:
    unresolved: list[str] = []
    parts: list[str] = []

    versions_table = render_pinned_versions_table(katzenpost_tag, thinclient_tag)
    data_types_block = (
        render_data_types(go_syms, data_types_spec) if data_types_spec else ""
    )
    placeholder_seen = False
    data_types_seen = False

    def fill(frag: str) -> str:
        nonlocal placeholder_seen, data_types_seen
        if PINNED_VERSIONS_PLACEHOLDER in frag:
            frag = frag.replace(PINNED_VERSIONS_PLACEHOLDER, versions_table)
            placeholder_seen = True
        if DATA_TYPES_PLACEHOLDER in frag:
            frag = frag.replace(DATA_TYPES_PLACEHOLDER, data_types_block)
            data_types_seen = True
        return frag

    # Emit the top overlay first (preamble, configuration, etc.).
    for frag in overlay["top"]:
        parts.append(fill(frag).rstrip() + "\n\n")

    if not placeholder_seen:
        unresolved.append(
            f"pinned versions placeholder {PINNED_VERSIONS_PLACEHOLDER!r} "
            "not found in any top overlay fragment"
        )

    # Group the groups list by section, preserving insertion order.
    sections_ordered: list[str] = []
    by_section: dict[str, list[dict]] = {}
    for group in groups:
        sec = group.get("section") or ""
        if sec not in by_section:
            sections_ordered.append(sec)
            by_section[sec] = []
        by_section[sec].append(group)

    for section in sections_ordered:
        slug = slugify_section(section) if section else ""
        if section:
            parts.append(f"## {section}\n\n")
        for frag in overlay["before_section"].get(slug, []):
            parts.append(frag.rstrip() + "\n\n")
        for group in by_section[section]:
            parts.append(render_group(group, go_syms, rust_syms, py_syms, unresolved))
        for frag in overlay["after_section"].get(slug, []):
            parts.append(frag.rstrip() + "\n\n")

    for frag in overlay["post"]:
        parts.append(fill(frag).rstrip() + "\n\n")

    if data_types_spec and not data_types_seen:
        unresolved.append(
            f"data types placeholder {DATA_TYPES_PLACEHOLDER!r} "
            "not found in any overlay fragment"
        )

    doc = "".join(parts)
    return doc, unresolved


def main() -> int:
    p = argparse.ArgumentParser(description="Stitch the thin-client API reference.")
    p.add_argument("--go-json", required=True, type=Path)
    p.add_argument("--rust-json", required=True, type=Path)
    p.add_argument("--python-json", required=True, type=Path)
    p.add_argument("--groups", required=True, type=Path)
    p.add_argument("--data-types", type=Path, default=None,
                   help="optional YAML list of Go structs to render as a "
                        "field reference at the DATA_TYPES placeholder")
    p.add_argument("--overlay", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero if any groups.yaml symbol is unresolved")
    p.add_argument("--katzenpost-tag", required=True,
                   help="pinned katzenpost tag, rendered into the preamble table")
    p.add_argument("--thinclient-tag", required=True,
                   help="pinned thin_client tag, rendered into the preamble table")
    args = p.parse_args()

    go_syms = load_symbols(args.go_json)
    rust_syms = load_symbols(args.rust_json)
    py_syms = load_symbols(args.python_json)

    groups_raw = yaml.safe_load(args.groups.read_text(encoding="utf-8")) or []
    if not isinstance(groups_raw, list):
        print("error: groups.yaml must be a YAML list at the top level", file=sys.stderr)
        return 2

    overlay = load_overlay(args.overlay)

    data_types_spec: list = []
    if args.data_types is not None:
        data_types_spec = yaml.safe_load(
            args.data_types.read_text(encoding="utf-8")) or []
        if not isinstance(data_types_spec, list):
            print("error: data-types file must be a YAML list at the top level",
                  file=sys.stderr)
            return 2

    doc, unresolved = render_document(
        groups_raw, overlay, go_syms, rust_syms, py_syms, args.strict,
        args.katzenpost_tag, args.thinclient_tag, data_types_spec,
    )

    for msg in unresolved:
        print(f"UNRESOLVED: {msg}", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(doc, encoding="utf-8")
    print(f"wrote {args.output} ({len(doc)} bytes, {len(groups_raw)} groups)", file=sys.stderr)

    if args.strict and unresolved:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
