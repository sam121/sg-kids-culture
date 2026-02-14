from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

import pytz

SG_TZ = pytz.timezone("Asia/Singapore")
SITE_TITLE = "Singapore Social Events Weekly"
SITE_DESC = "Social and cultural events in Singapore across theatre, music, dance, museums, and more."
BASE_URL = "https://sam121.github.io/sg-kids-culture/"
SOURCE_LABELS = {
    "esplanade": "Esplanade",
    "sso": "SSO",
    "sco": "SCO",
    "artshouse": "Arts House Group",
    "gallery": "National Gallery",
    "nhb": "NHB Museums",
    "sam": "Singapore Art Museum",
    "artscience": "ArtScience Museum",
    "sandstheatre": "Sands Theatre",
    "peranakan": "Peranakan Museum",
    "ihc": "Indian Heritage Centre",
    "childrensmuseum": "Children's Museum Singapore",
    "changi": "Changi Chapel & Museum",
    "bukitchandu": "Reflections at Bukit Chandu",
    "sccc": "Singapore Chinese Cultural Centre",
    "gateway": "Gateway Theatre",
}

SCRAPED_PLACE_ORDER = [
    "esplanade",
    "sso",
    "sco",
    "artshouse",
    "gallery",
    "nhb",
    "sam",
    "artscience",
    "sandstheatre",
    "peranakan",
    "ihc",
    "childrensmuseum",
    "bukitchandu",
    "sccc",
    "gateway",
    "changi",
]


