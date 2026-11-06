#!/usr/bin/env python3
"""Extract public API from a Python package directory as JSON.

Emits the common extractor schema (see README.md) on stdout.
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path


def is_public(name: str) -> bool:
    return not name.startswith("_")


def render_args(args: ast.arguments) -> str:
    """Render a function's arguments (incl. defaults, *args, **kwargs)."""
    parts: list[str] = []

    posonly = list(args.posonlyargs)
    normal = list(args.args)
    defaults = list(args.defaults)
    n_defaults = len(defaults)
    n_total = len(posonly) + len(normal)
    first_default_idx = n_total - n_defaults

    all_positional = posonly + normal
    for i, a in enumerate(all_positional):
        piece = a.arg
        if a.annotation is not None:
            piece += ": " + ast.unparse(a.annotation)
        if i >= first_default_idx:
            default = defaults[i - first_default_idx]
            piece += " = " + ast.unparse(default)
        parts.append(piece)
        if posonly and i == len(posonly) - 1:
            parts.append("/")

    if args.vararg is not None:
        v = "*" + args.vararg.arg
        if args.vararg.annotation is not None:
            v += ": " + ast.unparse(args.vararg.annotation)
        parts.append(v)
    elif args.kwonlyargs:
        parts.append("*")

    for kw, kwd in zip(args.kwonlyargs, args.kw_defaults):
        piece = kw.arg
        if kw.annotation is not None:
            piece += ": " + ast.unparse(kw.annotation)
        if kwd is not None:
            piece += " = " + ast.unparse(kwd)
        parts.append(piece)

    if args.kwarg is not None:
        kw = "**" + args.kwarg.arg
        if args.kwarg.annotation is not None:
            kw += ": " + ast.unparse(args.kwarg.annotation)
        parts.append(kw)

    return ", ".join(parts)


def render_function(node: ast.AST, receiver: str | None) -> str:
    assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    sig = prefix + node.name + "(" + render_args(node.args) + ")"
    if node.returns is not None:
        sig += " -> " + ast.unparse(node.returns)
    sig += ":"
    return sig


def render_class(node: ast.ClassDef) -> str:
    bases = [ast.unparse(b) for b in node.bases]
    head = "class " + node.name
    if bases:
        head += "(" + ", ".join(bases) + ")"
    head += ":"
    return head


def first_arg_is_self(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    args = (node.args.posonlyargs or []) + (node.args.args or [])
    return bool(args) and args[0].arg == "self"


def collect_monkey_patches(init_path: Path) -> dict[str, str]:
    """Scan __init__.py for `Class.attr = value` assignments.

    Returns a mapping from the rhs symbol name to the class name so that a
    module-level function `f` later discovered to be attached as
    `ThinClient.f = f` can be promoted to a method on `ThinClient`.
    """
    patches: dict[str, str] = {}
    if not init_path.is_file():
        return patches
    tree = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Attribute):
            continue
        if not isinstance(target.value, ast.Name):
            continue
        if not isinstance(node.value, ast.Name):
            continue
        patches[node.value.id] = target.value.id
    return patches


def extract_from_file(
    path: Path,
    relpath: str,
    symbols: list[dict],
    patches: dict[str, str],
) -> None:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        print(f"warning: cannot parse {path}: {e}", file=sys.stderr)
        return

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and is_public(node.name):
            symbols.append({
                "name": node.name,
                "kind": "class",
                "receiver": None,
                "signature": render_class(node),
                "doc": ast.get_docstring(node) or "",
                "file": relpath,
                "line": node.lineno,
            })
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(item.name):
                    symbols.append({
                        "name": item.name,
                        "kind": "method",
                        "receiver": node.name,
                        "signature": render_function(item, node.name),
                        "doc": ast.get_docstring(item) or "",
                        "file": relpath,
                        "line": item.lineno,
                    })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(node.name):
            receiver = patches.get(node.name)
            if receiver is None and first_arg_is_self(node):
                # Unassigned method-shaped function; leave as free function.
                pass
            kind = "method" if receiver else "function"
            symbols.append({
                "name": node.name,
                "kind": kind,
                "receiver": receiver,
                "signature": render_function(node, receiver),
                "doc": ast.get_docstring(node) or "",
                "file": relpath,
                "line": node.lineno,
            })


def main() -> int:
    p = argparse.ArgumentParser(description="Extract public Python API as JSON.")
    p.add_argument("srcdir", help="Python package directory to walk")
    args = p.parse_args()

    srcroot = Path(args.srcdir).resolve()
    if not srcroot.is_dir():
        print(f"error: {srcroot} is not a directory", file=sys.stderr)
        return 2

    patches = collect_monkey_patches(srcroot / "__init__.py")

    symbols: list[dict] = []
    for pyfile in sorted(srcroot.rglob("*.py")):
        rel = pyfile.relative_to(srcroot).as_posix()
        if rel.startswith("test_") or "/test_" in rel or rel.endswith("_test.py"):
            continue
        extract_from_file(pyfile, rel, symbols, patches)

    json.dump({"binding": "python", "symbols": symbols}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
