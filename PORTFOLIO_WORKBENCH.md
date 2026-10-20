# Portfolio workbench

Six sections: overview, observation performance, transactions, earnings calendar, alerts and hypothetical transfers. Authentication and the public audience remain unchanged.

Account documents retain their existing private R2 key. New fields `ledger` and `alerts` are additive. Price observations live under the same hashed account key plus `.observations.json`; no public asset route serves these files. Optimistic R2 writes and the existing revision guard prevent overwriting concurrent position edits. Clearing an account deletes the observation and AI report documents and clears its transactions/alarms.

`POST /api/portfolio/tools` accepts same-origin authenticated actions: trade, undo latest trade, add alarm, remove alarm. Weighted average cost includes buy fees. Sales reduce quantity and subtract sell fees from realized profit; overselling is rejected. Position corrections are labelled non-trade records, retain prior realized history and start a new performance segment. Transactions are chronological; initial positions are not invented historical transactions. The latest trade can be reversed, with an audit note and a fresh observation segment.

Authenticated quote reads record complete valuations. Missing or stale provider prices can use a visibly marked user fallback. Partial portfolios never become zero-valued observations. Recent observations are compacted to 10-minute buckets; observations over two days old are compacted by day, with segment starts retained where capacity permits. Storage is capped at 1,500 points. Performance compares value with initial value plus net recorded buy/sell cash flows; it is a dollar change, not TWR, MWR or a reconstruction of pre-recording market history. Cash balances, dividends, splits and tax are not automatically supported.

Price alerts use provider quotes only, are one-shot, and persist their trigger price/time. They are checked when the page refreshes quotes, including its five-minute interval while visible. Optional Notifications require a direct visitor click and browser permission. This version has no email or closed-page push delivery. Changing holdings or quotes invalidates an existing comparison result.

Calendar dates and guidance retain explicit source/check dates. Unknown dates and consensus are not filled in. ASML and TSM event updates were separately verified against their official sources on 15 October 2026. Current research/technical report dates remain independent from quote times. Technical reports over seven days old get a visible age badge; this is a display rule, not a recalculation of indicators.

Verification: `verify-portfolio-workbench.mjs`, account/portfolio dashboard regressions, public worker checks, site interactions and ESM artifact validation. Managed browser control was unavailable; visual browser QA was not performed.
