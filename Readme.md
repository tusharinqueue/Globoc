# 🌍 GLOBOC

> An interactive 3D globe that maps every Google Summer of Code organization on the planet. Filter, explore, shortlist, and find your GSoC home.

![MapLibre GL JS](https://img.shields.io/badge/MapLibre_GL_JS-v5.x-00f5ff?style=flat-square&labelColor=0a0a0f)
![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-No_Framework-00ff41?style=flat-square&labelColor=0a0a0f)
![GSoC Orgs](https://img.shields.io/badge/GSoC_Orgs-520+-ff6b35?style=flat-square&labelColor=0a0a0f)
![License](https://img.shields.io/badge/License-MIT-565f89?style=flat-square&labelColor=0a0a0f)

---

## What is this

GLOBOC plots all **520+ GSoC organizations** from 2016–2026 on a spinning dark globe. Each dot is a real org — colored by domain, sized by years of participation. Filter by year, category, or tech stack. Click any org to see its full profile. Find your next open source contribution.

Built as a tool for GSoC 2026 applicants who are overwhelmed by 500+ org choices.

---

## Features

- **3D Globe** — MapLibre globe projection with auto-spin, atmosphere glow, and star field
- **520+ Orgs** — Real data from GSoC Archive 2016–2026, geocoded to HQ city
- **Live Filters** — Filter by year, domain category, tech stack, veteran status
- **Fuzzy Search** — Search org names, countries, and tech stacks via Fuse.js
- **Org Detail Drawer** — Click any marker to see tech stack, participation timeline, slots, and links
- **Heatmap Mode** — Toggle density view to see where orgs are concentrated globally
- **Arc Mode** — Animated great-circle lines from Google HQ, Mountain View to every visible org
- **Shortlist** — Bookmark orgs, persisted to localStorage
- **Time Machine** — Watch GSoC grow from 2005 → 2026 with year playback
- **Stats HUD** — Live animated stats bar: orgs, countries, slots, stacks

---

## Stack

```
MapLibre GL JS v5.x    — globe, layers, clustering, animations
Fuse.js                — fuzzy search
Vanilla JS + HTML + CSS — no framework, no bundler, no npm
OpenFreeMaps           — free dark tile style
```

No build step. No dependencies to install. Open `index.html` and it works.

---

## Getting Started

```bash
git clone https://github.com/tusharinqueue/Globoc
cd Globoc
```

Open `index.html` in your browser. That's it.

> For the org data, run the generator script once to fetch fresh data:
> ```bash
> cd data
> python3 dump.py
> ```
> Requires Python 3 stdlib only. Fetches from `api.gsocorganizations.dev`.

---

## File Structure

```
globoc/
├── index.html       # Entry point
├── app.js           # All JS logic
├── style.css        # Dark terminal theme
└── data/
    ├── orgs.json    # 520+ geocoded GSoC orgs
    └── dump.py      # Data generator script
```

---

## Data Source

Org data is sourced from [gsocorganizations.dev](https://www.gsocorganizations.dev) — a community-maintained GSoC archive by [@nishantwrp](https://github.com/nishantwrp/gsoc-organizations). Coordinates are geocoded from org HQ city.

---

## Why I built this

Finding a GSoC org to contribute to is overwhelming. 500+ orgs, no map, no way to filter by what you actually care about. GLOBOC makes it visual, fast, and actually fun.

---

## License

MIT — do whatever you want with it.

---

*Built with [MapLibre GL JS](https://maplibre.org/) · Data from [GSoC Archive](https://summerofcode.withgoogle.com/archive)*