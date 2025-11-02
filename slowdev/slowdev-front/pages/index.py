import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import streamlit as st

MONTH_FORMAT = "%Y-%m"
DAY_FORMAT = "%Y-%m-%d"
UNKNOWN_MONTH_LABEL = "날짜 정보 없음"
FEEDBURNER_NS = "{http://rssnamespace.org/feedburner/ext/1.0}"

BAELDUNG_FEEDS = (
    ("Kotlin", "https://feeds.feedblitz.com/baeldung/kotlin"),
    ("Backend", "https://feeds.feedblitz.com/baeldung"),
    ("Ops", "https://feeds.feedblitz.com/baeldung/ops"),
    ("Computer Science", "https://feeds.feedblitz.com/baeldung/cs"),
)

DZONE_FEEDS = (
    ("Frameworks", "https://feeds.dzone.com/frameworks"),
    ("Java", "https://feeds.dzone.com/java"),
)


def _extract_date_fields(raw_date: str) -> tuple[str, str, float]:
    if not raw_date:
        return UNKNOWN_MONTH_LABEL, "", float("-inf")
    try:
        dt = parsedate_to_datetime(raw_date)
    except Exception:
        return UNKNOWN_MONTH_LABEL, raw_date, float("-inf")
    return dt.strftime(MONTH_FORMAT), dt.strftime(DAY_FORMAT), dt.timestamp()


def _format_tab_label(month_key: str) -> str:
    if month_key == UNKNOWN_MONTH_LABEL:
        return month_key
    parts = month_key.split("-")
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        year, month = parts
        return f"{year}년 {int(month):02d}월"
    return month_key


def _group_entries_by_month(entries: list[dict]) -> tuple[list[str], dict[str, list[dict]]]:
    month_order: list[str] = []
    month_groups: dict[str, list[dict]] = {}

    for entry in entries:
        month_key = entry.get("pub_month") or UNKNOWN_MONTH_LABEL
        if month_key not in month_groups:
            month_groups[month_key] = []
            month_order.append(month_key)
        month_groups[month_key].append(entry)

    return month_order, month_groups


@st.cache_data(ttl=3600)
def fetch_feed_group(feed_specs: tuple[tuple[str, str], ...], limit_per_feed: int = 5):
    aggregated: list[dict] = []
    errors: list[str] = []

    for label, rss_url in feed_specs:
        try:
            with urllib.request.urlopen(rss_url, timeout=10) as response:
                xml_bytes = response.read()
        except Exception as exc:
            errors.append(f"{label} RSS를 불러오지 못했습니다: {exc}")
            continue

        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as exc:
            errors.append(f"{label} RSS를 해석하는 중 문제가 발생했습니다: {exc}")
            continue

        channel = root.find("channel")
        if channel is None:
            errors.append(f"{label} RSS 형식이 예상과 다릅니다.")
            continue

        for item in channel.findall("item")[:limit_per_feed]:
            title = (item.findtext("title") or "").strip() or "(제목 없음)"
            link = (item.findtext(f"{FEEDBURNER_NS}origLink") or item.findtext("link") or "").strip()
            raw_date = (item.findtext("pubDate") or "").strip()

            pub_month, pub_day, sort_key = _extract_date_fields(raw_date)

            aggregated.append(
                {
                    "title": title,
                    "link": link,
                    "pub_date_raw": raw_date,
                    "pub_month": pub_month,
                    "pub_day": pub_day,
                    "sort_key": sort_key,
                    "source": label,
                }
            )

    aggregated.sort(key=lambda item: item["sort_key"], reverse=True)
    return {"items": aggregated, "errors": errors}


def _render_feed_section(title: str, feed_specs: tuple[tuple[str, str], ...], limit_per_feed: int = 5):
    st.header(title)
    feed_data = fetch_feed_group(feed_specs, limit_per_feed=limit_per_feed)

    for warning in feed_data["errors"]:
        st.warning(warning)

    if not feed_data["items"]:
        st.info("표시할 기사가 없습니다.")
        return

    month_order, month_groups = _group_entries_by_month(feed_data["items"])
    tab_labels = [_format_tab_label(month) for month in month_order]
    tabs = st.tabs(tab_labels)

    for tab, month_key in zip(tabs, month_order):
        with tab:
            for entry in month_groups.get(month_key, []):
                day_label = f"{entry['pub_day']} · " if entry.get("pub_day") else ""
                source_label = f" · {entry['source']}" if entry.get("source") else ""
                st.markdown(f"- {day_label}[{entry['title']}]({entry['link']}){source_label}")


_render_feed_section("📚 Baeldung 최신 글", BAELDUNG_FEEDS, limit_per_feed=5)
st.divider()
_render_feed_section("📰 DZone 최신 글", DZONE_FEEDS, limit_per_feed=5)
