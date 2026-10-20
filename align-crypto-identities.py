from pathlib import Path
import json,datetime
D=Path(__file__).resolve().parents[1]/'data';seed=json.loads((D/'crypto-market-seed.json').read_text());old=json.loads((D/'crypto-legacy-market.json').read_text());m=json.loads((D/'crypto-meta-seed.json').read_text());h=json.loads((D/'crypto-history-seed.json').read_text());cross=json.loads((D/'crypto-cmc-ids.json').read_text());used={c['id'] for c in seed['coins']};evidence=[]
for c in seed['coins']:
 if not c['id'].startswith('cmc-'):continue
 sources=set(m[c['id']].get('roleSources') or []);matches=[]
 for o in old['coins']:
  common=sources.intersection(m.get(o['id'],{}).get('roleSources') or [])
  if o['id'] not in used and c['symbol']==o['symbol'] and common:matches.append((o,common))
 if len(matches)!=1:continue
 o,common=matches[0];priorId=c['id'];c['id']=o['id'];c['coingecko_id']=o['id'];used.add(o['id']);m[o['id']]={**m.get(o['id'],{}),**m[priorId],'coingeckoId':o['id']};cross[str(c['cmc_id'])]={'id':o['id'],'coingeckoId':o['id']}
 if h.get(priorId,{}).get('prices'):h[o['id']]=h[priorId]
 evidence.append({'cmcId':c['cmc_id'],'legacyId':o['id'],'priorTemporaryId':priorId,'identityEvidence':sorted(common),'symbol':c['symbol'],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
assert len({c['id'] for c in seed['coins']})==500
for name,obj in [('crypto-market-seed',seed),('crypto-meta-seed',m),('crypto-history-seed',h),('crypto-cmc-ids',cross)]: (D/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')))
p=D/'crypto-identity-evidence.json';prior=json.loads(p.read_text()) if p.exists() else [];p.write_text(json.dumps(prior+evidence,ensure_ascii=False,indent=2));print({'confirmedLegacyAliases':[(e['cmcId'],e['legacyId']) for e in evidence]})
