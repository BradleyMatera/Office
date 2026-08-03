#!/usr/bin/env python3
"""Validate the static AWS portfolio site without third-party dependencies."""

from __future__ import annotations

import json
import sys
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
ERROR_PAGE = "404.html"


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
        self._capture_title = False
        self._capture_h1 = False
        self._capture_json_ld = False
        self._title_parts: list[str] = []
        self._h1_parts: list[str] = []
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "html":
            self.report.lang = values.get("lang")
        if tag == "title":
            self._capture_title = True
            self._title_parts = []
        if tag == "h1":
            self._capture_h1 = True
            self._h1_parts = []
        if tag == "main":
            self.report.main_count += 1
        if element_id := values.get("id"):
            self.report.ids.append(element_id)
        if tag == "meta":
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            content = values.get("content", "").strip()
            if name == "description" and content:
                self.report.descriptions.append(content)
            if prop == "og:image" and content:
                self.report.og_images.append(content)
        if tag == "link":
            rel = {part.lower() for part in values.get("rel", "").split()}
            href = values.get("href", "").strip()
            if "canonical" in rel and href:
                self.report.canonicals.append(href)
            if href:
                self._record_reference("href", href)
        if tag == "a":
            href = values.get("href", "").strip()
            if href:
                self._record_reference("href", href)
                classes = set(values.get("class", "").split())
                if "skip-link" in classes:
                    self.report.skip_links.append(href)
        if tag in {"img", "script", "source"}:
            src = values.get("src", "").strip()
            if src:
                self._record_reference("src", src)
        if tag == "img":
            self.report.images.append(values)
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._capture_json_ld = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._capture_title:
            self.report.title = " ".join("".join(self._title_parts).split())
            self._capture_title = False
        if tag == "h1" and self._capture_h1:
            text = " ".join("".join(self._h1_parts).split())
            self.report.headings_one.append(text)
            self._capture_h1 = False
        if tag == "script" and self._capture_json_ld:
            block = "".join(self._json_ld_parts).strip()
            if block:
                self.report.json_ld_blocks.append(block)
            self._capture_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)
        if self._capture_h1:
            self._h1_parts.append(data)
        if self._capture_json_ld:
            self._json_ld_parts.append(data)

    def _record_reference(self, attribute: str, value: str) -> None:
        parsed = urlparse(value)
        if parsed.scheme or parsed.netloc or value.startswith(("mailto:", "tel:", "data:")):
            return
        self.report.local_refs.append((attribute, value))


def parse_html(path: Path) -> PageReport:
    parser = SiteHTMLParser(path)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.report


def resolve_local_reference(page: Path, reference: str) -> tuple[Path, str]:
    parsed = urlparse(reference)
    raw_path = unquote(parsed.path)
    target = page if not raw_path else (ROOT / raw_path.lstrip("/")) if raw_path.startswith("/") else page.parent / raw_path
    if target.is_dir():
        target = target / "index.html"
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
    duplicates = sorted({element_id for element_id in report.ids if report.ids.count(element_id) > 1})
    if duplicates:
        errors.append(f"{relative}: duplicate ids: {', '.join(duplicates)}")

    for image in report.images:
        if "alt" not in image:
            errors.append(f"{relative}: image missing alt attribute: {image.get('src', '<unknown>')}")
        if not image.get("src"):
            errors.append(f"{relative}: image missing src")

    for block_number, block in enumerate(report.json_ld_blocks, start=1):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON-LD block {block_number}: {exc}")

    id_set = set(report.ids)
    for attribute, reference in report.local_refs:
        target, fragment = resolve_local_reference(report.path, reference)
        if reference.startswith("#"):
            if fragment not in id_set:
                errors.append(f"{relative}: missing local fragment target {reference}")
            continue
        try:
            target.relative_to(ROOT)
        except ValueError:
            errors.append(f"{relative}: {attribute} escapes repository root: {reference}")
            continue
        if not target.exists():
            errors.append(f"{relative}: missing local {attribute} target: {reference}")

    for og_image in report.og_images:
        parsed = urlparse(og_image)
        if parsed.netloc == "bradleymatera.github.io" and parsed.path.startswith("/Office/"):
            local_path = ROOT / parsed.path.removeprefix("/Office/")
            if not local_path.exists():
                errors.append(f"{relative}: missing local Open Graph image: {local_path.relative_to(ROOT)}")

    if require_canonical and report.canonicals:
        canonical = report.canonicals[0]
        if not canonical.startswith(BASE_URL):
            errors.append(f"{relative}: canonical must start with {BASE_URL}")
    return errors


