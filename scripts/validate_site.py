#!/usr/bin/env python3
"""Validate the static AWS portfolio site without third-party dependencies."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://bradleymatera.github.io/Office/"
AUDIT_DATE = date(2026, 8, 3)
PUBLIC_PAGES = (
    "index.html",
    "writing.html",
    "proof.html",
    "sources.html",
    "design-system.html",
)
ALL_PAGES = (*PUBLIC_PAGES, "404.html")


@dataclass
class PageReport:
    path: Path
    lang: str | None = None
    title: str = ""
    descriptions: list[str] = field(default_factory=list)
    canonicals: list[str] = field(default_factory=list)
    og_images: list[str] = field(default_factory=list)
    headings_one: list[str] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)
    local_refs: list[tuple[str, str]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    json_ld_blocks: list[str] = field(default_factory=list)
    main_count: int = 0
    skip_links: list[str] = field(default_factory=list)


class SiteHTMLParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.report = PageReport(path=path)
        self.capture_title = False
        self.capture_h1 = False
        self.capture_json_ld = False
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "html":
            self.report.lang = values.get("lang")
        elif tag == "title":
            self.capture_title = True
            self.title_parts = []
        elif tag == "h1":
            self.capture_h1 = True
            self.h1_parts = []
        elif tag == "main":
            self.report.main_count += 1

        element_id = values.get("id")
        if element_id:
            self.report.ids.append(element_id)

        if tag == "meta":
            self._handle_meta(values)
        elif tag == "link":
            self._handle_link(values)
        elif tag == "a":
            self._handle_anchor(values)

        if tag in {"img", "script", "source"}:
            src = values.get("src", "").strip()
            if src:
                self._record_reference("src", src)
        if tag == "img":
            self.report.images.append(values)
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self.capture_json_ld = True
            self.json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.capture_title:
            self.report.title = normalize_text(self.title_parts)
            self.capture_title = False
        elif tag == "h1" and self.capture_h1:
            self.report.headings_one.append(normalize_text(self.h1_parts))
            self.capture_h1 = False
        elif tag == "script" and self.capture_json_ld:
            block = "".join(self.json_ld_parts).strip()
            if block:
                self.report.json_ld_blocks.append(block)
            self.capture_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.capture_title:
            self.title_parts.append(data)
        if self.capture_h1:
            self.h1_parts.append(data)
        if self.capture_json_ld:
            self.json_ld_parts.append(data)

    def _handle_meta(self, values: dict[str, str]) -> None:
        content = values.get("content", "").strip()
        if not content:
            return
        if values.get("name", "").lower() == "description":
            self.report.descriptions.append(content)
        if values.get("property", "").lower() == "og:image":
            self.report.og_images.append(content)

    def _handle_link(self, values: dict[str, str]) -> None:
        href = values.get("href", "").strip()
        if not href:
            return
        rel = {part.lower() for part in values.get("rel", "").split()}
        if "canonical" in rel:
            self.report.canonicals.append(href)
        self._record_reference("href", href)

    def _handle_anchor(self, values: dict[str, str]) -> None:
        href = values.get("href", "").strip()
        if not href:
            return
        self._record_reference("href", href)
        if "skip-link" in values.get("class", "").split():
            self.report.skip_links.append(href)

    def _record_reference(self, attribute: str, value: str) -> None:
        parsed = urlparse(value)
        if parsed.scheme or parsed.netloc or value.startswith(("mailto:", "tel:", "data:")):
            return
        self.report.local_refs.append((attribute, value))


def normalize_text(parts: list[str]) -> str:
    return " ".join("".join(parts).split())


def parse_html(path: Path) -> PageReport:
    parser = SiteHTMLParser(path)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.report


def resolve_local_reference(page: Path, reference: str) -> tuple[Path, str]:
    parsed = urlparse(reference)
    raw_path = unquote(parsed.path)
    if not raw_path:
        target = page
    elif raw_path.startswith("/"):
        target = ROOT / raw_path.lstrip("/")
    else:
        target = page.parent / raw_path
    if target.is_dir():
        target /= "index.html"
    return target.resolve(), parsed.fragment


def validate_page(report: PageReport, *, require_canonical: bool) -> list[str]:
    errors: list[str] = []
    relative = report.path.relative_to(ROOT)

    if report.lang != "en":
        errors.append(f"{relative}: html lang must be 'en'")
    if not report.title:
        errors.append(f"{relative}: missing title")
    if len(report.descriptions) != 1:
        errors.append(f"{relative}: expected one meta description, found {len(report.descriptions)}")
    if require_canonical and len(report.canonicals) != 1:
        errors.append(f"{relative}: expected one canonical link, found {len(report.canonicals)}")
    if not require_canonical and len(report.canonicals) > 1:
        errors.append(f"{relative}: more than one canonical link")
    if len(report.headings_one) != 1 or not report.headings_one[0]:
        errors.append(f"{relative}: expected one non-empty h1, found {len(report.headings_one)}")
    if report.main_count != 1:
        errors.append(f"{relative}: expected one main landmark, found {report.main_count}")
    if not report.skip_links:
        errors.append(f"{relative}: missing skip link")

    duplicate_ids = sorted(item for item, count in Counter(report.ids).items() if count > 1)
    if duplicate_ids:
        errors.append(f"{relative}: duplicate ids: {', '.join(duplicate_ids)}")

    for image in report.images:
        if "alt" not in image:
            errors.append(f"{relative}: image missing alt attribute: {image.get('src', '<unknown>')}")
        if not image.get("src"):
            errors.append(f"{relative}: image missing src")

    for number, block in enumerate(report.json_ld_blocks, start=1):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON-LD block {number}: {exc}")

    errors.extend(validate_local_references(report))
    errors.extend(validate_og_images(report))

    if require_canonical and report.canonicals and not report.canonicals[0].startswith(BASE_URL):
        errors.append(f"{relative}: canonical must start with {BASE_URL}")
    return errors


def validate_local_references(report: PageReport) -> list[str]:
    errors: list[str] = []
    relative = report.path.relative_to(ROOT)
    ids = set(report.ids)
    for attribute, reference in report.local_refs:
        target, fragment = resolve_local_reference(report.path, reference)
        if reference.startswith("#"):
            if fragment not in ids:
                errors.append(f"{relative}: missing local fragment target {reference}")
            continue
        try:
            target.relative_to(ROOT)
        except ValueError:
            errors.append(f"{relative}: {attribute} escapes repository root: {reference}")
            continue
        if not target.exists():
            errors.append(f"{relative}: missing local {attribute} target: {reference}")
    return errors


def validate_og_images(report: PageReport) -> list[str]:
    errors: list[str] = []
    relative = report.path.relative_to(ROOT)
    for image_url in report.og_images:
        parsed = urlparse(image_url)
        if parsed.netloc != "bradleymatera.github.io" or not parsed.path.startswith("/Office/"):
            continue
        local_path = ROOT / parsed.path.removeprefix("/Office/")
        if not local_path.exists():
            errors.append(f"{relative}: missing local Open Graph image: {local_path.relative_to(ROOT)}")
    return errors


def validate_content_index() -> list[str]:
    path = ROOT / "data/aws-content.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"data/aws-content.json: unable to parse: {exc}"]

    errors: list[str] = []
    for name in ("articles", "devArticles", "repositories"):
        if not isinstance(data.get(name), list) or not data[name]:
            errors.append(f"data/aws-content.json: {name} must be a non-empty list")

    article_ids: set[str] = set()
    article_urls: set[str] = set()
    for article in data.get("articles", []):
        article_id = article.get("id")
        article_url = article.get("url")
        if not article_id or article_id in article_ids:
            errors.append(f"data/aws-content.json: missing or duplicate article id {article_id!r}")
        article_ids.add(article_id)
        if not article_url or article_url in article_urls:
            errors.append(f"data/aws-content.json: missing or duplicate article URL {article_url!r}")
        article_urls.add(article_url)

        try:
            published = date.fromisoformat(article["date"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"data/aws-content.json: invalid date for article {article_id!r}")
            continue
        if published > AUDIT_DATE:
            errors.append(f"data/aws-content.json: future-dated article {article_id!r}: {published}")

        image = article.get("image")
        if not image or not (ROOT / image).exists():
            errors.append(f"data/aws-content.json: missing article image for {article_id!r}: {image!r}")
    return errors


def validate_xml_files() -> list[str]:
    errors: list[str] = []
    for relative in ("sitemap.xml", "rss.xml"):
        try:
            ElementTree.parse(ROOT / relative)
        except (OSError, ElementTree.ParseError) as exc:
            errors.append(f"{relative}: invalid XML: {exc}")
    return errors


def validate_support_files() -> list[str]:
    errors: list[str] = []
    try:
        json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"site.webmanifest: invalid JSON: {exc}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {BASE_URL}sitemap.xml" not in robots:
        errors.append("robots.txt: missing canonical sitemap declaration")

    required = (
        ".nojekyll",
        "favicon.svg",
        "site.webmanifest",
        "robots.txt",
        "sitemap.xml",
        "rss.xml",
        "llms.txt",
        "humans.txt",
        "styles.css",
        "hub.css",
        "assets/og/aws-metadata-workflow.png",
    )
    for relative in required:
        if not (ROOT / relative).exists():
            errors.append(f"missing required production file: {relative}")
    return errors


def validate_svg_accessibility() -> list[str]:
    errors: list[str] = []
    svg_paths = list((ROOT / "assets").glob("*.svg"))
    svg_paths.extend((ROOT / "assets/content").glob("*.svg"))
    for path in svg_paths:
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid SVG XML: {exc}")
            continue
        namespace = "{http://www.w3.org/2000/svg}"
        if root.find(f"{namespace}title") is None:
            errors.append(f"{path.relative_to(ROOT)}: missing SVG title")
        if root.find(f"{namespace}desc") is None:
            errors.append(f"{path.relative_to(ROOT)}: missing SVG description")
    return errors


def duplicate_value_errors(reports: list[PageReport], attribute: str, label: str) -> list[str]:
    values: dict[str, list[str]] = {}
    for report in reports:
        for value in getattr(report, attribute):
            values.setdefault(value, []).append(str(report.path.relative_to(ROOT)))
    return [
        f"duplicate {label} {value!r}: {', '.join(pages)}"
        for value, pages in values.items()
        if value and len(pages) > 1
    ]


def main() -> int:
    errors: list[str] = []
    reports: list[PageReport] = []
    for relative in ALL_PAGES:
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing public page: {relative}")
            continue
        report = parse_html(path)
        reports.append(report)
        errors.extend(validate_page(report, require_canonical=relative in PUBLIC_PAGES))

    errors.extend(duplicate_value_errors(reports, "headings_one", "h1"))
    errors.extend(duplicate_value_errors(reports, "canonicals", "canonical URL"))
    title_counter = Counter(report.title for report in reports if report.title)
    for title, count in title_counter.items():
        if count > 1:
            errors.append(f"duplicate page title {title!r}")

    errors.extend(validate_content_index())
    errors.extend(validate_xml_files())
    errors.extend(validate_support_files())
    errors.extend(validate_svg_accessibility())

    if errors:
        print("Static site validation failed:", file=sys.stderr)
        for error in sorted(errors):
            print(f"- {error}", file=sys.stderr)
        return 1

    svg_count = len(list((ROOT / "assets").glob("*.svg")))
    svg_count += len(list((ROOT / "assets/content").glob("*.svg")))
    print(f"Static site validation passed: {len(reports)} HTML pages, {svg_count} SVG assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
