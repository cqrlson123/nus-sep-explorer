# NUS SEP Explorer

A local, static web app for browsing, searching, filtering and shortlisting NUS School of Computing SEP
(Student Exchange Programme) partner universities, built from your downloaded pre-approved course-mapping
list (`ps.xls`).

## Running it

```bash
cd sep-explorer
python3 -m http.server 8743
```

Then open http://localhost:8743 in your browser. (It must be served over HTTP, not opened as a `file://`
path, because the page fetches `data/data.json`.)

If you're driving this from Claude Code in this project, `preview_start` with the `sep-explorer` launch
config (see `../.claude/launch.json`) does the same thing.

## What it does

- **Search** by university name, or by course code/title (matches either the partner university's course or
  the NUS course it maps to — e.g. search `CS3244` to see every university with a pre-approved-list mapping
  to Machine Learning).
- **Filter** by region, country, and pre-approval status.
- **Shortlist** universities (☆ button) — saved in your browser's `localStorage`, so it persists across
  reloads but stays local to your machine/browser.
- **Detail view** per university: every course-mapping row on file, with its approval status
  (pre-approved / not approved / unspecified), plus:
  - a link to **search** for the university's official website, and
  - a link to **search** for its current academic calendar for **AY2027/2028 Semester 1**.

## Why links are search links, not direct URLs

Most partner universities have not published AY2027/28 semester dates yet (typically only ~1 year ahead),
and guessing 220+ institutions' exact homepage/calendar URLs risks silently pointing you at outdated or
wrong pages. Each university's link opens a pre-filled Google search instead, so you always land on
whatever the university's real, current page is. If you want, I can look up and hard-code verified real
links for the specific universities you shortlist — that's a much smaller, checkable set.

## Data notes

- Scope: **School of Computing** only (that's all `ps.xls` contained — 221 partner "universities", 5,302
  mapping rows).
- 5 mapping rows had no partner-university name in the source spreadsheet (a data-entry gap, not a parsing
  error); they're grouped under **"(University not specified in source data)"** — cross-check those against
  the original spreadsheet/SEP portal if you need them.
- Country/region tags are a browsing aid I added for filtering, not sourced from the spreadsheet — check the
  "Unknown" bucket if a university doesn't show a country.
- "Pre-approved" reflects the `Pre Approved?` column in the source file at the time you downloaded it —
  always cross-check against the current SEP course mapping list before relying on it, since it's revised
  every application cycle.

## Regenerating data.json

If you download an updated `ps.xls` from the SEP portal:

```bash
python3 scripts/build_data.py
```

It reads from `~/Downloads/ps.xls` and rewrites `data/data.json`.
