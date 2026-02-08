import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Optional

import dateutil.parser
import pytz
from bs4 import BeautifulSoup

SG_TZ = pytz.timezone("Asia/Singapore")

BLOCKED_TITLE_TERMS = {
    "exhibitions",
    "programmes",
    "plan your itinerary",
    "admissions",
    "museum map",
    "accessibility at the museum",
    "for groups",
    "shop & dine",
    "online exhibitions",
    "about us",
    "view all",
}

BLOCKED_URL_TERMS = [
    "/plan-your-visit/",
    "/about-us/",
    "/shop-and-dine/",
    "/virtual-gallery/",
    "/visitor-information/",
    "/museum-map",
    "/view-all",
]

@dataclass
class Event:
    title: str
    url: str
    source: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    venue: Optional[str] = None
    price: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    categories: Optional[List[str]] = None
    image: Optional[str] = None
    raw_date: Optional[str] = None

    def to_dict(self):
        data = asdict(self)
        if self.start:
            data["start"] = self.start.astimezone(SG_TZ).isoformat()
        if self.end:
            data["end"] = self.end.astimezone(SG_TZ).isoformat()
        return data

def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text: str) -> Optional[datetime]:
    if not text:
        return None
    try:
        dt = dateutil.parser.parse(text, dayfirst=False, fuzzy=True)
        if dt.tzinfo is None:
            dt = SG_TZ.localize(dt)
        else:
            dt = dt.astimezone(SG_TZ)
        now = datetime.now(tz=SG_TZ)
        if dt.year < now.year - 1 or dt.year > now.year + 3:
            return None
        return dt
    except (ValueError, OverflowError):
        return None


def parse_age_range(text: str) -> tuple[Optional[int], Optional[int]]:
    if not text:
        return None, None
    patterns = [
        r"ages?\s*(\d{1,2})\s*[–-]\s*(\d{1,2})",
        r"(\d{1,2})\s*to\s*(\d{1,2})\s*years",
        r"(\d{1,2})\+",
        r"for\s*children\s*aged?\s*(\d{1,2})\s*and\s*above",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            if len(m.groups()) == 2:
                lo, hi = int(m.group(1)), int(m.group(2))
                if lo > 17:
                    return None, None
                return lo, min(hi, 17)
            if len(m.groups()) == 1:
                lo = int(m.group(1))
                if lo > 17:
                    return None, None
                return lo, None
    return None, None


def age_bucket(age_min: Optional[int], age_max: Optional[int]) -> str:
    if age_max is not None:
        if age_max <= 5:
            return "0-5"
        if age_max <= 12:
            return "6-12"
    if age_min is None:
        return "all"
    if age_min <= 5:
        return "0-5"
    if age_min <= 12:
        return "6-12"
    if age_min <= 17:
        return "13-17"
    return "all"


def is_probable_event(event: Event) -> bool:
    title = normalize_space(event.title).lower()
    if not title:
        return False
    if title in BLOCKED_TITLE_TERMS:
        return False
    url = (event.url or "").strip()
    if not url.startswith("http"):
        return False
    path = urlparse(url).path.lower()
    if any(term in path for term in BLOCKED_URL_TERMS):
        return False
    # Keep to known event-like paths for this first pass.
    if "/whats-on/" not in path and "/events/" not in path and "/concert" not in path:
        return False
    # Must have at least one hint of timing or age relevance.
    if not event.start and event.age_min is None and event.age_max is None:
        return False
    return True


def extract_jsonld_events(html: str, source: str) -> List[Event]:
    soup = BeautifulSoup(html, "lxml")
    events: List[Event] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except json.JSONDecodeError:
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            if item.get("@type") not in ("Event", ["Event"], "MusicEvent", "TheaterEvent"):
                continue
            title = item.get("name") or "Untitled"
            url = item.get("url") or item.get("@id") or ""
            start = parse_date(item.get("startDate"))
            end = parse_date(item.get("endDate"))
            offers = item.get("offers") or {}
            price = None
            if isinstance(offers, dict):
                price = offers.get("priceCurrency", "") + " " + str(offers.get("price")) if offers.get("price") else offers.get("description")
            image = item.get("image")
            venue = None
            loc = item.get("location")
            if isinstance(loc, dict):
                venue = loc.get("name")
            age_min, age_max = parse_age_range(json.dumps(item))
            events.append(Event(
                title=normalize_space(title),
                url=url,
                source=source,
                start=start,
                end=end,
                venue=venue,
                price=price,
                age_min=age_min,
                age_max=age_max,
                image=image,
            ))
    return events


def dedupe(events: List[Event]) -> List[Event]:
    seen = set()
    unique = []
    for ev in events:
        key = (ev.title.lower(), ev.start.isoformat() if ev.start else ev.url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(ev)
    return unique


def sort_events(events: List[Event]) -> List[Event]:
    fallback = datetime.now(tz=SG_TZ)
    return sorted(events, key=lambda e: e.start.astimezone(SG_TZ) if e.start else fallback)
