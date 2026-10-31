# Browser test notes

The dashboard has no external JavaScript library: the three charts and KPI sparklines are drawn directly as inline SVG, so the page works offline, loads instantaneously, and prints cleanly. The only external request is the optional Open Sans web font (the page falls back to Segoe UI or the system font).

Tested in headless Chromium against the built HTML file, verifying layout, interactive filtering, and SVG chart rendering.

| Test | Result |
|---|---|
| Desktop 1920 and 1440 px, light theme: no horizontal page overflow, table cells on one line | Pass |
| Desktop 1280 px: table scrolls cleanly inside its card container | Works |
| Dark theme toggle, charts redraw in dark colours | Pass |
| Phone width 390 px: no horizontal overflow; charts adapt (shorter labels, fewer ticks) | Pass |
| Click a NICU row, use the NICU dropdown, filter by ODN network (e.g. Yorkshire & Humber), sort a column, select with the Enter key | Pass |
| Charts for the National NICU benchmark and for individual units (including small cohorts `<50` marked `*` and `<23` shown as "too few") | Checked visually, no script errors |
| Expandable Methodology & Automated Validation table (`<details>`) | Renders all 22 checks cleanly |
