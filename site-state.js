const STATE_KEY='arda-research-state-v2';
let savedState={overrides:{},deleted:[],custom:[],favorites:[],notes:{}};
let items=[];
try {const raw=localStorage.getItem(STATE_KEY);if(raw){const v=JSON.parse(raw);if(v&&Array.isArray(v.deleted)&&Array.isArray(v.custom)&&v.overrides&&v.notes&&Array.isArray(v.favorites))savedState=v;}else{
 let old=[];try{old=JSON.parse(localStorage.getItem('arda-research-v1'))||[]}catch{};if(!Array.isArray(old))old=[];
 let installed=[];try{installed=JSON.parse(localStorage.getItem('arda-catalog-installed'))||[]}catch{};
 for(const c of catalog){const x=old.find(v=>v.ticker===c.ticker||v.id===c.id);if(!x){if(installed.includes(c.ticker))savedState.deleted.push(c.id);continue}const edits={};for(const [k] of schema){if(k in x&&String(x[k])!==String(c[k])&&!legacyHashes[c.ticker]?.[k]?.includes(fnv(x[k])))edits[k]=x[k]}if(Object.keys(edits).length)savedState.overrides[c.id]=edits;}
 savedState.custom=old.filter(v=>v.id!=='demo'&&!catalog.some(c=>c.ticker===v.ticker||c.id===v.id));
}}catch{}
items=catalog.filter(c=>!savedState.deleted.includes(c.id)).map(c=>({...c,...savedState.overrides[c.id],id:c.id})).concat(savedState.custom);
let favorites=new Set(savedState.favorites),notes=savedState.notes;
let selected=items[0]?.id,editing=null;
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function persist(){
 const state={overrides:{},deleted:catalog.filter(c=>!items.some(x=>x.id===c.id)).map(c=>c.id),custom:items.filter(x=>!catalog.some(c=>c.id===x.id)),favorites:[...favorites],notes};
 for(const x of items){const c=catalog.find(v=>v.id===x.id);if(!c)continue;const edits={};for(const [k] of schema)if(String(x[k]??'')!==String(c[k]??''))edits[k]=x[k];if(Object.keys(edits).length)state.overrides[x.id]=edits;}
 try{localStorage.setItem(STATE_KEY,JSON.stringify(state));localStorage.removeItem('arda-research-v1');localStorage.setItem('arda-analysis-revision','2026-10-13-r6');localStorage.setItem('arda-catalog-installed',JSON.stringify(catalog.map(c=>c.ticker)))}catch{alert('Tarayıcıya kayıt yapılamadı. Verilerini yedek indir ile koru.')}
}
