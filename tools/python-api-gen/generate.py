#!/usr/bin/env python3
"""Generate the Hugo/Docsy Python thin-client API page.

Pipeline:

  1. Read the pinned tag and checkout path (env overrides win over
     pinned-versions.env defaults).
  2. `git archive` the pinned tag's `katzenpost_thinclient` subtree
     into the build directory, so the working checkout is untouched.
  3. Substitute the export path into pydoc-markdown.yml.
  4. Run `pydoc-markdown` (native Python tooling) over the export.
  5. Prepend the Docsy front matter from preamble.md and write the
     page into content/en/docs/misc/.

This file does no API extraction of its own; pydoc-markdown is the
single source of the Python API content.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEBSITE_ROOT = HERE.parent.parent
OUTPUT = WEBSITE_ROOT / "content" / "en" / "docs" / "misc" / "python_thin_client_api.md"
BUILD_DIR = HERE / "build"
SRC_DIR = BUILD_DIR / "src"
PINNED_ENV = HERE / "pinned-versions.env"
CONFIG_TEMPLATE = HERE / "pydoc-markdown.yml"
PREAMBLE = HERE / "preamble.md"
VENV_PYDOC = HERE / ".venv" / "bin" / "pydoc-markdown"

_ASSIGN = re.compile(r"^\s*([A-Z_]+)\s*\?=\s*(.*?)\s*$")


def pinned(name: str) -> str:
    """Environment override, else the default from pinned-versions.env."""
    if name in os.environ and os.environ[name].strip():
        return os.environ[name].strip()
    for line in PINNED_ENV.read_text().splitlines():
        m = _ASSIGN.match(line)
        if m and m.group(1) == name:
            return m.group(2)
    sys.exit(f"error: {name} not set and absent from {PINNED_ENV}")


def export_pinned_tree(thinclient_path: str, tag: str) -> None:
    """git archive the pinned tag's package subtree into SRC_DIR."""
    if not (Path(thinclient_path) / ".git").exists():
        sys.exit(f"error: {thinclient_path} is not a git checkout")
    rev = subprocess.run(
        ["git", "-C", thinclient_path, "rev-parse", "--verify", "--quiet", f"{tag}^{{commit}}"],
        capture_output=True, text=True,
    )
    if rev.returncode != 0:
        sys.exit(f"error: tag '{tag}' does not resolve in {thinclient_path}")
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    archive = subprocess.Popen(
        ["git", "-C", thinclient_path, "archive", tag, "katzenpost_thinclient"],
        stdout=subprocess.PIPE,
    )
    tar = subprocess.Popen(["tar", "-xC", str(SRC_DIR)], stdin=archive.stdout)
    archive.stdout.close()
    tar.communicate()
    if tar.returncode != 0 or archive.wait() != 0:
        sys.exit("error: failed to export pinned thin_client tree")


def render_api() -> str:
    """Run pydoc-markdown over the export and return its markdown."""
    config = CONFIG_TEMPLATE.read_text().replace("@SRC@", str(SRC_DIR.resolve()))
    built_config = BUILD_DIR / "pydoc-markdown.yml"
    built_config.write_text(config)
    pydoc = str(VENV_PYDOC) if VENV_PYDOC.exists() else "pydoc-markdown"
    result = subprocess.run(
        [pydoc, str(built_config)], capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"error: pydoc-markdown failed:\n{result.stderr}")
    body = result.stdout.strip()
    if not body:
        sys.exit("error: pydoc-markdown produced no output")
    return space_sections(
        group_exceptions(flatten_setext(fence_doctests(body))))


_HEADING = re.compile(r"^(#{2,4}) +(.*)$")
_EXC_NAME = re.compile(r"(Error|Exception)$")


