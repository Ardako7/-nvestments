import assert from 'node:assert/strict';import fs from 'node:fs/promises';import {webcrypto} from 'node:crypto';globalThis.crypto??=webcrypto;
const source=await fs.readFile('worker/index.js','utf8'),{default:worker}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const records=new Map();let seq=0;const env={BUCKET:{get:async key=>{const r=records.get(key);return r?{etag:r.etag,json:async()=>JSON.parse(r.value)}:null},put:async(key,value,options)=>{const current=records.get(key),cond=options.onlyIf;if(cond?.etagMatches&&current?.etag!==cond.etagMatches)return null;if(cond?.etagDoesNotMatch==='*'&&current)return null;const etag=String(++seq);records.set(key,{value,etag});return {etag}}}};
function call(user,method='GET',body,origin='https://site.test',extra={}){return worker.fetch(new Request('https://site.test/api/portfolio',{method,headers:{...(user?{'oai-authenticated-user-id':user,'oai-authenticated-user-email':user+'@example.com'}:{}),Origin:origin,'X-Arda-Portfolio':'1','Content-Type':'application/json',...extra},...(body?{body:JSON.stringify(body)}:{})}),env)}
assert.equal((await call(null)).status,401);assert.equal((await call(null,'PUT',{})).status,401);
let a=await(await call('alice')).json();assert.equal(a.holdings.length,0);
const payload={username:'Alice',revision:0,holdings:[{ticker:'MRVL',quantity:10,cost:150,currentPrice:160}]};
assert.equal((await call('alice','PUT',payload,'https://evil.test')).status,403);
assert.equal((await call('alice','PUT',payload,'https://site.test',{'X-Arda-Portfolio':''})).status,403);
let response=await call('alice','PUT',payload);assert.equal(response.status,200);a=await response.json();assert.equal(a.revision,1);assert.equal(a.holdings[0].priceSource,'Kullanıcı girişi');
assert.equal((await(await call('bob')).json()).holdings.length,0);assert.equal((await(await call('alice')).json()).holdings.length,1);
assert.equal((await call('alice','PUT',payload)).status,409);
assert.equal((await call('alice','PUT',{...payload,revision:1,holdings:[{...payload.holdings[0],ticker:'FAKE'}]})).status,400);
assert.equal((await call('alice','PUT',{...payload,revision:1,holdings:[{...payload.holdings[0],quantity:-1}]})).status,400);
assert.equal((await call('alice','PUT',{...payload,revision:1,holdings:[payload.holdings[0],payload.holdings[0]]})).status,400);
const timestamp=a.holdings[0].priceAsOf;response=await call('alice','PUT',{...payload,revision:1,username:'Alice2'});a=await response.json();assert.equal(a.holdings[0].priceAsOf,timestamp);
response=await call('alice','DELETE',{revision:2});assert.equal(response.status,200);a=await response.json();assert.equal(a.holdings.length,0);assert.equal(a.username,'');assert.equal((await(await call('alice')).json()).holdings.length,0);
const html=await(await worker.fetch(new Request('https://site.test/portfoyum/'),env)).text();assert(html.includes('target="_top"'));assert(html.includes('AI')||html.includes('otomatik'));assert.equal((await worker.fetch(new Request('https://site.test/private-portfolios/v1/alice.json'),env)).status,404);
console.log('PASS: auth required, per-user isolation, origin/CSRF checks, revision conflicts, invalid data rejected, price timestamps retained, clear/readback, private records not routable');
