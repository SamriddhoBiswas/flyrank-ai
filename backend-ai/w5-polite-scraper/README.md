# The Polite Scraper 📚

A small, well-behaved web scraping pipeline that downloads the first **3 catalogue pages** of [Books to Scrape](https://books.toscrape.com), visits all **60 book detail pages**, turns messy HTML into clean validated JSON — politely, without crashing on a broken page, and with an honest run report at the end.

---

## Quick start

```bash
pip install -r requirements.txt
python src/main.py
```

Output files appear in `output/`:

| File | Contents |
|---|---|
| `output/books.json` | 60 validated, normalized book records |
| `output/errors.json` | Any records that failed validation (with reason) |
| `output/run-report.json` | Counts, timings, cache hits, failures |

---

## Target classification

| Field | Value |
|---|---|
| **Site** | [Books to Scrape](https://books.toscrape.com) |
| **Why this site** | A public **sandbox** built explicitly for scraping practice — `toscrape.com` says: *"A books website created to help people learn web scraping"* |
| **Scope** | First **3 catalogue pages only** → 60 book pages |
| **Data collected** | Title, price, availability, star rating, description, URL, source page, fetch timestamp |
| **robots.txt** | `https://books.toscrape.com/robots.txt` — file exists, no disallow rules; all paths are permitted |
| **Appropriate?** | Yes — this is exactly what the sandbox was made for |

> **I will not reuse this code on another site without checking its rules and terms first.**

---

## Record schema

Each validated record in `books.json` has these fields:

| Field | Type | Notes |
|---|---|---|
| `title` | `str` | Book title |
| `product_url` | `str` | Canonical `https://` URL — the record's unique identity |
| `price_text` | `str` | Raw value, e.g. `"£51.77"` |
| `price_gbp` | `float` | Normalized number, e.g. `51.77` |
| `availability_text` | `str` | Raw availability string |
| `in_stock` | `bool` | `true` / `false` |
| `rating_text` | `str` | Word rating, e.g. `"Three"` |
| `rating` | `int` | Numeric 1–5 |
| `description` | `str \| null` | Book description — `null` when absent, never invented |
| `source_page` | `str` | Which catalogue page this book was found on |
| `fetched_at` | `str` | ISO-8601 UTC timestamp |

---

## Politeness rules

| Rule | Implementation |
|---|---|
| **User-agent** | `FlyRankInternship-A9/1.0 (+https://github.com/prime-programmer-ar/flyrank-w5-polite-scraper)` |
| **Delay** | ≥ 600 ms between every real HTTP request |
| **Timeout** | 10 s per request — never waits forever |
| **Cache** | HTML saved to `cache/` on first fetch; all subsequent runs read from disk |
| **No retry on 403/404** | Asking again is how a polite robot becomes a pest |
| **One retry on 5xx/timeout** | Wait 2 s, try once more |

---

## Sample `run-report.json`

```json
{
  "start_time": "2026-08-12T07:40:28Z",
  "duration_sec": 55.15,
  "catalogue_pages": 3,
  "urls_discovered": 60,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

*(On a second run, `pages_fetched` drops to 0 and `cache_hits` rises to 63 — the site is never hit again.)*

---

## Why no browser was needed

The data — titles, prices, ratings, descriptions — is present in the **static HTML** the server sends directly. A headless browser would add 10–20× more memory and time to fetch the same bytes that a plain HTTP request already delivers. Books to Scrape has no JavaScript-rendered content, so `requests` + `BeautifulSoup` is both sufficient and correct.

---

## Ethics note

> Use an official API when one exists. Never bypass logins, paywalls, or blocks. Collect only what you need. Identify yourself honestly with a real user-agent. This scraper touches only a sandbox that was built for this purpose.

---

## Project structure

```
.
├── src/
│   └── main.py          # Full pipeline: fetch → extract → normalize → validate → store → report
├── output/
│   ├── books.json        # 60 validated records
│   ├── errors.json       # Failed records with reasons
│   └── run-report.json   # Run statistics
├── cache/               # HTML cache (git-ignored)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Limitation

The scraper is single-threaded and sequential. Scraping 60 pages with a 600 ms polite delay takes ~40–60 seconds on first run (0 seconds on subsequent runs from cache). A concurrent version with a rate limiter would be significantly faster but adds complexity beyond this assignment's scope.
