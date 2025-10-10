"""fastMCP server that collects daily pickpocket risk reports."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from xml.etree import ElementTree

from email.utils import parsedate_to_datetime

import httpx
from fastmcp import FastMCP

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOGGER = logging.getLogger("pickpocket-risk-collector.server")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

GOOGLE_NEWS_RSS_ENDPOINT = "https://news.google.com/rss/search"
BASE_PICKPOCKET_QUERY = '"pickpocket" OR "pick pocket" OR "bag snatching"'
DEFAULT_MAX_RESULTS = 15
MAX_RESULTS_LIMIT = 25

app = FastMCP(name="pickpocket-risk-collector", stateless_http=True)


def _write_daily_entry(entry: dict) -> Path:
    """Append a JSON line entry to the current day's log file."""
    filename = f"{entry['timestamp'][:10]}.jsonl"
    path = DATA_DIR / filename
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry, ensure_ascii=False))
        fp.write("\n")
    return path


def _normalize_query(user_query: str | None) -> str:
    """Combine the base pickpocket query with an optional user-supplied filter."""
    if not user_query:
        return BASE_PICKPOCKET_QUERY
    cleaned = user_query.strip()
    if not cleaned:
        return BASE_PICKPOCKET_QUERY
    return f"({BASE_PICKPOCKET_QUERY}) AND ({cleaned})"


def _guess_locations(*texts: str) -> list[str]:
    """Extract potential location names from text using simple heuristics."""
    location_patterns = [
        re.compile(r"in ([A-Z][A-Za-z]+(?:[\s-][A-Z][A-Za-z]+)*)"),
        re.compile(r"at ([A-Z][A-Za-z]+(?:[\s-][A-Z][A-Za-z]+)*)"),
    ]
    candidates: list[str] = []
    for text in texts:
        if not text:
            continue
        for pattern in location_patterns:
            for match in pattern.findall(text):
                normalized = match.strip()
                if normalized and normalized not in candidates:
                    candidates.append(normalized)
        # Many news headlines use "City: ..." format.
        if ":" in text:
            leading = text.split(":", 1)[0].strip()
            if leading and leading == leading.title() and leading not in candidates:
                candidates.append(leading)
    return candidates


def _parse_pub_date(pub_date: str | None) -> str | None:
    if not pub_date:
        return None
    try:
        dt = parsedate_to_datetime(pub_date)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _extract_text(element: ElementTree.Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def _parse_feed_items(feed_xml: str, limit: int) -> list[dict]:
    try:
        root = ElementTree.fromstring(feed_xml)
    except ElementTree.ParseError as exc:
        raise ValueError(f"Failed to parse feed XML: {exc}") from exc

    items: Iterable[ElementTree.Element] = root.findall(".//item")
    reports: list[dict] = []
    for item in items:
        title = _extract_text(item.find("title"))
        link = _extract_text(item.find("link"))
        description = _extract_text(item.find("description"))
        pub_date = _parse_pub_date(_extract_text(item.find("pubDate")))

        source_element = item.find("{http://news.google.com/}source")
        if source_element is None:
            source_element = item.find("source")
        source_name = _extract_text(source_element)

        report: dict[str, object | None] = {
            "headline": title or None,
            "summary": description or None,
            "link": link or None,
            "published_at": pub_date,
            "source": source_name or None,
        }
        guessed_locations = _guess_locations(title, description)
        if guessed_locations:
            report["guessed_locations"] = guessed_locations

        reports.append(report)
        if len(reports) >= limit:
            break
    return reports


@app.tool(
    name="collect_pickpocket_reports",
    description="Search recent news for pickpocket incidents and persist the results.",
)
async def collect_pickpocket_reports(
    query: str | None = None,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> dict:
    """Collect pickpocket-related news articles and persist a summary snapshot."""
    LOGGER.info(
        "Received collect_pickpocket_reports request query=%r max_results=%d",
        query,
        max_results,
    )
    if max_results < 1 or max_results > MAX_RESULTS_LIMIT:
        LOGGER.warning(
            "Rejecting request due to invalid max_results=%d (limit=%d)",
            max_results,
            MAX_RESULTS_LIMIT,
        )
        return {
            "error": f"`max_results` must be between 1 and {MAX_RESULTS_LIMIT}.",
            "details": {"max_results": max_results},
        }

    timestamp = datetime.now(tz=timezone.utc)
    normalized_query = _normalize_query(query)
    params = {
        "q": normalized_query,
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    }
    feed_url = f"{GOOGLE_NEWS_RSS_ENDPOINT}?{urlencode(params)}"
    LOGGER.info("Fetching pickpocket feed url=%s", feed_url)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(feed_url)
            response.raise_for_status()
            reports = _parse_feed_items(response.text, max_results)
    except httpx.HTTPError as exc:
        LOGGER.error("HTTP error fetching feed: %s", exc)
        return {
            "error": "Failed to fetch pickpocket reports feed.",
            "details": str(exc),
            "source": feed_url,
        }
    except ValueError as exc:
        LOGGER.error("Parsing error processing feed: %s", exc)
        return {
            "error": "Failed to process pickpocket reports feed.",
            "details": str(exc),
            "source": feed_url,
        }

    entry = {
        "timestamp": timestamp.isoformat(),
        "query": normalized_query,
        "requested_query": query,
        "feed_url": feed_url,
        "report_count": len(reports),
        "reports": reports,
    }
    path = _write_daily_entry(entry)
    LOGGER.info(
        "Persisted %d reports to %s for query=%r",
        len(reports),
        path,
        normalized_query,
    )
    message = "Snapshot persisted to daily log."
    if not reports:
        LOGGER.info("No reports found for query=%r", normalized_query)
        message = "Snapshot persisted but no reports were found for the query."
    return {
        "entry": entry,
        "file_path": str(path),
        "message": message,
    }


if __name__ == "__main__":
    app.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/",
        log_level="debug",
    )
