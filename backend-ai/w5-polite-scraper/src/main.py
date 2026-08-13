"""
The Polite Scraper — FlyRank Internship Week 5 Assignment A9
=============================================================
Pipeline: classify → fetch → extract → normalize → validate → store → report

Target : Books to Scrape (https://books.toscrape.com)
         A public sandbox built exactly for scraping practice.
Scope  : First 3 catalogue pages → 60 book detail pages
Output : output/books.json, output/errors.json, output/run-report.json
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError, field_validator

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL    = "https://books.toscrape.com/catalogue/"
START_URL   = "https://books.toscrape.com/catalogue/page-1.html"
REPO_URL    = "https://github.com/prime-programmer-ar/flyrank-w5-polite-scraper"

USER_AGENT  = f"FlyRankInternship-A9/1.0 (+{REPO_URL})"
TIMEOUT     = 10          # seconds per request
DELAY       = 0.6         # seconds between real (non-cached) requests
MAX_PAGES   = 3           # catalogue pages to visit
MAX_RETRIES = 1           # retries on 5xx / timeout

CACHE_DIR   = Path("cache")
OUTPUT_DIR  = Path("output")
BOOKS_FILE  = OUTPUT_DIR / "books.json"
ERRORS_FILE = OUTPUT_DIR / "errors.json"
REPORT_FILE = OUTPUT_DIR / "run-report.json"

CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Pydantic schema ───────────────────────────────────────────────────────────

WORD_TO_INT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
}


class BookRecord(BaseModel):
    """Validated, normalized book record."""
    title:             str
    product_url:       str           # canonical identity
    price_text:        str           # raw, e.g. "£51.77"
    price_gbp:         float         # normalized number
    availability_text: str
    in_stock:          bool
    rating_text:       str
    rating:            int           # 1–5
    description:       Optional[str] # null when missing — never invented
    source_page:       str
    fetched_at:        str           # ISO-8601 UTC

    @field_validator("price_gbp")
    @classmethod
    def price_positive(cls, v):
        if v < 0:
            raise ValueError("price_gbp must be non-negative")
        return v

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("rating must be 1–5")
        return v

    @field_validator("product_url", "source_page")
    @classmethod
    def must_be_https(cls, v):
        if not v.startswith("https://"):
            raise ValueError(f"URL must start with https://: {v}")
        return v


# ── HTTP helpers ──────────────────────────────────────────────────────────────

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

_stats = {
    "fetched":    0,
    "cache_hits": 0,
    "failed":     0,
    "start_time": None,
}


def _cache_path(url: str) -> Path:
    """Turn a URL into a safe filename inside cache/."""
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", url.replace("https://", ""))
    return CACHE_DIR / (safe[:180] + ".html")


def fetch(url: str) -> Optional[str]:
    """
    Fetch a page with caching, polite delay, timeout, and one retry on 5xx.

    Returns HTML text on success, None on any failure.
    Never fetches from cache? No delay needed — the file never leaves disk.
    """
    path = _cache_path(url)

    if path.exists():
        _stats["cache_hits"] += 1
        print(f"  CACHE HIT  {url}")
        return path.read_text(encoding="utf-8")

    # Polite delay before every real request
    time.sleep(DELAY)

    for attempt in range(1 + MAX_RETRIES):
        try:
            resp = session.get(url, timeout=TIMEOUT)

            if resp.status_code == 200:
                path.write_text(resp.text, encoding="utf-8")
                _stats["fetched"] += 1
                print(f"  FETCH      {url}  ({len(resp.text):,} bytes)")
                return resp.text

            if resp.status_code in (403, 404):
                # Do NOT retry — asking again won't help
                print(f"  SKIP {resp.status_code}  {url}")
                _stats["failed"] += 1
                return None

            # 5xx — wait and retry once
            if attempt < MAX_RETRIES:
                print(f"  RETRY ({resp.status_code})  {url}")
                time.sleep(2)
                continue

            print(f"  FAIL {resp.status_code}  {url}")
            _stats["failed"] += 1
            return None

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                print(f"  TIMEOUT — retrying {url}")
                time.sleep(2)
                continue
            print(f"  TIMEOUT — giving up {url}")
            _stats["failed"] += 1
            return None

        except requests.exceptions.RequestException as exc:
            print(f"  ERROR {exc}  {url}")
            _stats["failed"] += 1
            return None

    _stats["failed"] += 1
    return None


# ── Stage 2: Catalogue crawler ────────────────────────────────────────────────

def discover_book_urls() -> list[str]:
    """
    Follow the catalogue's own 'next' links for up to MAX_PAGES pages.
    Collect and deduplicate all book URLs found.
    """
    book_urls: list[str] = []
    page_url   = START_URL
    pages_seen = 0

    while page_url and pages_seen < MAX_PAGES:
        html = fetch(page_url)
        if not html:
            print(f"  Could not fetch catalogue page: {page_url}")
            break

        soup        = BeautifulSoup(html, "html.parser")
        pages_seen += 1

        # Collect book links on this page
        for article in soup.select("article.product_pod"):
            a    = article.select_one("h3 > a")
            href = a["href"] if a else None
            if href:
                # Relative URLs — resolve against the page URL (never string-glue)
                absolute = urljoin(page_url, href)
                book_urls.append(absolute)

        # Follow the 'next' button if present
        next_btn  = soup.select_one("li.next > a")
        page_url  = urljoin(page_url, next_btn["href"]) if next_btn else None

    # Deduplicate while preserving order
    seen       = set()
    unique     = []
    for u in book_urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    print(f"\ncatalogue_pages={pages_seen}  discovered={len(book_urls)}  unique_urls={len(unique)}")
    return unique


# ── Stage 3: Detail page extractor ───────────────────────────────────────────

def extract_raw(url: str, source_page: str) -> Optional[dict]:
    """
    Download a book detail page and return a raw record dict with 8 fields.
    Returns None if the page cannot be fetched.
    """
    html = fetch(url)
    if not html:
        return None

    soup        = BeautifulSoup(html, "html.parser")
    product_div = soup.select_one("div.product_main")

    if not product_div:
        print(f"  PARSE FAIL (no product_main)  {url}")
        return None

    title             = product_div.select_one("h1")
    price_tag         = product_div.select_one("p.price_color")
    availability_tag  = product_div.select_one("p.availability")
    rating_tag        = product_div.select_one("p.star-rating")

    # Description is in the product description section — may be absent
    desc_header = soup.find("div", id="product_description")
    description = None
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True) or None

    return {
        "title":             title.get_text(strip=True) if title else "",
        "product_url":       url,
        "price_text":        price_tag.get_text(strip=True) if price_tag else "",
        "availability_text": availability_tag.get_text(strip=True) if availability_tag else "",
        "rating_text":       rating_tag["class"][1] if rating_tag and len(rating_tag.get("class", [])) > 1 else "",
        "description":       description,
        "source_page":       source_page,
        "fetched_at":        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


# ── Stage 4: Normalise & validate ────────────────────────────────────────────

def _parse_price(text: str) -> float:
    """Strip currency symbols and parse '£51.77' → 51.77."""
    cleaned = re.sub(r"[^\d.]", "", text)
    return float(cleaned) if cleaned else 0.0


def _parse_stock(text: str) -> bool:
    return "in stock" in text.lower()


def normalize_and_validate(raw: dict) -> tuple[Optional[BookRecord], Optional[str]]:
    """
    Turn a raw record into a validated BookRecord.
    Returns (record, None) on success, (None, reason) on failure.
    """
    try:
        record = BookRecord(
            title             = raw["title"],
            product_url       = raw["product_url"],
            price_text        = raw["price_text"],
            price_gbp         = _parse_price(raw["price_text"]),
            availability_text = raw["availability_text"],
            in_stock          = _parse_stock(raw["availability_text"]),
            rating_text       = raw["rating_text"],
            rating            = WORD_TO_INT.get(raw["rating_text"].lower(), 0),
            description       = raw["description"],
            source_page       = raw["source_page"],
            fetched_at        = raw["fetched_at"],
        )
        return record, None
    except (ValidationError, Exception) as exc:
        return None, str(exc)


# ── Stage 5: Error handling & run report ─────────────────────────────────────

def load_existing_books() -> dict[str, dict]:
    """Load existing books.json → dict keyed by product_url (idempotency)."""
    if BOOKS_FILE.exists():
        try:
            records = json.loads(BOOKS_FILE.read_text(encoding="utf-8"))
            return {r["product_url"]: r for r in records}
        except Exception:
            pass
    return {}


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run():
    _stats["start_time"] = datetime.now(timezone.utc)

    print("=" * 60)
    print("The Polite Scraper — FlyRank W5 A9")
    print(f"Target: {START_URL}")
    print("=" * 60)

    # Stage 2 — discover
    print("\n[Stage 2] Discovering catalogue pages...")
    book_urls = discover_book_urls()

    # Load existing records for idempotency
    existing = load_existing_books()

    good_records: list[dict] = []
    error_records: list[dict] = []

    # Stage 3 + 4 + 5 — fetch, extract, validate, survive failures
    print(f"\n[Stage 3-4] Scraping {len(book_urls)} book pages...")
    for i, url in enumerate(book_urls, 1):
        # Identify which catalogue page this came from (approximate by position)
        page_num   = (i - 1) // 20 + 1
        source_pg  = f"https://books.toscrape.com/catalogue/page-{page_num}.html"

        print(f"\n[{i:02}/{len(book_urls)}]", end="")

        # Stage 5: each page is independent — failures don't stop the run
        try:
            raw = extract_raw(url, source_pg)
            if raw is None:
                error_records.append({"url": url, "reason": "fetch or parse failed"})
                continue

            record, reason = normalize_and_validate(raw)
            if record is None:
                error_records.append({"url": url, "reason": reason, "raw": raw})
                continue

            good_records.append(record.model_dump())

        except Exception as exc:
            error_records.append({"url": url, "reason": f"unexpected: {exc}"})

    # Merge with existing for idempotency (same URL = overwrite, not duplicate)
    merged = {**existing, **{r["product_url"]: r for r in good_records}}
    final_records = list(merged.values())

    # Write outputs
    BOOKS_FILE.write_text(
        json.dumps(final_records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ERRORS_FILE.write_text(
        json.dumps(error_records, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Run report
    duration = (datetime.now(timezone.utc) - _stats["start_time"]).total_seconds()
    report = {
        "start_time":     _stats["start_time"].isoformat().replace("+00:00", "Z"),
        "duration_sec":   round(duration, 2),
        "catalogue_pages": MAX_PAGES,
        "urls_discovered": len(book_urls),
        "pages_fetched":  _stats["fetched"],
        "cache_hits":     _stats["cache_hits"],
        "valid_records":  len(final_records),
        "invalid_records": len(error_records),
        "failed_pages":   _stats["failed"],
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Summary
    print("\n" + "=" * 60)
    print("RUN COMPLETE")
    print(f"  valid records : {report['valid_records']}")
    print(f"  invalid       : {report['invalid_records']}")
    print(f"  failed pages  : {report['failed_pages']}")
    print(f"  fetched       : {report['pages_fetched']}")
    print(f"  cache hits    : {report['cache_hits']}")
    print(f"  duration      : {report['duration_sec']}s")
    print(f"  output        : {BOOKS_FILE}")
    print(f"  report        : {REPORT_FILE}")
    print("=" * 60)

    # Sample record
    if final_records:
        print("\nSample record:")
        print(json.dumps(final_records[0], indent=2, ensure_ascii=False))

    return report


if __name__ == "__main__":
    run()