HTML_TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>__SITE_TITLE__</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap\" rel=\"stylesheet\" />
  <style>
    :root {
      --bg: #0b1021;
      --card: rgba(255,255,255,0.06);
      --accent: #35d7a7;
      --text: #f6f7fb;
      --muted: #b4b7c5;
      --pill: rgba(53,215,167,0.12);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; background: radial-gradient(120% 120% at 20% 20%, #10203e 0%, #0b1021 45%, #0b0f1c 100%); color: var(--text); }
    .shell { max-width: 1080px; margin: 0 auto; padding: 48px 20px 72px; }
    header { display: flex; justify-content: space-between; gap: 16px; align-items: center; flex-wrap: wrap; }
    h1 { margin: 0; font-size: 32px; letter-spacing: -0.5px; }
    .muted { color: var(--muted); font-size: 15px; line-height: 1.6; }
    .intro { margin-top: 4px; font-size: 14px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 28px; }
    .card { background: var(--card); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 16px 16px 18px; backdrop-filter: blur(4px); display: flex; flex-direction: column; gap: 10px; }
    .title { font-weight: 700; font-size: 18px; margin: 0; color: #fff; }
    .meta { display: flex; flex-direction: column; gap: 6px; }
    .pill-row { display: flex; gap: 8px; flex-wrap: wrap; }
    .pill { background: var(--pill); color: var(--accent); padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .filters { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
    .filter-groups { display: grid; grid-template-columns: 1fr; gap: 8px; margin-top: 10px; }
    .filter-group .muted { font-size: 13px; }
    .month-select { border: 1px solid rgba(255,255,255,0.2); background: transparent; color: #fff; padding: 8px 12px; border-radius: 10px; font-weight: 600; }
    .month-select option { color: #111827; }
    .filter-btn { border: 1px solid rgba(255,255,255,0.2); background: transparent; color: #fff; padding: 8px 12px; border-radius: 10px; cursor: pointer; font-weight: 600; }
    .filter-btn.active { background: var(--accent); color: #0b1021; border-color: var(--accent); }
    .count { margin-top: 8px; }
    .signup { margin-top: 22px; padding: 16px; border: 1px dashed rgba(255,255,255,0.2); border-radius: 12px; }
    footer { margin-top: 32px; color: var(--muted); font-size: 13px; }
  </style>
</head>
<body>
  <div class=\"shell\">
    <header>
      <div>
        <h1>__SITE_TITLE__</h1>
        <div class=\"muted\">Weekly social and cultural picks for all ages. Updated Mondays 9:00 AM SGT.</div>
        <div class=\"muted intro\">Tracking: __SCRAPED_PLACES__.</div>
        <div class=\"muted intro\">This run includes events from: __SOURCE_SUMMARY__.</div>
      </div>
      <div class=\"muted\"><a href=\"rss.xml\">RSS</a></div>
    </header>

    <div class=\"filter-groups\">
      <div class=\"filter-group\">
        <div class=\"muted\">Age</div>
        <div class=\"filters\" id=\"age-filters\">
          <button class=\"filter-btn active\" data-age=\"all\">All ages</button>
          <button class=\"filter-btn\" data-age=\"0-5\">0-5</button>
          <button class=\"filter-btn\" data-age=\"6-12\">6-12</button>
          <button class=\"filter-btn\" data-age=\"13-17\">13-17</button>
        </div>
      </div>
      <div class=\"filter-group\">
        <div class=\"muted\">Category</div>
        <div class=\"filters\" id=\"category-filters\">
          <button class=\"filter-btn active\" data-category=\"all\">All categories</button>
          <button class=\"filter-btn\" data-category=\"Theatre\">Theatre</button>
          <button class=\"filter-btn\" data-category=\"Opera\">Opera</button>
          <button class=\"filter-btn\" data-category=\"Orchestra\">Orchestra</button>
          <button class=\"filter-btn\" data-category=\"Cinema\">Cinema</button>
          <button class=\"filter-btn\" data-category=\"Dance\">Dance</button>
          <button class=\"filter-btn\" data-category=\"Music\">Music</button>
          <button class=\"filter-btn\" data-category=\"Workshop\">Workshop</button>
          <button class=\"filter-btn\" data-category=\"Exhibition\">Exhibition</button>
        </div>
      </div>
      <div class=\"filter-group\">
        <div class=\"muted\">Month</div>
        <div class=\"filters\" id=\"month-filters\">
          <select id=\"month-select\" class=\"month-select\"></select>
          <button class=\"filter-btn\" id=\"month-this\">This month</button>
        </div>
      </div>
      <div class=\"filter-group\">
        <div class=\"muted\">Location</div>
        <div class=\"filters\" id=\"location-filters\">
          <select id=\"location-select\" class=\"month-select\"></select>
        </div>
      </div>
    </div>
    <div id=\"result-count\" class=\"muted count\"></div>

    <div class=\"signup\">
      <div class=\"muted\" style=\"margin-bottom:8px;\">Get this list by email (Kit):</div>
      <div id=\"kit-embed\">Paste your Kit embed script here once you have the form ID.</div>
    </div>

    <div id=\"grid\" class=\"grid\"></div>

    <footer>
      <div>Generated automatically. Sources: __SOURCE_SUMMARY__.</div>
    </footer>
  </div>
  <script>
    const events = __EVENTS_JSON__;
    const sourceLabels = __SOURCE_LABELS_JSON__;
    const grid = document.getElementById('grid');

    function eventRanges(ev) {
      const ranges = [];
      if (Array.isArray(ev.age_ranges) && ev.age_ranges.length > 0) {
        ev.age_ranges.forEach(r => {
          if (!Array.isArray(r) || r.length < 2) return;
          const lo = r[0] === null || r[0] === undefined ? null : Number(r[0]);
          const hi = r[1] === null || r[1] === undefined ? null : Number(r[1]);
          ranges.push([Number.isNaN(lo) ? null : lo, Number.isNaN(hi) ? null : hi]);
        });
      } else if (ev.age_min !== null || ev.age_max !== null) {
        ranges.push([ev.age_min ?? null, ev.age_max ?? null]);
      }
      return ranges;
    }

    function eventCategories(ev) {
      if (!Array.isArray(ev.categories)) return [];
      return ev.categories.filter(Boolean);
    }

    function sourceLabel(source) {
      return sourceLabels[source] || source || 'Unknown source';
    }

    function eventLocation(ev) {
      if (typeof ev.venue === 'string' && ev.venue.trim()) return ev.venue.trim();
      return sourceLabel(ev.source);
    }

    function parseDateSafe(iso) {
      if (!iso) return null;
      const d = new Date(iso);
      return Number.isNaN(d.getTime()) ? null : d;
    }

    function monthPartsFromDate(date) {
      const parts = new Intl.DateTimeFormat('en-SG', {
        timeZone: 'Asia/Singapore',
        year: 'numeric',
        month: '2-digit',
      }).formatToParts(date);
      const year = parts.find(p => p.type === 'year')?.value;
      const month = parts.find(p => p.type === 'month')?.value;
      return { year, month };
    }

    function monthKeyFromDate(date) {
      const { year, month } = monthPartsFromDate(date);
      if (!year || !month) return null;
      return `${year}-${month}`;
    }

    function monthLabel(key) {
      const [yy, mm] = key.split('-').map(Number);
      if (!yy || !mm) return key;
      const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return `${names[mm - 1]} ${yy}`;
    }

    function nextMonthKey(key) {
      const [yy, mm] = key.split('-').map(Number);
      if (!yy || !mm) return key;
      const month = mm === 12 ? 1 : mm + 1;
      const year = mm === 12 ? yy + 1 : yy;
      return `${year}-${String(month).padStart(2, '0')}`;
    }

    function eventMonthSpan(ev) {
      const start = parseDateSafe(ev.start);
      const end = parseDateSafe(ev.end);
      if (!start && !end) return null;
      const startKey = monthKeyFromDate(start || end);
      const endKey = monthKeyFromDate(end || start);
      if (!startKey || !endKey) return null;
      return startKey <= endKey ? [startKey, endKey] : [endKey, startKey];
    }

    function allMonthKeys(events) {
      const set = new Set();
      events.forEach(ev => {
        const span = eventMonthSpan(ev);
        if (!span) return;
        let key = span[0];
        while (key <= span[1]) {
          set.add(key);
          const nxt = nextMonthKey(key);
          if (nxt === key) break;
          key = nxt;
        }
      });
      return Array.from(set).sort();
    }

    function bucketOverlap(r, bucket) {
      const bounds = { '0-5': [0, 5], '6-12': [6, 12], '13-17': [13, 17] }[bucket];
      if (!bounds) return true;
      const [bLo, bHi] = bounds;
      const lo = r[0] === null || r[0] === undefined ? 0 : r[0];
      const hi = r[1] === null || r[1] === undefined ? 99 : r[1];
      return lo <= bHi && hi >= bLo;
    }

    function eventBuckets(ev) {
      const ranges = eventRanges(ev);
      if (ranges.length === 0) return [];
      const buckets = ['0-5', '6-12', '13-17'].filter(b => ranges.some(r => bucketOverlap(r, b)));
      return buckets;
    }

    function matchesFilter(ev, filterAge, filterCategory, filterMonth, filterLocation) {
      if (filterAge !== 'all' && !eventBuckets(ev).includes(filterAge)) return false;
      if (filterCategory !== 'all' && !eventCategories(ev).includes(filterCategory)) return false;
      if (filterMonth !== 'all') {
        const span = eventMonthSpan(ev);
        if (!span) return false;
        if (filterMonth < span[0] || filterMonth > span[1]) return false;
      }
      if (filterLocation !== 'all' && eventLocation(ev) !== filterLocation) return false;
      return true;
    }

    function bucketLabel(ev) {
      const buckets = eventBuckets(ev);
      if (buckets.length === 0) return 'age unknown';
      const order = ['0-5', '6-12', '13-17'];
      const bounds = { '0-5': [0, 5], '6-12': [6, 12], '13-17': [13, 17] };
      const sorted = buckets.slice().sort((a, b) => order.indexOf(a) - order.indexOf(b));
      const contiguous = sorted.every((b, idx) => idx === 0 || order.indexOf(sorted[idx - 1]) + 1 === order.indexOf(b));
      if (!contiguous) return sorted.join('/');
      const first = bounds[sorted[0]][0];
      const last = bounds[sorted[sorted.length - 1]][1];
      if (first === 0 && last === 17) return 'all ages';
      return `${first}-${last}`;
    }

    function sameDayInSingapore(left, right) {
      const l = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Singapore', year: 'numeric', month: '2-digit', day: '2-digit' }).format(left);
      const r = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Singapore', year: 'numeric', month: '2-digit', day: '2-digit' }).format(right);
      return l === r;
    }

    function isMidnightInSingapore(date) {
      const parts = new Intl.DateTimeFormat('en-SG', {
        timeZone: 'Asia/Singapore',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }).formatToParts(date);
      const hh = parts.find(p => p.type === 'hour')?.value;
      const mm = parts.find(p => p.type === 'minute')?.value;
      return hh === '00' && mm === '00';
    }

    function formatDateOnly(date) {
      return date.toLocaleDateString('en-SG', {
        timeZone: 'Asia/Singapore',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    }

    function formatDateTime(date) {
      return date.toLocaleString('en-SG', {
        timeZone: 'Asia/Singapore',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }

    function formatDateLabel(ev) {
      const start = parseDateSafe(ev.start);
      const end = parseDateSafe(ev.end);
      if (start && end) {
        if (sameDayInSingapore(start, end)) {
          return `On ${isMidnightInSingapore(start) ? formatDateOnly(start) : formatDateTime(start)}`;
        }
        const left = isMidnightInSingapore(start) ? formatDateOnly(start) : formatDateTime(start);
        const right = isMidnightInSingapore(end) ? formatDateOnly(end) : formatDateTime(end);
        return `Runs ${left} to ${right}`;
      }
      if (start) {
        return `From ${isMidnightInSingapore(start) ? formatDateOnly(start) : formatDateTime(start)}`;
      }
      if (typeof ev.raw_date === 'string' && ev.raw_date.trim()) {
        return `Dates: ${ev.raw_date.trim()}`;
      }
      return 'Date TBC';
    }

    function currentMonthKey() {
      return monthKeyFromDate(new Date());
    }

    function setupMonthFilter() {
      const select = document.getElementById('month-select');
      if (!select) return;
      const keys = allMonthKeys(events);
      const current = currentMonthKey();
      const upcomingKeys = current ? keys.filter(k => k >= current) : keys;
      const opts = [{ value: 'all', label: 'All upcoming' }];
      if (current) opts.push({ value: current, label: `This month (${monthLabel(current)})` });
      upcomingKeys.forEach(key => {
        if (!opts.some(o => o.value === key)) {
          opts.push({ value: key, label: monthLabel(key) });
        }
      });
      select.innerHTML = opts.map(o => `<option value=\"${o.value}\">${o.label}</option>`).join('');
      state.month = current && opts.some(o => o.value === current) ? current : 'all';
      select.value = state.month;
      select.addEventListener('change', () => {
        state.month = select.value;
        render(state.age, state.category, state.month);
      });

      const thisBtn = document.getElementById('month-this');
      if (thisBtn) {
        thisBtn.addEventListener('click', () => {
          const nowKey = currentMonthKey();
          if (nowKey && Array.from(select.options).some(o => o.value === nowKey)) {
            select.value = nowKey;
            state.month = nowKey;
            render(state.age, state.category, state.month);
          }
        });
      }
    }

    function setupLocationFilter() {
      const select = document.getElementById('location-select');
      if (!select) return;
      const locations = Array.from(new Set(events.map(eventLocation))).filter(Boolean).sort((a, b) => a.localeCompare(b));
      const opts = [{ value: 'all', label: 'All locations' }].concat(locations.map(loc => ({ value: loc, label: loc })));
      select.innerHTML = opts.map(o => `<option value=\"${o.value}\">${o.label}</option>`).join('');
      select.value = state.location;
      select.addEventListener('change', () => {
        state.location = select.value;
        render(state.age, state.category, state.month, state.location);
      });
    }

    function render(filterAge = 'all', filterCategory = 'all', filterMonth = 'all', filterLocation = 'all') {
      grid.innerHTML = '';
      const filtered = events.filter(ev => matchesFilter(ev, filterAge, filterCategory, filterMonth, filterLocation));
      filtered.forEach(ev => {
          const card = document.createElement('div');
          card.className = 'card';
          const categoryPills = eventCategories(ev).map(cat => `<span class=\"pill\">${cat}</span>`).join('');
          card.innerHTML = `
            <div class=\"pill-row\">
              <span class=\"pill\">${ev.source}</span>
              <span class=\"pill\">${bucketLabel(ev)}</span>
              ${categoryPills}
            </div>
            <a class=\"title\" href=\"${ev.url}\" target=\"_blank\" rel=\"noopener\">${ev.title}</a>
            <div class=\"meta muted\">
              <span>${formatDateLabel(ev)}</span>
              ${ev.venue ? `<span>${ev.venue}</span>` : ''}
              ${ev.price ? `<span>${ev.price}</span>` : ''}
            </div>
          `;
          grid.appendChild(card);
      });
      const countEl = document.getElementById('result-count');
      if (countEl) {
        const monthText = filterMonth === 'all' ? 'All upcoming' : monthLabel(filterMonth);
        const ageText = filterAge === 'all' ? 'All ages' : filterAge;
        const categoryText = filterCategory === 'all' ? 'All categories' : filterCategory;
        const locationText = filterLocation === 'all' ? 'All locations' : filterLocation;
        countEl.textContent = `${filtered.length} event${filtered.length === 1 ? '' : 's'} shown - ${monthText} - ${ageText} - ${categoryText} - ${locationText}`;
      }
    }

    const state = { age: 'all', category: 'all', month: 'all', location: 'all' };

    document.querySelectorAll('#age-filters .filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#age-filters .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.age = btn.dataset.age;
        render(state.age, state.category, state.month, state.location);
      });
    });

    document.querySelectorAll('#category-filters .filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#category-filters .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.category = btn.dataset.category;
        render(state.age, state.category, state.month, state.location);
      });
    });

    setupMonthFilter();
    setupLocationFilter();
    render(state.age, state.category, state.month, state.location);
  </script>
</body>
</html>
"""


def load_events(path: Path) -> List[dict]:
    with path.open() as f:
        return json.load(f)


def source_summary(events: List[dict]) -> str:
    seen: list[str] = []
    for ev in events:
        src = (ev.get("source") or "").strip().lower()
        if src and src not in seen:
            seen.append(src)
    labels = [SOURCE_LABELS.get(src, src.title()) for src in seen]
    return ", ".join(labels) if labels else "No sources"


def scraped_places_summary() -> str:
    labels = [SOURCE_LABELS.get(src, src.title()) for src in SCRAPED_PLACE_ORDER]
    return ", ".join(labels)


def render_html(events: List[dict]) -> str:
    # Escape HTML-significant characters to avoid accidentally closing script tags.
    events_json = (
        json.dumps(events)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return (
        HTML_TEMPLATE.replace("__SITE_TITLE__", SITE_TITLE)
        .replace("__SCRAPED_PLACES__", scraped_places_summary())
        .replace("__SOURCE_SUMMARY__", source_summary(events))
        .replace("__SOURCE_LABELS_JSON__", json.dumps(SOURCE_LABELS))
        .replace("__EVENTS_JSON__", events_json)
    )


def render_rss(events: List[dict]) -> str:
    now = datetime.now(tz=SG_TZ)
    items = []
    for ev in events:
        start = ev.get("start") or ""
        title = ev.get("title", "Event")
        link = ev.get("url", "")
        if ev.get("age_min") is not None and ev.get("age_max") is not None:
            age_text = f"Ages {ev.get('age_min')}-{ev.get('age_max')}"
        elif ev.get("age_min") is not None:
            age_text = f"Ages {ev.get('age_min')}+"
        else:
            age_text = ""
        category_text = ", ".join(ev.get("categories") or [])
        desc_parts = [ev.get("venue"), ev.get("price"), age_text, category_text]
        description = " | ".join([p for p in desc_parts if p])
        items.append(
            f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <pubDate>{start}</pubDate>
      <description><![CDATA[{description}]]></description>
    </item>"""
        )
    items_xml = "\n".join(items)
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
<rss version=\"2.0\">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{BASE_URL}</link>
    <description>{SITE_DESC}</description>
    <lastBuildDate>{now.isoformat()}</lastBuildDate>
{items_xml}
  </channel>
</rss>
"""


def build(output_dir: Path = Path("site")):
    data_path = Path("data/events.json")
    data = load_events(data_path) if data_path.exists() else []
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(render_html(data), encoding="utf-8")
    (output_dir / "rss.xml").write_text(render_rss(data), encoding="utf-8")
    (output_dir / "events.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Built site with {len(data)} events -> {output_dir}")


def main():
    build()


if __name__ == "__main__":
    main()
