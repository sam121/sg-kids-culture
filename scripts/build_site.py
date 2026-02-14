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
  <link href=\"https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Space+Grotesk:wght@400;500;700&display=swap\" rel=\"stylesheet\" />
  <style>
    :root {
      --bg: #f5f2e9;
      --bg-alt: #ece6d7;
      --card: #fffdf7;
      --ink: #23262f;
      --muted: #5b6376;
      --accent: #0f766e;
      --accent-2: #ad5b27;
      --line: #d7d1c0;
      --pill: #e2f3f1;
      --shadow: 0 16px 36px rgba(31, 36, 48, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Space Grotesk', system-ui, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at 10% -10%, #fce9c9 0%, rgba(252, 233, 201, 0) 70%),
        radial-gradient(900px 420px at 90% 0%, #d8f1ec 0%, rgba(216, 241, 236, 0) 75%),
        linear-gradient(180deg, var(--bg) 0%, #f8f5ee 100%);
    }
    .shell { max-width: 1180px; margin: 0 auto; padding: 28px 18px 72px; }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      padding: 10px 0 18px;
      border-bottom: 1px solid var(--line);
    }
    .brand { font-weight: 700; letter-spacing: 0.1px; color: var(--ink); text-decoration: none; }
    .nav { display: flex; gap: 14px; flex-wrap: wrap; }
    .nav a { color: var(--muted); text-decoration: none; font-weight: 600; }
    .nav a:hover { color: var(--ink); }
    .hero {
      margin-top: 18px;
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 14px;
      align-items: stretch;
    }
    .hero-card {
      background: linear-gradient(145deg, #fffef8 0%, #f5f7fb 100%);
      border: 1px solid var(--line);
      border-radius: 20px;
      box-shadow: var(--shadow);
      padding: 20px;
    }
    h1 {
      margin: 0;
      font-family: 'Fraunces', serif;
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.1;
      letter-spacing: -0.4px;
    }
    .subtitle {
      margin-top: 10px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
      max-width: 70ch;
    }
    .hero-links { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
    .hero-links a {
      border-radius: 999px;
      border: 1px solid var(--line);
      padding: 8px 12px;
      text-decoration: none;
      color: var(--ink);
      font-weight: 600;
      background: #fff;
    }
    .hero-links a.primary {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fff;
      padding: 12px;
    }
    .stat .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat .value { margin-top: 6px; font-size: 24px; font-weight: 700; line-height: 1.1; }
    .stat .tiny { margin-top: 4px; color: var(--muted); font-size: 12px; }
    .muted { color: var(--muted); font-size: 14px; line-height: 1.5; }
    .intro-block {
      margin-top: 14px;
      background: rgba(255, 255, 255, 0.65);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 28px; }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px 16px 18px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: transform 140ms ease, box-shadow 140ms ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 18px 34px rgba(31, 36, 48, 0.12); }
    .title { font-weight: 700; font-size: 18px; margin: 0; color: var(--ink); text-decoration: none; }
    .meta { display: flex; flex-direction: column; gap: 6px; }
    .pill-row { display: flex; gap: 8px; flex-wrap: wrap; }
    .pill {
      background: var(--pill);
      color: var(--accent);
      border: 1px solid #c3e8e3;
      padding: 5px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
    }
    .pill-source {
      background: #fcefe5;
      color: var(--accent-2);
      border-color: #f2d1bb;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .panel {
      margin-top: 18px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.7);
    }
    .filters { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }
    .filter-groups { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 2px; }
    .filter-group .muted { font-size: 13px; text-transform: uppercase; letter-spacing: 0.4px; }
    .month-select {
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      padding: 8px 12px;
      border-radius: 10px;
      font-weight: 600;
      min-width: 200px;
    }
    .filter-btn {
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      padding: 8px 12px;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
    }
    .filter-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
    .count { margin-top: 10px; }
    .signup {
      margin-top: 22px;
      padding: 16px;
      border: 1px dashed var(--line);
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.6);
    }
    footer { margin-top: 32px; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 14px; }
    @media (max-width: 980px) {
      .hero { grid-template-columns: 1fr; }
      .filter-groups { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class=\"shell\">
    <div class=\"topbar\">
      <a class=\"brand\" href=\"index.html\">Singapore Social Events</a>
      <div class=\"nav\">
        <a href=\"index.html\">Browse</a>
        <a href=\"about.html\">About</a>
        <a href=\"rss.xml\">RSS</a>
      </div>
    </div>

    <section class=\"hero\">
      <div class=\"hero-card\">
        <h1>__SITE_TITLE__</h1>
        <div class=\"subtitle\">Weekly social and cultural listings across theatre, music, museums, cinema, and festivals in Singapore. Refreshes every Monday at 9:00 AM SGT.</div>
        <div class=\"hero-links\">
          <a class=\"primary\" href=\"#filters\">Start Filtering</a>
          <a href=\"about.html\">How This Works</a>
          <a href=\"rss.xml\">Subscribe via RSS</a>
        </div>
        <div class=\"intro-block muted\">
          Tracking: __SCRAPED_PLACES__.<br />
          This run includes events from: __SOURCE_SUMMARY__.
        </div>
      </div>
      <div class=\"hero-card\">
        <div class=\"stats\">
          <div class=\"stat\">
            <div class=\"label\">Events In Feed</div>
            <div class=\"value\" id=\"stat-total\">0</div>
          </div>
          <div class=\"stat\">
            <div class=\"label\">Upcoming</div>
            <div class=\"value\" id=\"stat-upcoming\">0</div>
          </div>
          <div class=\"stat\">
            <div class=\"label\">Sources</div>
            <div class=\"value\" id=\"stat-sources\">0</div>
          </div>
          <div class=\"stat\">
            <div class=\"label\">Last Build</div>
            <div class=\"tiny\">__UPDATED_AT__</div>
          </div>
        </div>
      </div>
    </section>

    <div class=\"panel\" id=\"filters\">
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
    </div>

    <div class=\"signup\">
      <div class=\"muted\" style=\"margin-bottom:8px;\">Get this list by email (Kit):</div>
      <div id=\"kit-embed\">Paste your Kit embed script here once you have the form ID.</div>
    </div>

    <div id=\"grid\" class=\"grid\"></div>

    <footer>
      <div>Generated automatically from public pages. Sources in this run: __SOURCE_SUMMARY__.</div>
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
      filtered.sort((a, b) => {
        const aDate = parseDateSafe(a.start);
        const bDate = parseDateSafe(b.start);
        if (!aDate && !bDate) return (a.title || '').localeCompare(b.title || '');
        if (!aDate) return 1;
        if (!bDate) return -1;
        return aDate - bDate;
      });
      filtered.forEach(ev => {
          const card = document.createElement('div');
          card.className = 'card';
          const categoryPills = eventCategories(ev).map(cat => `<span class=\"pill\">${cat}</span>`).join('');
          card.innerHTML = `
            <div class=\"pill-row\">
              <span class=\"pill pill-source\">${sourceLabel(ev.source)}</span>
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

    function setupStats() {
      const total = events.length;
      const upcoming = events.filter(ev => {
        const end = parseDateSafe(ev.end);
        const start = parseDateSafe(ev.start);
        const d = end || start;
        if (!d) return true;
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        return d >= today;
      }).length;
      const srcCount = new Set(events.map(e => (e.source || '').toLowerCase()).filter(Boolean)).size;
      const totalEl = document.getElementById('stat-total');
      const upcomingEl = document.getElementById('stat-upcoming');
      const srcEl = document.getElementById('stat-sources');
      if (totalEl) totalEl.textContent = String(total);
      if (upcomingEl) upcomingEl.textContent = String(upcoming);
      if (srcEl) srcEl.textContent = String(srcCount);
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
    setupStats();
    render(state.age, state.category, state.month, state.location);
  </script>
</body>
</html>
"""

ABOUT_TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>About - __SITE_TITLE__</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Space+Grotesk:wght@400;500;700&display=swap\" rel=\"stylesheet\" />
  <style>
    :root {
      --bg: #f5f2e9;
      --card: #fffdf7;
      --ink: #23262f;
      --muted: #5b6376;
      --line: #d7d1c0;
      --accent: #0f766e;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Space Grotesk', system-ui, sans-serif; color: var(--ink); background: linear-gradient(180deg, var(--bg) 0%, #f8f5ee 100%); }
    .shell { max-width: 920px; margin: 0 auto; padding: 28px 18px 70px; }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; border-bottom: 1px solid var(--line); padding-bottom: 14px; }
    .topbar a { text-decoration: none; color: var(--muted); font-weight: 600; }
    .topbar a:hover { color: var(--ink); }
    .card { margin-top: 18px; background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 20px; }
    h1 { margin: 0; font-family: 'Fraunces', serif; font-size: clamp(28px, 4vw, 38px); }
    h2 { margin: 18px 0 8px; font-size: 17px; }
    p, li { color: var(--muted); line-height: 1.65; }
    ul { padding-left: 18px; margin: 8px 0 0; }
    code { background: #f1eee5; border-radius: 4px; padding: 1px 5px; }
  </style>
</head>
<body>
  <div class=\"shell\">
    <div class=\"topbar\">
      <a href=\"index.html\">Back to listings</a>
      <a href=\"rss.xml\">RSS</a>
    </div>
    <div class=\"card\">
      <h1>About This Feed</h1>
      <p>This project aggregates public event listings in Singapore into one filterable feed with age, category, month, and location filters.</p>

      <h2>Current Coverage</h2>
      <p>Configured sources: __SCRAPED_PLACES__.</p>
      <p>Sources with events in the latest build: __SOURCE_SUMMARY__.</p>

      <h2>How Dates Are Displayed</h2>
      <ul>
        <li><code>On ...</code> for single-date events.</li>
        <li><code>Runs ... to ...</code> when a clear start and end date are found.</li>
        <li><code>From ...</code> when only a start date is available.</li>
        <li><code>Date TBC</code> when source pages do not provide parseable dates.</li>
      </ul>

      <h2>Age Logic</h2>
      <ul>
        <li>Recognizes year and month formats, including ranges like <code>16-20 months</code>.</li>
        <li>UI buckets remain <code>0-5</code>, <code>6-12</code>, and <code>13-17</code> for consistent filtering.</li>
      </ul>

      <h2>Limitations</h2>
      <ul>
        <li>No official APIs are available for some venues, so extraction depends on page structure.</li>
        <li>Listings can change quickly and may lag until the next scheduled refresh.</li>
      </ul>
    </div>
  </div>
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
        .replace("__UPDATED_AT__", datetime.now(tz=SG_TZ).strftime("%d %b %Y, %H:%M SGT"))
        .replace("__SOURCE_LABELS_JSON__", json.dumps(SOURCE_LABELS))
        .replace("__EVENTS_JSON__", events_json)
    )


def render_about(events: List[dict]) -> str:
    return (
        ABOUT_TEMPLATE.replace("__SITE_TITLE__", SITE_TITLE)
        .replace("__SCRAPED_PLACES__", scraped_places_summary())
        .replace("__SOURCE_SUMMARY__", source_summary(events))
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
    (output_dir / "about.html").write_text(render_about(data), encoding="utf-8")
    (output_dir / "rss.xml").write_text(render_rss(data), encoding="utf-8")
    (output_dir / "events.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Built site with {len(data)} events -> {output_dir}")


def main():
    build()


if __name__ == "__main__":
    main()
