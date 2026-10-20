# Crypto workspace

## Scope and source identity

The US catalog, research, financial data and portfolio implementations remain unchanged. Crypto runs at `/kripto/` with an independent private portfolio namespace and a one-click US switch.

`crypto-market-seed.json` contains the actual CoinMarketCap top 500 snapshot, sorted by provider rank with 500 unique numerical CMC identities. Source/acquisition timestamps are retained. Runtime market refresh uses the official keyless `/public-api/v3/cryptocurrency/listings/latest` endpoint, or the authenticated endpoint when `COINMARKETCAP_API_KEY` exists. Quotes can be the documented v3 USD array. A 15-minute R2 cache, per-isolate deduplication, CAS lease and 30-minute failure backoff preserve the last successful complete universe. No provider restriction is bypassed.

`crypto-meta-seed.json` contains official provider metadata for all initial 500 assets: available websites, technical documents, repositories, explorers, platform contract, category, notice and source dates. Independently reviewed primary-source role descriptions have separate `roleSources` and `verifiedAt`; provider classification is never represented as a reviewed investment thesis. Metadata refresh is bounded to the selected asset, weekly, via the official info endpoint and a shared CAS cache. Failed requests retain prior metadata. A changed provider slug triggers identity review instead of automatic historical-price continuity.

Cross-provider history identities require normalized exact name and symbol or separately recorded primary-source evidence. `crypto-cmc-ids.json` is the stable crosswalk. `crypto-identity-evidence.json` documents retained account aliases. Old assets outside the new universe remain in the registry so private holdings are not silently lost. No symbol-only or guessed-slug alias is used.

## Technical data

`crypto-history-seed.json` contains timestamped daily price observations or explicit source errors. The bounded authoring-only collector paces requests and backs off on rate limits. It never creates a history from a market sparkline. Runtime daily history renewal requires a configured historical-data provider: optional `COINMARKETCAP_API_KEY`, `COINGECKO_DEMO_API_KEY` or `COINGECKO_PRO_API_KEY`. No plaintext key is stored in source. Appropriate provider rights and historical endpoint access are necessary. With no historical connection the dated series remains visible and its age is explicit; current market prices do not refresh an old technical report.

Daily observations must have an actual 00:00 UTC timestamp, positive finite price and no future/intraday sample. Calculations use the most recent contiguous daily segment after any gap, without interpolation. Wilder RSI14, SMA-seeded EMA20/50/200, MACD12/26/9, Bollinger20 bands, within-series drawdown and 30-log-return sample volatility annualized with365 days require adequate sample counts. The 30-observation price range is a support/resistance candidate, not an OHLC pivot or order-book level. ATR/candle patterns cannot be computed from price-only data. Missing indicators remain null.

The radar is a transparent rules-based research screen, not a fundamental quality or expected-return score. It requires a primary-source reviewed role, at least EMA50 history and technical data within72 hours; stable, wrapped, non-tradable and identity-review records are excluded. Platform account records do not receive token trading analysis or market-trade actions. Stablecoin scenarios focus on peg/reserve/redemption rather than price appreciation. Sources and technical dates remain separate.

Selected-asset historical refresh writes a CAS-protected common report cache so public markets, detail, private catalog and portfolio agree. Build-time seed calculation and compact series indices avoid recalculating all500 indicator sets on a cold request. Dated calculations remain tied to their exact source observations. A WeakMap memo avoids repeated series assembly. Catalog payloads omit full chart histories; public rows use at most30 chart points.

## Research desk and private portfolio

Public research includes search/pagination, advanced type/category/rank/liquidity/technical filters, up to4 asset comparisons, a fee-aware user-defined spot scenario and visible data coverage. Watchlists and up to100 thesis/invalidation/review-date notes are browser-local when signed out and account-private when signed in. `/api/crypto/workspace` requires identity, origin/header checks, CAS revisions, field/size/date validation and private no-store responses. JSON research export/import carries only personal research, merges without overwriting existing notes, and never distributes a standalone quote dataset.

The separate `/kripto/portfoyum/` uses `private-crypto-portfolios/v1/` hashed account storage. Positions, ledger, alerts, observations, events and reports are separate from US accounts. Fees, partial sales, latest-trade undo, cash-flow-separated observations, manual dated events and JSON portfolio export remain available. Historical/snapshot prices cannot trigger price alarms; current provider prices are required. No wallets, seed phrases or exchange trading permissions are requested.

Portfolio analytics show completeness, largest weight and HHI concentration (not correlation or predicted loss). User-defined target weights provide an arithmetic allocation preview only, without executing trades or creating a cash balance. Currency formats retain tiny prices. Existing user-triggered AI configuration remains optional; no bulk paid AI generation is performed.

## Validation

`verify-crypto.mjs` covers 500 ranked identities, daily technical boundaries, source failure retention, independent account storage, transactions, snapshots/alarms, client initialization, deep links, historical TTL and common reports, weekly metadata retention and identity-transition handling. `verify-crypto-universe.mjs` exercises all500 analysis endpoints and detail views with identity/technical guards. `verify-crypto-workspace.mjs` checks private research access/isolation/revision/date validation, filters/watchlists, import, fee scenarios, concentration and allocation arithmetic. Existing US, account, workbench, dashboard, privacy and public worker tests remain applicable. Browser visual QA is unavailable in this environment.
