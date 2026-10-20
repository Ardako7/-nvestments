# BIST research implementation

The existing US and crypto datasets and account records are retained. The BIST universe is the official XU500 constituent list from KAP, not a calculated top-500 ranking. The directory was cross-checked by MKK company identity against the official PDF; the list is dated and does not claim automatic index reconstitution.

## Source snapshots

- `data/bist-universe.json`: 500 unique constituents, exact KAP company identity, sector and links. Sources: [KAP indices](https://www.kap.org.tr/tr/Endeksler), [official index PDF](https://www.kap.org.tr/tr/api/company/indices/pdf/endeksler), [sectors](https://www.kap.org.tr/tr/Sektorler), [company directory](https://www.kap.org.tr/tr/bist-sirketler).
- `data/bist-financials.json`: 488 source reports from KAP's normal public all-company financial-table export for 2026/6. The public homepage financial-table form produces `GET /tr/api/financialTable/checkFileExist/2026/2` then `GET /tr/api/financialTable/download/2026/2`. The source ZIP contains 778 HTML-format `.xls` reports. The 2026/9 export was empty at authoring time and was not treated as a successful financial update.
- `scripts/prepare-bist-financials.py <explicitly-downloaded-archive.zip>` normalizes this export. It matches full ticker tokens, including compound issuer codes; prefers consolidated reports, then the highest disclosure ID within that basis. Each displayed amount is converted from its reported TL unit. Bank balance sheets use the total column, not the TRY-only column. Parent-share and total-group profit are distinct. Income comparisons use the same filing's prior-year six-month column; balance comparisons use the filing's prior year-end column. No invented zeroes, annualized earnings, financial-debt proxy from total liabilities, or mixed restated/unrestated growth series.
- `data/bist-summary-snapshots.json`: 11 additional explicitly downloaded public KAP summary pages. `scripts/prepare-bist-summaries.py <downloaded-page-directory>` preserves only the latest visible summary column, source, unit and label. These are distinctly labeled snapshots; prior summary columns are not used for growth or comparisons. The duration of the income period must be checked in the original filing. They do not count as full six-month reports. DOCO has no numeric KAP snapshot in this release; its official links and provider financial panel remain available.
- `data/bist-business.json`: 49 issuer-specific business models, structural drivers and risks, with official sources. Other issuers show official KAP sector/industry, a provider company profile and an explicitly marked research checklist; they are not passed off as editorially reviewed models.

This is bounded authoring research, not a production crawler. High-volume KAP integration requires an authorized data agreement/API. Refreshing this source data requires a verified authoring update; the UI discloses the snapshot date and potential newer individual filings.

## Quotes, technicals and missing data

Public prices, charts, RSI/MACD, technical summaries, company profiles and supplemental financials use official TradingView embeds and attribution. No provider-widget prices are extracted, redistributed or fed into authored reports. Panels mount only for the active company/tab. Provider links remain available on failure. No numerical BIST support/resistance is manufactured without an appropriate licensed historical series. The scenario calculator is explicitly user-defined and excludes fees, gaps and execution risk.

BIST account quotes reuse the existing private portfolio architecture with Yahoo `.IS` symbols, TRY validation, a separate cache, 120-second TTL, bounded 25-symbol refresh and manual-price fallback. These are private account requests, not a public quote API. The portfolio uses Istanbul session dates. Trades are records, not exchange orders; corporate actions, taxes and dividends are not automatically accounted for.

## Account isolation and validation

BIST records use `private-bist-portfolios/v1/` and separate quote/AI-budget namespaces. Existing origin/CSRF checks, optimistic revision checks and per-user hashed keys remain in place. No existing account data is migrated, deleted or overwritten. Watchlists and company notes on the public BIST research screen are local to the browser, separately named and disclosed. User-triggered AI receives source data, not account email or display name; no batch AI calls are made by the build.

Run `bash scripts/build.sh`, `node scripts/verify-bist.mjs`, and the existing US/crypto/privacy/live-worker suites. UI initialization is verified through functional DOM harnesses; real browser visual QA was unavailable in this environment. `/api/research-status` reads coverage and dates without initiating a provider refresh. Existing paused automations are preserved.
