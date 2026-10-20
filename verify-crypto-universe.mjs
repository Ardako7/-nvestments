import fs from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
globalThis.crypto??=webcrypto;
const originalFetch=globalThis.fetch;
globalThis.fetch=async()=>{throw Error('External requests forbidden in universe test');};
const {default:worker}=await import('../worker/index.js');
const seed=JSON.parse(await fs.readFile('data/crypto-market-seed.json','utf8'));
const records=new Map([['crypto-public/v2/markets.json',{...seed,nextRetryAt:Date.now()+3600000}]]);
const env={BUCKET:{get:async k=>records.has(k)?{etag:'1',json:async()=>structuredClone(records.get(k))}:null,put:async(k,s)=>{records.set(k,JSON.parse(s));return {etag:'1'};},delete:async k=>records.delete(k)}};
const get=p=>worker.fetch(new Request('https://site.test'+p),env);
const market=await(await get('/api/crypto/markets')).json();
const html=await(await get('/kripto/')).text();
const ids=[...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]);
const els=new Map(ids.map(id=>[id,{innerHTML:'',textContent:'',value:['coinKind','coinSort'].includes(id)?'all':'',querySelectorAll:()=>[],scrollIntoView(){},hidden:false,disabled:false}]));
els.set('closeCoin',{onclick:null});const reports=new Map();
const ui={document:{getElementById:id=>{assert(els.has(id),id);return els.get(id);}},Date,Intl,Number,Map,Set,Math,URL,location:{href:'https://site.test/kripto/'},history:{replaceState(){}},setInterval(){},console,fetch:async p=>p.startsWith('/api/crypto/analysis')?Response.json(reports.get(new URL(p,'https://site.test').searchParams.get('id'))):Response.json(market)};
ui.window=ui;vm.runInNewContext(await fs.readFile('web/crypto.js','utf8'),ui);
await new Promise(setImmediate);
let available=0,reviewed=0;
for(const c of seed.coins){
 const response=await get('/api/crypto/analysis?id='+encodeURIComponent(c.id));assert.equal(response.status,200,c.id);
 const d=await response.json(),a=d.coin;assert.equal(a.ticker,c.id);assert.equal(a.market.cmc_id,c.cmc_id);assert.equal(a.meta.cmcId,c.cmc_id);assert(a.moat.length>20);assert(a.future.length>20);if(a.meta.roleSources?.length)reviewed++;
 if(a.technical.available){available++;assert(a.technical.samples>=15);assert(Number.isFinite(a.technical.rsi14));assert(a.technical.rsi14>=0&&a.technical.rsi14<=100);assert(a.technical.series.length<=90);for(let i=0;i<a.technical.series.length;i++){const p=a.technical.series[i];assert.equal(p[0]%864e5,0);assert(p[1]>0);if(i)assert.equal(p[0]-a.technical.series[i-1][0],864e5);}}
 if(a.meta.nonTradable||a.meta.identityReview)assert.equal(a.technical.available,false);
 reports.set(c.id,d);await ui.ArdaCrypto.openCoin(c.id);const rendered=els.get('coinDetail').innerHTML;assert(rendered.includes('Varlığın rolü'));assert(rendered.includes('Token ekonomisi'));assert(!rendered.includes('NaN'));assert(!rendered.includes('>undefined<'));assert(!rendered.includes('javascript:'));
}
assert.equal(reports.size,500);globalThis.fetch=originalFetch;
console.log(JSON.stringify({pass:true,profilesAndDetailViews:reports.size,primarySourceRoles:reviewed,dailyTechnicalAvailable:available,allIdentityAndNonTradableGuards:true}));
