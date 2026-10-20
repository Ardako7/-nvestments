import fs from 'node:fs/promises';import assert from 'node:assert/strict';
const code=await fs.readFile('worker/index.js','utf8');const {default:worker}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const store=new Map(),env={BUCKET:{get:async k=>store.has(k)?{json:async()=>JSON.parse(store.get(k))}:null,put:async(k,v)=>store.set(k,v)}};
const realFetch=globalThis.fetch;let calls=0;globalThis.fetch=async url=>{calls++;return new Response('<rss><channel><item><title>Official company &amp; product update</title><link>https://example.com/official-release</link><pubDate>'+new Date().toUTCString()+'</pubDate></item></channel></rss>')};
const call=p=>worker.fetch(new Request('https://example.com'+p),env);
for(const path of ['/','/hisse/MRVL/','/hakkimizda/']){const r=await call(path);assert.equal(r.status,200);assert((await r.text()).includes('Arda'))}
assert.equal((await call('/analysis-audit.json')).status,404);assert.equal((await call('/companies.json')).status,404);
const a=await (await call('/api/daily-bulletin')).json();assert(a.updatedAt&&!a.stale);assert.equal(calls,10);assert(store.has('daily-bulletin/latest.json'));const b=await(await call('/api/daily-bulletin')).json();assert.equal(b.updatedAt,a.updatedAt);assert.equal(calls,10);assert(b.cached);
assert.equal((await worker.fetch(new Request('https://example.com/api/daily-bulletin',{method:'POST',body:'untrusted input'}),env)).status,405);
const info=await(await call('/api/update-info')).json();assert.equal(info.sourceCount,10);assert(info.priceSource.includes('TradingView'));
const html=await(await call('/')).text();const embedded=html.slice(html.indexOf('const catalog=')+14,html.indexOf('const legacyHashes='));const catalog=JSON.parse(embedded.trim().replace(/;$/,''));assert.equal(catalog.length,107);assert(catalog.every(c=>c.analysis.technical.history.length===0));assert(html.includes('embed-widget-mini-symbol-overview.js'));assert(html.includes('refreshDailyNews();'));
globalThis.fetch=realFetch;console.log('PASS public routes,raw data excluded,10 feed reads,persistent cache readback,daily dedup,no arbitrary writes,101 stripped histories and provider widgets');
