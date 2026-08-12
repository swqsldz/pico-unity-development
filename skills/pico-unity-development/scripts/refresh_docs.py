#!/usr/bin/env python3
"""Refresh the local PICO Unity Integration llms.txt corpus (stdlib only)."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


SOURCES = {
    "zh": "https://developer-cn.picoxr.com/llmstxt/document/unity-integration/zh/llms.txt",
    "en": "https://developer-cn.picoxr.com/llmstxt/document/unity-integration/en/llms.txt",
}
LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
MAX_BYTES = 20 * 1024 * 1024


class FetchError(RuntimeError):
    """A remote document could not be safely fetched."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def line_count(text: str) -> int:
    """Count logical lines without treating a trailing newline as an empty line."""
    return text.count("\n") + (1 if text and not text.endswith("\n") else 0)


def read_text(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    try:
        return data, data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FetchError(f"not UTF-8: {path}") from exc


def text_is_safe(data: bytes, content_type: str, url: str) -> str:
    lowered_type = content_type.lower().split(";", 1)[0].strip()
    if lowered_type and not (lowered_type.startswith("text/") or "markdown" in lowered_type):
        raise FetchError(f"non-text Content-Type {lowered_type!r}: {url}")
    try:
        value = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FetchError(f"response is not UTF-8: {url}") from exc
    sample = value.lstrip("\ufeff \t\r\n").lower()
    if "html" in lowered_type or sample.startswith("<!doctype html") or sample.startswith("<html"):
        raise FetchError(f"HTML response rejected: {url}")
    return value


def fetch(url: str, timeout: float, retries: int) -> tuple[bytes, str]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "pico-unity-development-doc-refresh/1.0"})
            with urlopen(request, timeout=timeout) as response:
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise FetchError(f"response exceeds {MAX_BYTES} byte limit: {url}")
                return data, text_is_safe(data, response.headers.get("Content-Type", ""), url)
        except (HTTPError, URLError, TimeoutError, OSError, FetchError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 4))
    raise FetchError(f"failed after {retries + 1} attempt(s): {url}: {last_error}")


