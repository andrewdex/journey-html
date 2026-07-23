#!/usr/bin/env python3
"""Validate a generated Journey HTML artifact using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_SECTIONS = {"summary", "journey", "evidence", "verification"}
FORBIDDEN_TAGS = {"script", "iframe", "object", "embed", "form"}
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    "OpenAI-style token": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}


class JourneyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.sections: set[str] = set()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.has_lang = False
        self.has_viewport = False
        self.in_title = False
        self.title_parts: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.tags.append(tag)
        attributes = {key.lower(): value or "" for key, value in attrs}

        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"Forbidden <{tag}> element")
        if tag == "html" and attributes.get("lang", "").strip():
            self.has_lang = True
        if tag == "meta" and attributes.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1

        section = attributes.get("data-journey-section", "").strip().lower()
        if section:
            self.sections.add(section)

        for name, value in attributes.items():
            if name.startswith("on"):
                self.errors.append(f"Inline event handler '{name}' is forbidden")
            if name in {"href", "src", "action", "poster"} and value:
                self._check_url(tag, name, value.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    def _check_url(self, tag: str, name: str, value: str) -> None:
        lowered = value.lower()
        parsed = urlparse(value)
        if lowered.startswith("javascript:") or lowered.startswith("data:text/html"):
            self.errors.append(f"Unsafe URL in <{tag}> {name}")
        elif parsed.scheme in {"http", "https", "//"} or value.startswith("//"):
            self.errors.append(f"Remote URL in <{tag}> {name}: {value}")
        elif parsed.scheme and parsed.scheme not in {"data", "mailto", "tel"}:
            self.errors.append(f"Unsupported URL scheme '{parsed.scheme}' in <{tag}> {name}")


def validate(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return {"valid": False, "errors": [f"File not found: {path}"], "warnings": []}
    if path.suffix.lower() not in {".html", ".htm"}:
        errors.append("Output must use an .html or .htm extension")

    raw = path.read_text(encoding="utf-8")
    parser = JourneyParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception as exc:  # HTMLParser errors are uncommon but should be actionable.
        errors.append(f"HTML parsing failed: {exc}")

    errors.extend(parser.errors)
    warnings.extend(parser.warnings)

    if not re.search(r"<!doctype\s+html", raw, re.IGNORECASE):
        errors.append("Missing HTML5 doctype")
    if not parser.has_lang:
        errors.append("Missing non-empty lang attribute on <html>")
    if not parser.has_viewport:
        errors.append("Missing viewport meta element")

    title = " ".join(parser.title_parts).strip()
    if not title:
        errors.append("Missing non-empty <title>")
    if parser.h1_count != 1:
        errors.append(f"Expected exactly one <h1>; found {parser.h1_count}")

    missing_sections = sorted(REQUIRED_SECTIONS - parser.sections)
    if missing_sections:
        errors.append("Missing required data-journey-section values: " + ", ".join(missing_sections))

    placeholders = sorted(set(PLACEHOLDER.findall(raw)))
    if placeholders:
        errors.append("Unresolved template placeholders: " + ", ".join(placeholders[:10]))
    if "```" in raw:
        errors.append("Markdown fence found in HTML output")
    if re.search(r"url\(\s*['\"]?https?://", raw, re.IGNORECASE):
        errors.append("Remote URL found in CSS")

    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(raw):
            errors.append(f"Possible {label} found; redact before sharing")

    size_bytes = path.stat().st_size
    if size_bytes > 3_000_000:
        warnings.append(f"File is large ({size_bytes} bytes); confirm embedded assets are necessary")

    return {
        "valid": not errors,
        "file": str(path.resolve()),
        "size_bytes": size_bytes,
        "sections": sorted(parser.sections),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def main() -> int:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("html_file", type=Path)
    argument_parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print only the machine-readable JSON result.",
    )
    args = argument_parser.parse_args()

    result = validate(args.html_file)
    if not args.json_only:
        status = "PASS" if result["valid"] else "FAIL"
        print(f"Journey HTML validation: {status}")
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
