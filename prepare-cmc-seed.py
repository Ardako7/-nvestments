from pathlib import Path
import json,datetime,re,argparse
R=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--source-dir',required=True,type=Path);S=parser.parse_args().source_dir;D=R/'data'
listing=json.loads((S/'cmc500.json').read_text());info=json.loads((S/'cmc500-meta.json').read_text());cg=json.loads((S/'cg500.json').read_text())['coins'];old=json.loads((D/'crypto-market-seed.json').read_text())
if not (D/'crypto-legacy-market.json').exists():(D/'crypto-legacy-market.json').write_text(json.dumps(old,ensure_ascii=False,separators=(',',':')))
else:old=json.loads((D/'crypto-legacy-market.json').read_text())
meta=json.loads((D/'crypto-meta-seed.json').read_text());existingCross=json.loads((D/'crypto-cmc-ids.json').read_text()) if (D/'crypto-cmc-ids.json').exists() else {}
extra=S/'crypto-verified-roles-batch5.json'
if extra.exists():
 for k,v in json.loads(extra.read_text()).items():meta[k]={**meta.get(k,{}),**v}
normal=lambda s:''.join(ch for ch in s.casefold() if ch.isalnum())
def indexes(rows):
 out={}
 for c in rows:out.setdefault((normal(c['name']),c['symbol'].lower()),[]).append(c)
 return out
legacy=indexes(old['coins']);candidates=indexes(cg);coins=[];cross={};now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for c in listing['data']:
 key=(normal(c['name']),c['symbol'].lower());prior=legacy.get(key,[]);match=candidates.get(key,[]);prior=prior[0] if len(prior)==1 else None;match=match[0] if len(match)==1 else None
 known=existingCross.get(str(c['id']),{});id=known.get('id') or (prior['id'] if prior else 'cmc-'+str(c['id']));cgid=known.get('coingeckoId') or (prior['id'] if prior else match['id'] if match else None);q=next((q for q in c['quote'] if q.get('symbol')=='USD'),None) if isinstance(c['quote'],list) else c['quote']['USD'];m=info.get(str(c['id']),{});priorMeta=meta.get(id) or (meta.get(prior['id'],{}) if prior else meta.get(cgid,{}) if cgid else {});urls=m.get('urls',{});tags=m.get('tags') or c.get('tags') or [];role=priorMeta.get('role');useful=[t for t in tags if not any(x in t for x in ['portfolio','ecosystem','listing','bankruptcy','sec-cftc','alt-season'])][:6]
 if not role:role=c['name']+' ('+c['symbol']+') '+('kendi ağının varlığı' if m.get('category')=='coin' else 'bir token')+' olarak listeleniyor. '+('Sağlayıcı etiketleri: '+', '.join(useful)+'. ' if useful else '')+'Tokenın kullanım ve gelir hakları resmî teknik belgelerden ayrıca doğrulanmalı.'
 nm={**priorMeta,'role':role,'providerRole':not bool(priorMeta.get('roleSources')),'cmcId':c['id'],'cmcSlug':c['slug'],'coingeckoId':cgid,'homepage':urls.get('website',[]),'technicalDocs':urls.get('technical_doc',[]),'explorers':urls.get('explorer',[]),'sourceCode':urls.get('source_code',[]),'socials':{k:v for k,v in urls.items() if k in ['twitter','reddit','message_board','chat']},'categories':useful,'providerTags':tags,'providerNotice':m.get('notice') or None,'metadataCheckedAt':now,'dateAdded':c.get('date_added'),'dateLaunched':m.get('date_launched'),'assetCategory':m.get('category'),'infiniteSupply':c.get('infinite_supply'),'contract':{c['platform']['name']:c['platform']['token_address']} if c.get('platform') and c['platform'].get('token_address') else priorMeta.get('contract',{}),'metadataSource':'CoinMarketCap'}
 rows=[]
 if m.get('platform') and m['platform'].get('token_address'):rows.append({'chain':m['platform']['name'],'address':m['platform']['token_address']})
 rows += [{'chain':a['platform']['name'],'address':a['contract_address']} for a in m.get('contract_address',[]) if a.get('platform',{}).get('name') and a.get('contract_address')]
 nm['contractRecords']=list({(a['chain'],a['address']):a for a in rows}.values());nm['contractSource']='CoinMarketCap'
 meta[id]=nm;cross[str(c['id'])]={'id':id,'coingeckoId':cgid}
 coins.append({'id':id,'cmc_id':c['id'],'cmc_slug':c['slug'],'coingecko_id':cgid,'symbol':c['symbol'].lower(),'name':c['name'],'image':m.get('logo'),'current_price':q.get('price'),'market_cap':q.get('market_cap'),'market_cap_rank':c['cmc_rank'],'fully_diluted_valuation':q.get('fully_diluted_market_cap'),'total_volume':q.get('volume_24h'),'price_change_percentage_24h':q.get('percent_change_24h'),'price_change_percentage_7d_in_currency':q.get('percent_change_7d'),'price_change_percentage_30d_in_currency':q.get('percent_change_30d'),'price_change_percentage_1h':q.get('percent_change_1h'),'circulating_supply':c.get('circulating_supply'),'total_supply':c.get('total_supply'),'max_supply':c.get('max_supply'),'last_updated':q.get('last_updated',c['last_updated']),'num_market_pairs':c.get('num_market_pairs'),'market_cap_dominance':q.get('market_cap_dominance'),'volume_change_24h':q.get('volume_change_24h'),'cex_volume_24h':q.get('cex_volume_24h'),'dex_volume_24h':q.get('dex_volume_24h'),'tvl':q.get('tvl'),'date_added':c.get('date_added'),'provider':'CoinMarketCap','sparkline_in_7d':None})
assert len(coins)==500 and len({c['id'] for c in coins})==500 and sorted(c['market_cap_rank'] for c in coins)==list(range(1,501))
for name,d in [('crypto-market-seed',{'coins':coins,'fetchedAt':listing['status']['timestamp'],'source':'CoinMarketCap','mode':'dated-snapshot','universe':'CMC top 500','live':False}),('crypto-meta-seed',meta),('crypto-cmc-ids',cross)]:
 (D/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
# Copy verified histories to new stable CMC IDs when an exact name+symbol mapping exists.
h=json.loads((D/'crypto-history-seed.json').read_text())
for c in coins:
 cgId=c['coingecko_id']
 if c['id'] not in h and cgId in h:h[c['id']]=h[cgId]
(D/'crypto-history-seed.json').write_text(json.dumps(h,separators=(',',':')))
print({'CMC':len(coins),'metadata':sum(c['id'] in meta for c in coins),'CG_exact_matches':sum(bool(c['coingecko_id']) for c in coins),'verifiedRoles':sum(bool(meta[c['id']].get('roleSources')) for c in coins),'existingDailyHistory':sum(bool(h.get(c['id'],{}).get('prices')) for c in coins)})
