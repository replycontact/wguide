# Light & Shadow

An extensive **WoW: Forever Human Priest field guide**, researched for a fresh account with **zero Legacy points**. It covers Shadow solo leveling, Holy healing, Human racials, account progression, professions, equipment, macros and PvP.

Research snapshot: **6 November 2026**. Current client references identify build **1.60.1.70790**. Official changes, client data and practical recommendations are distinguished in the text. Unresolved conflicts are retained rather than silently guessed.

## Read the guide

- **[Polished PDF](output/pdf/wow-forever-human-priest-guide.pdf)** — complete book with linked contents, bookmarks, tables and citations.
- **[Single-file offline website](output/site/wow-forever-priest-guide.html)** — download and open in a browser; includes the PDF, fonts, artwork, search and Legacy planner.
- **[Offline bundle](output/site/wguide-offline.zip)** — unzip, then open `index.html`; the separate PDF is included.
- **[Hosted site](https://wguide-human-priest.vastbloom19.chatgpt.site)** — owner-private Sites publication.

The downloaded site needs no CDN, API key, server, account or internet connection. Source links naturally require a connection when followed. The hosted copy has its own host access controls.

## Content

Fifteen chapters cover the first-character plan, exact Legacy purchase sequences, travel/camps/gold, Shadow talents and combat, the Human leveling route, healing spells and talents, practical healing scenarios, equipment, professions and consumables, Shadow/Holy PvP, battleground progression, macros and sources.

The Legacy planner has six separately justified plans. It caps character spending at 16, validates prerequisites and handles account earnings from 0 to 65. Its recommendations match the researched point-by-point snapshots.

## Build

Python 3.12+ and Node.js 22+ are suitable. No browser is needed to generate either artifact.

```sh
python -m pip install -r requirements.txt
npm ci
python scripts/compile_content.py
python scripts/build_pdf.py
python scripts/build_site.py
npm test
```

Editable manuscripts are in `manuscripts/`. The compiler organizes them into the shared `content/` chapters and compiles the planner data. Both final formats use that same chapter catalog. Source ledgers and independent audits are in `research/`.

The PDF builder uses ReportLab and the included fonts; the site builder produces self-contained HTML and ZIP editions. Static hosting output is `dist/`. Deployment configuration is `.openai/hosting.json`. No credentials belong in this repository.

## Verification and limits

The researchers independently checked talent rank caps, row gates, prerequisites and 51-point totals. Automated checks cover Legacy allocations and caps; site navigation and offline resources; PDF text bounds, links, bookmarks and required topics. The PDF is also rendered and visually inspected. Results are in `output/validation.json`.

The site was checked with static parsing and simulated DOM interaction tests. Full browser visual QA was unavailable because the managed preview browser tool was not exposed in this session. No gameplay or macro testing in the live WoW client is claimed.

A universal level-60 BiS list, live respec costs and several unsettled tooltip details could not be established reliably. The guide explains the limits beside the relevant recommendations. Check live tooltips and later hotfixes before spending scarce resources.

## Credits and rights

Created by three GPT-6 Astra high-reasoning authors, two GPT-6 Luna high-reasoning support agents, and the coordinating Codex agent. GPT-6.1 Luna was requested but was not accepted by the available agent service.

Original vector illustrations and editorial layout accompany source-backed original guide text. Noto and DejaVu font licenses are included under `assets/fonts/`. This is an independent, unofficial fan guide; World of Warcraft and related marks belong to Blizzard Entertainment.
