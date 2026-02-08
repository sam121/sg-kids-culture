from __future__ import annotations

from collections import deque
from bs4 import BeautifulSoup

from .common import Event, extract_jsonld_events, normalize_space, parse_date, parse_age_range
from .http import get

BASE = "https://www.esplanade.com"
LISTING = f"{BASE}/whats-on"


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
        for child in _collect_whats_on_links(page, limit=max_events):
            if child not in visited and child not in queue:
                queue.append(child)
        jsonld = extract_jsonld_events(page, "esplanade", page_url=url)
        events.extend(jsonld)
        if not jsonld:
            # Fallback: minimal extraction from page header
            soup_ev = BeautifulSoup(page, "lxml")
            title_el = soup_ev.find("h1")
            date_el = soup_ev.find(string=lambda s: s and "202" in s)
            start = parse_date(date_el) if date_el else None
            age_min, age_max = parse_age_range(page)
            events.append(Event(
                title=normalize_space(title_el.get_text()) if title_el else "(Esplanade event)",
                url=url,
                source="esplanade",
                start=start,
                age_min=age_min,
                age_max=age_max,
                raw_date=normalize_space(date_el) if date_el else None,
            ))
    return events