def validate_content_index() -> list[str]:
    errors: list[str] = []
    path = ROOT / "data/aws-content.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"data/aws-content.json: unable to parse: {exc}"]

    for collection_name in ("articles", "devArticles", "repositories"):
        if not isinstance(data.get(collection_name), list) or not data[collection_name]:
            errors.append(f"data/aws-content.json: {collection_name} must be a non-empty list")

    article_ids: set[str] = set()
    article_urls: set[str] = set()
    for article in data.get("articles", []):
        article_id = article.get("id")
        url = article.get("url")
        if not article_id or article_id in article_ids:
            errors.append(f"data/aws-content.json: missing or duplicate article id {article_id!r}")
        article_ids.add(article_id)
        if not url or url in article_urls:
            errors.append(f"data/aws-content.json: missing or duplicate article URL {url!r}")
        article_urls.add(url)
        try:
            published = date.fromisoformat(article["date"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"data/aws-content.json: invalid date for article {article_id!r}")
        else:
            if published > AUDIT_DATE:
                errors.append(f"data/aws-content.json: future-dated article {article_id!r}: {published}")
        image = article.get("image")
        if not image or not (ROOT / image).exists():
            errors.append(f"data/aws-content.json: missing article image for {article_id!r}: {image!r}")
    return errors


def validate_xml_files() -> list[str]:
    errors: list[str] = []
    for relative in ("sitemap.xml", "rss.xml"):
        path = ROOT / relative
        try:
            ElementTree.parse(path)
        except (OSError, ElementTree.ParseError) as exc:
            errors.append(f"{relative}: invalid XML: {exc}")
    return errors


def validate_support_files() -> list[str]:
    errors: list[str] = []
    manifest = ROOT / "site.webmanifest"
    try:
        json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"site.webmanifest: invalid JSON: {exc}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    expected_sitemap = f"Sitemap: {BASE_URL}sitemap.xml"
    if expected_sitemap not in robots:
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
    )
    for relative in required:
        if not (ROOT / relative).exists():
            errors.append(f"missing required production file: {relative}")
    return errors


def validate_svg_accessibility() -> list[str]:
    errors: list[str] = []
    for directory in (ROOT / "assets", ROOT / "assets/content"):
        if not directory.exists():
            continue
        for path in directory.glob("*.svg"):
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


def main() -> int:
    errors: list[str] = []
    reports: list[PageReport] = []
    for relative in (*PUBLIC_PAGES, ERROR_PAGE):
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing public page: {relative}")
            continue
        report = parse_html(path)
        reports.append(report)
        errors.extend(validate_page(report, require_canonical=relative in PUBLIC_PAGES))

    title_map: dict[str, list[str]] = {}
    canonical_map: dict[str, list[str]] = {}
    for report in reports:
        title_map.setdefault(report.title, []).append(str(report.path.relative_to(ROOT)))
        for canonical in report.canonicals:
            canonical_map.setdefault(canonical, []).append(str(report.path.relative_to(ROOT)))
    for title, pages in title_map.items():
        if title and len(pages) > 1:
            errors.append(f"duplicate page title {title!r}: {', '.join(pages)}")
    for canonical, pages in canonical_map.items():
        if len(pages) > 1:
            errors.append(f"duplicate canonical URL {canonical!r}: {', '.join(pages)}")

    errors.extend(validate_content_index())
    errors.extend(validate_xml_files())
    errors.extend(validate_support_files())
    errors.extend(validate_svg_accessibility())

    if errors:
        print("Static site validation failed:", file=sys.stderr)
        for error in sorted(errors):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Static site validation passed: {len(reports)} HTML pages, "
        f"{len(list((ROOT / 'assets').glob('*.svg'))) + len(list((ROOT / 'assets/content').glob('*.svg')))} SVG assets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