def group_exceptions(body: str) -> str:
    """Fold the exception subclasses under one "Exceptions" heading.

    The binding declares a long run of thin exception classes. As H3
    headings they swamped Docsy's right-hand table of contents. We
    insert a single `### Exceptions` heading before the first of them
    and demote each exception class (H3 to H4) and its members (H4 to
    H5), so the whole taxonomy collapses to one TOC entry while still
    rendering in full on the page.
    """
    out: list[str] = []
    in_fence = False
    in_group = False
    inserted = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        m = _HEADING.match(line) if not in_fence else None
        if m:
            level = len(m.group(1))
            name = m.group(2).replace("\\", "").strip()
            if level == 2:
                in_group = False
            elif level == 3:
                if _EXC_NAME.search(name):
                    if not inserted:
                        j = len(out)
                        while j > 0 and out[j - 1].strip() == "":
                            j -= 1
                        if j > 0 and _ANCHOR.match(out[j - 1]):
                            j -= 1
                        out[j:j] = [
                            '<a id="exceptions"></a>', "",
                            "### Exceptions", "",
                            "Error types raised by the thin client; each "
                            "derives from the standard library `Exception`.",
                            "",
                        ]
                        inserted = True
                    in_group = True
                    line = "#" + line
                else:
                    in_group = False
            elif level == 4 and in_group:
                line = "#" + line
        out.append(line)
    return "\n".join(out)


_PROMPT = re.compile(r"^(>>>|\.\.\.)( |$)")


def fence_doctests(body: str) -> str:
    """Wrap doctest example lines in a python code fence.

    Method docstrings give examples as two-space-indented `>>>`
    doctest lines. Goldmark reads the leading `>>>` as three nested
    blockquotes (the "three vertical lines"), and any `#` comment
    within becomes a heading. Collecting each run of prompt lines,
    stripping the prompts, and fencing the result as Python removes
    both hazards and yields a proper code block.
    """
    out: list[str] = []
    in_fence = False
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if not in_fence and _PROMPT.match(line.strip()):
            code: list[str] = []
            while i < len(lines) and _PROMPT.match(lines[i].strip()):
                stripped = lines[i].strip()
                code.append(stripped[3:].lstrip() if len(stripped) > 3 else "")
                i += 1
            out += ["", "```python", *code, "```", ""]
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


_SETEXT = re.compile(r"^(=|-){2,}\s*$")


def flatten_setext(body: str) -> str:
    """Demote RST underline titles in docstrings to bold text.

    Several module and class docstrings decorate section titles with
    `=====` / `-----` underlines. Goldmark reads those as setext H1/H2
    headings, so they hijacked the page hierarchy (a dozen stray H1s)
    and Docsy's TOC. Rewriting `Title` + underline to `**Title**`
    keeps the emphasis without minting a heading. Fenced code and our
    own thematic rules (a lone rule on a blank-flanked line) are left
    alone.
    """
    out: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if (not in_fence and _SETEXT.match(line) and out
                and out[-1].strip()
                and out[-1].lstrip()[:1] not in "#`-*<|>"):
            out[-1] = f"**{out[-1].strip()}**"
            continue
        out.append(line)
    return "\n".join(out)


_SECTION = re.compile(r"^#{2,3} \S")
_ANCHOR = re.compile(r'^<a id="[^"]*"></a>\s*$')


def space_sections(body: str) -> str:
    """Set a thematic rule before each module and top-level member.

    pydoc-markdown leaves only a single blank line between adjacent
    classes and functions, so they read as one squished column. A
    horizontal rule before every H2 (module) and H3 (class/function)
    section, placed above its anchor, gives each entry room to
    breathe. Methods (H4) keep no rule, so they stay grouped beneath
    their class. Fenced code is left untouched.
    """
    out: list[str] = []
    in_fence = False
    seen = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and _SECTION.match(line):
            if seen:
                j = len(out)
                while j > 0 and out[j - 1].strip() == "":
                    j -= 1
                if j > 0 and _ANCHOR.match(out[j - 1]):
                    j -= 1
                out[j:j] = ["", "---", ""]
            seen = True
        out.append(line)
    return "\n".join(out)


def main() -> None:
    tag = pinned("THINCLIENT_TAG")
    thinclient_path = pinned("THINCLIENT_PATH")

    if SRC_DIR.exists():
        subprocess.run(["rm", "-rf", str(SRC_DIR)], check=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    export_pinned_tree(thinclient_path, tag)
    body = render_api()

    front_matter = PREAMBLE.read_text().replace("@THINCLIENT_TAG@", tag)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(front_matter.rstrip() + "\n\n" + body + "\n")

    lines = OUTPUT.read_text().count("\n") + 1
    print(f"wrote {OUTPUT.relative_to(WEBSITE_ROOT)} "
          f"({lines} lines, thin_client {tag})")


if __name__ == "__main__":
    main()