def markdown_links(text: str, lang: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    required_prefix = f"/llmstxt/document/unity-integration/{lang}/"
    for title, raw_url in LINK_RE.findall(text):
        url = raw_url.strip("<>")
        parsed = urlparse(url)
        if (parsed.scheme not in {"http", "https"} or parsed.hostname != "developer-cn.picoxr.com"
                or not parsed.path.startswith(required_prefix) or not parsed.path.endswith(".md")):
            continue
        if url not in seen:
            seen.add(url)
            links.append({"title": title.strip(), "url": url})
    return links


def local_doc_path(docs_dir: Path, url: str, used: set[Path]) -> Path:
    name = unquote(Path(urlparse(url).path).name) or "index.md"
    # Keep the source filename whenever possible; suffix only if a feed has a collision.
    candidate = docs_dir / name
    if candidate not in used:
        used.add(candidate)
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    candidate = docs_dir / f"{stem}-{sha256(url.encode('utf-8'))[:10]}{suffix or '.md'}"
    used.add(candidate)
    return candidate


def document_record(lang: str, title: str, url: str, path: Path, data: bytes) -> dict[str, Any]:
    return {
        "language": lang,
        "title": title,
        "local_path": path.as_posix(),
        "source_url": url,
        "sha256": sha256(data),
        "bytes": len(data),
        "lines": line_count(data.decode("utf-8")),
    }


def catalog(records: list[dict[str, Any]]) -> str:
    lines = ["# PICO Unity Integration documentation catalog", ""]
    for lang, title in (("zh", "中文"), ("en", "English")):
        lines.extend([f"## {title}", "", "| Language | Title | Local path | Source URL |", "| --- | --- | --- | --- |"])
        for item in (record for record in records if record["language"] == lang):
            lines.append(f"| {item['language']} | {item['title']} | `{item['local_path']}` | {item['source_url']} |")
        lines.append("")
    return "\n".join(lines)


def check(root: Path) -> int:
    failures: list[str] = []
    records: list[dict[str, Any]] = []
    meta: dict[str, Any] = {}
    source_hashes: dict[str, str] = {}
    for lang in SOURCES:
        source = root / "sources" / lang / "llms.txt"
        if not source.exists():
            failures.append(f"missing source: {source}")
            continue
        try:
            data, content = read_text(source)
            text_is_safe(data, "text/plain", str(source))
            source_hashes[lang] = sha256(data)
        except (FetchError, OSError) as exc:
            failures.append(str(exc))
            continue
        used: set[Path] = set()
        for link in markdown_links(content, lang):
            target = local_doc_path(root / "docs" / lang, link["url"], used)
            if not target.exists():
                failures.append(f"missing document: {target} ({link['url']})")
                continue
            try:
                data, _ = read_text(target)
                text_is_safe(data, "text/markdown", str(target))
                records.append(document_record(lang, link["title"], link["url"], target.relative_to(root), data))
            except (FetchError, OSError) as exc:
                failures.append(str(exc))
    catalog_path = root / "catalog.md"
    meta_path = root / "source-meta.json"
    if not catalog_path.exists():
        failures.append(f"missing generated file: {catalog_path}")
    if not meta_path.exists():
        failures.append(f"missing generated file: {meta_path}")
    else:
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"invalid metadata: {exc}")
    if meta:
        if meta.get("success_count") != len(records):
            failures.append(f"metadata success_count is {meta.get('success_count')!r}, expected {len(records)}")
        if meta.get("failure_count") != 0:
            failures.append(f"metadata failure_count is {meta.get('failure_count')!r}, expected 0")
        for lang, digest in source_hashes.items():
            recorded_source = meta.get("sources", {}).get(lang, {})
            if recorded_source.get("sha256") and recorded_source["sha256"] != digest:
                failures.append(f"metadata SHA256 mismatch: sources/{lang}/llms.txt")
        recorded = {item.get("local_path"): item for item in meta.get("documents", []) if isinstance(item, dict)}
        for record in records:
            prior = recorded.get(record["local_path"])
            if prior is not None and prior.get("sha256") != record["sha256"]:
                failures.append(f"metadata SHA256 mismatch: {record['local_path']}")
    if failures:
        print("CHECK FAILED:", *[f"- {item}" for item in failures], sep="\n", file=sys.stderr)
        return 1
    print(f"CHECK OK: {len(records)} documents across {len(SOURCES)} language(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "references")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--check", action="store_true", help="validate local corpus only; do not use the network")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 16 or args.timeout <= 0 or args.retries < 0:
        parser.error("workers must be 1..16, timeout > 0, and retries >= 0")
    root = args.output.resolve()
    if args.check:
        return check(root)

    failures: list[str] = []
    source_texts: dict[str, str] = {}
    source_records: dict[str, dict[str, Any]] = {}
    for lang, url in SOURCES.items():
        try:
            data, content = fetch(url, args.timeout, args.retries)
            source_texts[lang] = content
            source_records[lang] = {"url": url, "sha256": sha256(data), "bytes": len(data),
                                    "lines": line_count(content), "links": len(markdown_links(content, lang))}
            path = root / "sources" / lang / "llms.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        except (FetchError, OSError) as exc:
            failures.append(f"[{lang}] llms.txt: {exc}")

    jobs: list[tuple[str, str, str, Path]] = []
    for lang, content in source_texts.items():
        used: set[Path] = set()
        for link in markdown_links(content, lang):
            jobs.append((lang, link["title"], link["url"], local_doc_path(root / "docs" / lang, link["url"], used)))
    records: list[dict[str, Any]] = []

    def download(job: tuple[str, str, str, Path]) -> dict[str, Any]:
        lang, title, url, path = job
        data, _ = fetch(url, args.timeout, args.retries)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return document_record(lang, title, url, path.relative_to(root), data)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download, job): job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            lang, _, url, _ = futures[future]
            try:
                records.append(future.result())
            except Exception as exc:  # Also retain local I/O and executor failures in the manifest.
                failures.append(f"[{lang}] {url}: {exc}")

    records.sort(key=lambda item: (item["language"], item["local_path"]))

    def slug(item: dict[str, Any]) -> str:
        name = Path(urlparse(item["source_url"]).path).stem
        return name[3:] if item["language"] == "en" and name.startswith("en_") else name

    zh_slugs = {slug(item) for item in records if item["language"] == "zh"}
    en_slugs = {slug(item) for item in records if item["language"] == "en"}
    meta = {"fetched_at": datetime.now(timezone.utc).isoformat(), "sources": source_records,
            "documents": records, "success_count": len(records), "failure_count": len(failures),
            "failures": failures,
            "language_pair_differences": {"zh_only_slugs": sorted(zh_slugs - en_slugs), "en_only_slugs": sorted(en_slugs - zh_slugs)}}
    root.mkdir(parents=True, exist_ok=True)
    (root / "catalog.md").write_text(catalog(records), encoding="utf-8", newline="\n")
    (root / "source-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if failures:
        print("REFRESH FAILED:", *[f"- {item}" for item in failures], sep="\n", file=sys.stderr)
        return 1
    print(f"REFRESH OK: {len(records)} documents across {len(SOURCES)} language(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
