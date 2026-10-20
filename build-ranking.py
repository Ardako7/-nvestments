import json, pathlib, math
P=pathlib.Path('dist')
cs=json.loads((P/'companies.json').read_text())
editorial=json.loads((P/'ranking-editorial.json').read_text())
editorial.update(json.loads((P/'expansion-ranking-editorial.json').read_text()))
def clamp(x,a,b): return max(a,min(b,x))
rows=[]
for c in cs:
 t=c['ticker']; f=c['analysis']['financial']; a=c['analysis']['technical']; e=editorial[t]
 if f['operatingQuarter'] is not None and f['netQuarter'] is not None and f['netQuarter']>1.5*max(f['operatingQuarter'],1): f_for_pe=None
 else: f_for_pe=f['pe']
 op=f['operatingMargin']; net=f['netMargin']; g=f['revenueGrowth']; ps=f['ps']; pe=f_for_pe
 profitability=clamp((op if op is not None else net if net is not None else 0)/2+5,0,15) if op is not None or net is not None else 5
 cash=(5 if f['cfo'] is not None and f['cfo']>0 else 0 if f['cfo'] is not None else 2.5)+(5 if f['fcf'] is not None and f['fcf']>0 else 0 if f['fcf'] is not None else 2.5)
 growth=clamp(g/2+5,0,15) if g is not None else 5
 valuation=(10 if pe<=20 else 8 if pe<=30 else 6 if pe<=45 else 4 if pe<=65 else 2) if pe else (8 if ps<=5 else 6 if ps<=10 else 4 if ps<=20 else 2) if ps else 5
 trend=12 if a['trend']=='Yükseliş' else 5 if a['trend']=='Karma' else 3 if a['trend']=='Kısa geçmiş' else 0
 relative=clamp(4+(a['relativeSPY'] or 0)/5,0,8); sector=clamp(2.5+(a['relativeSector'] or 0)/8,0,5)
 extension=5 if a['rsi14']<=70 and (not a['ma50'] or a['price']/a['ma50']<=1.15) else 2 if a['rsi14']<=80 else 0
 parts={'Ürün kalıcılığı':e['durabilityScore'],'Kârlılık':round(profitability,1),'Nakit üretimi':cash,'Gelir büyümesi':round(growth,1),'Değerleme':valuation,'Trend':trend,'Endekse göre güç':round(relative,1),'Sektöre göre güç':round(sector,1),'Fiyatın uzaması':extension}
 fundamental=round(sum(list(parts.values())[:5]),1); technical=round(sum(list(parts.values())[5:]),1)
 row=dict(ticker=t,score=round(fundamental+technical,1),fundamental=fundamental,technical=technical,parts=parts,reason=e['reason'],risk=e['risk'],priceDate=a['date'],reportDate=f['reportDate'],missing=[k for k,v in {'faaliyet marjı':op,'yıllık gelir büyümesi':g,'CFO−capex':f['fcf'],'P/E ve P/S':pe or ps,'200 günlük geçmiş':a['ma200']}.items() if v is None])
 c['ranking']=row;rows.append(row)
rows.sort(key=lambda x:(-x['score'],-x['fundamental'],x['ticker']))
for i,x in enumerate(rows,1):x['rank']=i
(P/'ranking.json').write_text(json.dumps({'date':'2026-10-13','priceCutoff':'2026-10-12','weights':{'fundamental':70,'technical':30},'ranking':rows},ensure_ascii=False,indent=2))
(P/'companies.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2))
print('First10',[(x['ticker'],x['score']) for x in rows[:10]])
