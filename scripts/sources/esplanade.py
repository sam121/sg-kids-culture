from __future__ import annotations

from collections import deque
import json
import re
from bs4 import BeautifulSoup

from .common import (
    Event,
    extract_jsonld_events,
    normalize_space,
    parse_age_ranges,
    parse_date,
    summarize_age_ranges,
)
from .http import get

BASE = "https://www.esplanade.com"
LISTING = f"{BASE}/whats-on"
LISTING_API = f"{BASE}/sitecore/api/website/event/listing/view-by-event"


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
            )
        )
        out_links.append(event_url)
    return out_events, out_links


def fetch(max_events: int = 40) -> list[Event]:
    html = get(LISTING, params={"type": "Family & Children"})
    if not html:
        return []
    events: list[Event] = []
    queue = deque(_collect_whats_on_links(html, limit=max_events))
    visited: set[str] = set()

    while queue and len(visited) < max_events:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        page = get(url)
        if not page:
            continue
        listing_events, listing_links = _fetch_listing_component_events(page)
        events.extend(listing_events)
        child_links = _collect_whats_on_links(page, limit=max_events) + listing_links
        for child in child_links:
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
            date_el = soup_ev.find(string=lambda s: s and "202" in s)
            start = parse_date(date_el) if date_el else None
            age_ranges = parse_age_ranges(page)
            age_min, age_max = summarize_age_ranges(age_ranges)
            events.append(Event(
                title=normalize_space(title_el.get_text()) if title_el else "(Esplanade event)",
                url=url,
                source="esplanade",
                start=start,
                age_min=age_min,
                age_max=age_max,
                age_ranges=age_ranges or None,
                raw_date=normalize_space(date_el) if date_el else None,
            ))
    return events
