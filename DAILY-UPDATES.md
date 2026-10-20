# Arda Research daily data and technical calculations

The linked daily task runs at 08:00 Europe/Istanbul. The worker now has an unattended, fixed-universe, persistent update path. A saved schedule does not prove provider access: current production has no historical market-data credentials. The API reports this as `blocked`, not as an updated analysis. No paid account, trial, credential, or data-license entitlement was created by this change.

## Production configuration

Use Sites runtime secrets; never put provider tokens in source, public JSON, query strings on this Site, or task prompts.

| Runtime key | Purpose |
| --- | --- |
| `EODHD_API_TOKEN` | EODHD account with the required US and Turkish exchange historical coverage. The exchange code is discovered from the provider's exchange list using country and currency, never guessed from Yahoo suffixes. Each instrument is confirmed in the exchange's symbol list with matching code and currency. |
| `EODHD_PUBLIC_DISPLAY_ENABLED=true` | Enable only after the account's plan/permission covers displaying the derived analytics on this public Site. A personal or demo key is not treated as evidence of that permission. |
| `COINMARKETCAP_API_KEY` | Existing crypto adapter: current top 500 and historical prices, subject to that account's endpoint/credit and publication permissions. |
| `COINGECKO_PRO_API_KEY` or `COINGECKO_DEMO_API_KEY` | Existing alternative history adapter for coins with a verified CoinGecko identity; historical range, quota, and display rights depend on the plan. An alternative history key does not supply CMC ranking updates. |

Do not claim complete exchange/coin coverage before testing the actual configured account. Failed or unsupported symbols remain visibly missing. Public pricing still uses the official TradingView embeds. The adapter does not scrape those panels or turn them into a redistributed quote feed. Provider licensing and account activation remain external prerequisites.

Primary integration documentation:
- https://eodhd.com/financial-apis/api-for-historical-data-and-volumes
- https://eodhd.com/financial-apis/exchanges-api-list-of-tickers-and-trading-hours
- https://eodhd.com/financial-apis/commercial-vs-personal-license-use
- https://coinmarketcap.com/api/documentation/

## Unattended protocol

1. Resolve the current Site URL and supported service access through Sites `get_site` for `appgprj_6acd5a53623c8191850a2d6fb7fed437`. Send a returned service token only to that origin in `OAI-Sites-Authorization: Bearer <token>`. It is platform service access, not a visitor identity or data-provider key.
2. `GET /api/daily-technical` is a status-only read. Check the configured flags and coverage before attempting any source updates. It reveals required connection names, never secret values.
3. For each configured market `us`, `bist`, `crypto`, start `GET /api/daily-technical?market=<market>&offset=0`. It processes at most five allowlisted instruments. Advance only with the returned `nextOffset`; stop on null. No arbitrary provider URL or instrument list is accepted. Do not parallelize batches against the provider.
4. Stop a market on `blocked`, `pausedSource=true`, repeated HTTP 429, or an entire failed batch; respect retry times and report the gap. Do not spin through hundreds of unsupported requests. Unsupported individual instruments can remain missing while supported ones complete.
5. Re-read `/api/daily-technical`, `/api/research-status`, and selected `/api/daily-technical?market=us&ticker=NVDA` or `/api/daily-technical?market=bist&ticker=THYAO`. Crypto reports are shared with `/api/crypto/catalog` and `/api/crypto/analysis?id=<verified-id>`. Confirm source dates and persistent records; do not infer success merely from HTTP 200.
6. Preserve the existing news update: read `/api/daily-bulletin` twice, checking matching `updatedAt`, `stale=false`, `cached=true` and source status. A successful routine data refresh does not need a deployment.

The endpoint's source cache, per-instrument day stamp, five-minute batch lease, optimistic report writes, and one-hour negative-cache/backoff protect quota and concurrent updates. A failed run retains the last successful report and its actual `asOf`; `computedAt` is a separate processing timestamp. There is no access to private visitor portfolios in this operation.

## Equity calculations

- Only complete sessions, with conservative New York / Istanbul post-close cutoffs, are eligible. Weekends rewind to Friday; exchange holidays are represented by the actual latest provider bar rather than an invented calendar-day bar. A source more than seven calendar days behind the expected cutoff is rejected.
- Download the full 600-calendar-day window again because corporate-action adjustments can restate the whole history. Do not append mismatched old and new adjustment bases.
- Use provider `adjusted_close` (splits and dividends); scale each day's OHLC by `adjusted_close / close`. Preserve the provider's split-adjusted volume; do not scale it with the price factor.
- Require at least 35 validated bars; reject duplicate dates, impossible OHLC, non-finite values and invalid adjustment results. EMA(50/200) stays absent if its own lookback is insufficient.
- Wilder RSI(14), Wilder ATR(14), SMA-seeded EMA(20/50/200) and MACD(12,26,9) are deterministic. No LLM or paid AI call is used in a daily refresh.
- Pivot levels require two lower/higher neighboring candles on each side within 120 sessions. No confirmed pivot means null. Prior 20-session bands are separate observations, not mislabeled confirmed levels or price targets.
- No fixed target return, personal trade instruction, or automatic re-ranking of the long-term thesis is generated.

The shared daily panel appears on US company reader pages, the main US company view and BIST's technical tab. Account portfolio catalogs overlay only verified daily technical fields; business models, balance sheets, fundamental research dates and users' holdings are unchanged. Older editorial technical scenarios remain explicitly dated.

## Tests and limits

`node scripts/verify-daily-technical.mjs` exercises arithmetic, flat/rising/split series, incomplete bars, validation, weekend cutoffs, fixed-universe paging, storage readback, source-error retention and backoff, secret exclusion, three-market catalog compatibility and missing-source UI. Existing privacy, US, crypto, BIST and news suites are retained. Provider-integration tests use clearly labeled synthetic test fixtures; they do not seed production. Live provider refresh cannot be verified until valid credentials and suitable publication permissions are connected. Real browser visual QA is unavailable in this environment.
