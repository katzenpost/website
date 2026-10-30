"""Check rendered directory-spec links and reciprocal links in related specs.

Hugo output URLs and fragments are authoritative, since slugs can differ from
source filenames. Legacy same-page references inside sibling specs are outside
this directory-spec check.
"""

import sys
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = set()
        self.content_links = []
        self.content_images = []
        self.div_depth = 0
        self.content_depth = None
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "div":
            self.div_depth += 1
            if "td-content" in attributes.get("class", "").split():
                self.content_depth = self.div_depth
        if tag == "a" and "href" in attributes and self.content_depth is not None:
            self.content_links.append(attributes["href"])
        if tag == "img" and "src" in attributes and self.content_depth is not None:
            self.content_images.append(attributes["src"])

    def handle_endtag(self, tag):
        if tag == "div":
            if self.div_depth == self.content_depth:
                self.content_depth = None
            self.div_depth -= 1


def destination(source, href):
    url = urlsplit(urljoin("https://katzenpost.network" + source, href))
    if url.hostname != "katzenpost.network" or not url.path.startswith("/docs/specs/"):
        return None
    path = unquote(url.path)
    if not Path(path).suffix:
        path = path.rstrip("/") + "/"
    return path, unquote(url.fragment)


def check(site):
    directory = "/docs/specs/dirauth/"
    errors = []

    @lru_cache(None)
    def page(path):
        target = site / path.lstrip("/")
        if not target.suffix:
            target = target / "index.html"
        if not target.is_file():
            raise ValueError(f"missing rendered target {path}")
        return Page(target.read_text(encoding="utf-8")) if target.suffix.lower() in {".html", ".htm"} else Page("")

    def validate(source, href):
        result = destination(source, href)
        if result is None:
            return None
        path, fragment = result
        try:
            target = page(path)
            if fragment and Path(path).suffix.lower() in {"", ".html", ".htm"} and fragment not in target.ids:
                raise ValueError(f"missing fragment #{fragment} in {path}")
        except ValueError as error:
            errors.append(f"{source}: {href}: {error}")
        return path

    try:
        document = page(directory)
    except ValueError as error:
        print(error)
        return 1
    siblings = set()
    for href in document.content_links:
        path = validate(directory, href)
        if path and path != directory and not Path(path).suffix and path != "/docs/specs/":
            siblings.add(path)
    for href in document.content_images:
        validate(directory, href)
    required = {"mixnet", "sphinx", "kemsphinx", "wireprotocol", "certificate",
                "thinclient", "mixdecoy", "packetreplay", "pigeonhole", "glossary", "pki"}
    for peer in required:
        if f"/docs/specs/{peer}/" not in siblings:
            errors.append(f"{directory}: no authored link to {peer}")
    for path in sorted(siblings):
        try:
            target = page(path)
        except ValueError:
            continue  # Already reported by validate.
        backlinks = []
        for href in target.content_links:
            result = destination(path, href)
            if result and result[0] != path:
                validate(path, href)
                if result[0] == directory:
                    backlinks.append(href)
        if not backlinks:
            errors.append(f"{path}: no authored backlink to {directory}")
    for error in errors:
        print(error)
    print(f"Rendered links and reciprocal navigation: {len(siblings)} related specs, {len(errors)} errors")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(check(Path(sys.argv[1] if len(sys.argv) > 1 else "public")))
