from __future__ import annotations

from collections import deque
import json
import re
from bs4 import BeautifulSoup

from .common import (
    Event,
    extract_jsonld_events,
    infer_categories,
    normalize_space,
    parse_age_ranges,
    parse_date,
    summarize_age_ranges,
)
from .http import get

BASE = "https://www.esplanade.com"
LISTING = f"{BASE}/whats-on"
LISTING_API = f"{BASE}/sitecore/api/website/event/listing/view-by-event"
PRIORITY_PAGES = [
    f"{BASE}/whats-on/festivals-and-series/series/playtime",
]


def _collect_whats_on_links(html: str, limit: int = 50) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/whats-on/" not in href:
            continue
        if href.startswith("/"):
            href = BASE + href
        if not href.startswith(BASE):
            continue
        if href not in links:
            links.append(href)
        if len(links) >= limit:
            break
    return links


def _extract_listing_config(html: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    section = soup.find("section", id="event-listing-info-cards")
    if not section:
        return None
    x_data = section.get("x-data") or ""
    parent_match = re.search(r"parentId:\s*'([a-f0-9]+)'", x_data, flags=re.IGNORECASE)
    datasource_match = re.search(r"datasourceId:\s*'([a-f0-9]+)'", x_data, flags=re.IGNORECASE)
    if not parent_match or not datasource_match:
        return None
    lang_match = re.search(r"params:\s*\{[^}]*languages:\s*'([^']+)'", x_data, flags=re.IGNORECASE)
    page_size_match = re.search(r"params:\s*\{[^}]*pageSize:\s*(\d+)", x_data, flags=re.IGNORECASE)
    return {
        "languages": (lang_match.group(1) if lang_match else "en"),
        "page_size": int(page_size_match.group(1)) if page_size_match else 20,
        "parent_id": parent_match.group(1),
        "datasource_id": datasource_match.group(1),
    }


def _fetch_listing_component_events(html: str) -> tuple[list[Event], list[str]]:
    cfg = _extract_listing_config(html)
    if not cfg:
        return [], []
    payload = get(
        LISTING_API,
        params={
            "languages": cfg["languages"],
            "pageSize": cfg["page_size"],
            "pageNumber": 1,
            "parentId": cfg["parent_id"],
            "datasourceId": cfg["datasource_id"],
            "eventType": "ongoing",
        },
    )
    if not payload:
        return [], []
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return [], []
    out_events: list[Event] = []
    out_links: list[str] = []
    for item in data.get("Listings") or []:
        page_data = item.get("PageData") or {}
        rel_url = page_data.get("Url") or item.get("Url") or item.get("Link")
        if not rel_url:
            continue
        event_url = BASE + rel_url if rel_url.startswith("/") else rel_url
        title = normalize_space(page_data.get("Title") or item.get("Title") or "")
        if not title:
            continue
        age_ranges = parse_age_ranges(page_data.get("Description") or "")
        age_min, age_max = summarize_age_ranges(age_ranges)
        categories = infer_categories(
            title=title,
            url=event_url,
            source="esplanade",
            text_blob=" ".join(
                [
                    page_data.get("Description") or "",
                    item.get("CategoryName") or "",
                    item.get("Tag") or "",
                ]
            ),
        )
        out_events.append(
            Event(
                title=title,
                url=event_url,
                source="esplanade",
                start=parse_date(item.get("PerformanceStartDate")),
                end=parse_date(item.get("PerformanceEndDate")),
                venue=item.get("VenueName"),
                price=item.get("PriceRange"),
                age_min=age_min,
                age_max=age_max,
                age_ranges=age_ranges or None,
                categories=categories or None,
            )
        )
        out_links.append(event_url)
    return out_events, out_links


def fetch(max_events: int = 40) -> list[Event]:
    html = get(LISTING, params={"type": "Family & Children"})
    if not html:
        return []
    events: list[Event] = []
    seed_links = PRIORITY_PAGES + _collect_whats_on_links(html, limit=max_events)
    queue = deque()
    for link in seed_links:
        if link not in queue:
            queue.append(link)
    visited: set[str] = set()
    max_pages = max(max_events + 40, 80)

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        page = get(url)
        if not page:
            continue
        listing_events, listing_links = _fetch_listing_component_events(page)
        events.extend(listing_events)
        # Prioritize component-listed event links so details (age/date) are crawled before cap.
        for child in listing_links:
            if child not in visited and child not in queue:
                queue.appendleft(child)
        for child in _collect_whats_on_links(page, limit=12):
            if child not in visited and child not in queue:
                queue.append(child)
        jsonld = extract_jsonld_events(
            page,
            "esplanade",
            page_url=url,
            fallback_age_text=page,
        )
        events.extend(jsonld)
        if not jsonld:
            # Fallback: minimal extraction from page header
            soup_ev = BeautifulSoup(page, "lxml")
            title_el = soup_ev.find("h1")
            date_pattern = re.compile(
                r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b|(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*(?:/|,|\s+\d)",
                flags=re.IGNORECASE,
            )
            date_text = None
            for tag in soup_ev.find_all(["time", "p", "div", "span", "li", "h3", "h4"]):
                text = normalize_space(tag.get_text(" ", strip=True))
                if not text or len(text) > 140:
                    continue
                low = text.lower()
                if "window.datalayer" in low or "copyright" in low or "last updated" in low:
                    continue
                if date_pattern.search(text):
                    date_text = text
                    break
            page_category = ""
            page_category_meta = soup_ev.find("meta", attrs={"name": "pageCategory"})
            if page_category_meta:
                page_category = page_category_meta.get("content") or ""
            start = parse_date(date_text) if date_text else None
            age_ranges = parse_age_ranges(page)
            age_min, age_max = summarize_age_ranges(age_ranges)
            title = normalize_space(title_el.get_text()) if title_el else "(Esplanade event)"
            events.append(Event(
                title=title,
                url=url,
                source="esplanade",
                start=start,
                age_min=age_min,
                age_max=age_max,
                age_ranges=age_ranges or None,
                categories=infer_categories(
                    title=title,
                    url=url,
                    source="esplanade",
                    text_blob=page_category,
                ) or None,
                raw_date=date_text,
            ))
    return events
