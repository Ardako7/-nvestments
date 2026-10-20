"""One-time, dated authoring import. Does not enable daily provider access or overwrite old dossiers."""
import json,pathlib,sys,datetime,math
ROOT=pathlib.Path(__file__).resolve().parents[1];P=pathlib.Path(sys.argv[1]);profiles=json.loads((ROOT/'data/neocloud-profiles.json').read_text());raw=json.loads((P/'metrics.json').read_text());scope={'__name__':'metrics_helpers'};exec((ROOT/'scripts/analyze-data.py').read_text(),scope);scope.update(ROOT=P,ASOF='2026-10-19')
out={}
for t,p in profiles.items():
 f=raw[t]
 if t=='WULF':
  old=scope['TAGS']['revenue'];scope['TAGS']['revenue']=['Revenues'];f=scope['fundamental'](t);scope['TAGS']['revenue']=old
 def fl(k,period='quarter'):
  z=f['flows'][k][period];return z['val'] if z else None
 rev=f['flows']['revenue']['quarter'];end=rev['end'] if rev else None
 fin={'reportDate':end,'currency':'USD','revenueQuarter':fl('revenue'),'revenueGrowth':f['flows']['revenue']['yoy'],'revenueTTM':fl('revenue','ttm'),'netQuarter':fl('net'),'operatingQuarter':fl('operating'),'grossMargin':fl('gross')/fl('revenue')*100 if fl('gross') is not None and fl('revenue') else None,'operatingMargin':fl('operating')/fl('revenue')*100 if fl('operating') is not None and fl('revenue') else None,'netMargin':fl('net')/fl('revenue')*100 if fl('net') is not None and fl('revenue') else None,'cash':(f['balances']['cash'] or {}).get('val'),'cashDate':(f['balances']['cash'] or {}).get('end'),'marketCap':None,'ps':None,'pe':None,'cfo':fl('cfo','latestPeriod'),'capex':fl('capex','latestPeriod'),'fcf':None,'cashflowPeriod':None}
 cf=f['flows']['cfo']['latestPeriod'];cap=f['flows']['capex']['latestPeriod']
 if cf:fin['cashflowPeriod']=cf['start']+' / '+cf['end']
 if cf and cap and (cf['start'],cf['end'])==(cap['start'],cap['end']):fin['fcf']=cf['val']-cap['val']
 if t=='HUT':fin.update(capex=None,fcf=None)
 if t=='NBIS':
  fin.update(reportDate='2026-06-30',revenueQuarter=582.3e6,revenueGrowth=(582.3/105.1-1)*100,revenueTTM=None,netQuarter=-190.4e6,operatingQuarter=-175.9e6,grossMargin=None,operatingMargin=-175.9/582.3*100,netMargin=-190.4/582.3*100,cash=8042.1e6,cashDate='2026-06-30',cfo=4504.1e6,capex=8130.3e6,fcf=(4504.1-8130.3)*1e6,cashflowPeriod='2026-01-01 / 2026-06-30')
  # Explicit 6-K quarter overrides stale annual-only XBRL. No synthetic TTM comparison.
 chart=json.loads((P/(t+'-chart.json')).read_text())['chart']['result'][0];q=chart['indicators']['quote'][0];bars=[]
 for i,stamp in enumerate(chart.get('timestamp',[])):
  date=datetime.datetime.fromtimestamp(stamp,datetime.timezone.utc).date().isoformat()
  if date>'2026-10-16' or any(q[k][i] is None for k in ['open','high','low','close','volume']):continue
  bars.append({'date':date,**{k:q[k][i] for k in ['open','high','low','close','volume']}})
 assert len(bars)>=50 and bars[-1]['date']=='2026-10-16',t
 cs=[b['close'] for b in bars];price=cs[-1];sma=lambda n:sum(cs[-n:])/n if len(cs)>=n else None
 tr=[max(b['high']-b['low'],abs(b['high']-bars[i-1]['close']),abs(b['low']-bars[i-1]['close'])) for i,b in enumerate(bars) if i>0];atr=sum(tr[:14])/14
 for v in tr[14:]:atr=(atr*13+v)/14
 lows=[];highs=[]
 for i in range(max(2,len(bars)-126),len(bars)-2):
  if bars[i]['low']<min(b['low'] for j,b in enumerate(bars[i-2:i+3]) if j!=2):lows.append(bars[i]['low'])
  if bars[i]['high']>max(b['high'] for j,b in enumerate(bars[i-2:i+3]) if j!=2):highs.append(bars[i]['high'])
 supports=sorted(set(v for v in lows if v<price),reverse=True);resists=sorted(set(v for v in highs if v>price));m50=sma(50);m200=sma(200)
 tech={'price':price,'date':bars[-1]['date'],'bars':len(bars),'ma20':sma(20),'ma50':m50,'ma200':m200,'rsi14':scope['rsi'](cs),'atr14':atr,'atrPct':atr/price*100,'volumeRatio':bars[-1]['volume']/(sum(b['volume'] for b in bars[-21:-1])/20),'return3m':None,'return6m':None,'return12m':None,'relativeSPY':None,'benchmark':'DTCR','relativeSector':None,'support':supports[0] if supports else None,'support2':supports[1] if len(supports)>1 else None,'resistance':resists[0] if resists else None,'resistance2':resists[1] if len(resists)>1 else None,'breakout':max(b['high'] for b in bars[-21:-1]),'trend':'Yükseliş' if m200 and price>m50>m200 else 'Düşüş' if m200 and price<m50<m200 else 'Karma' if m200 else 'Kısa geçmiş','weekly10':None,'weekly40':None,'weeklyLast':None,'yearHigh':max(b['high'] for b in bars[-252:]),'yearLow':min(b['low'] for b in bars[-252:]),'history':[]}
 meta=json.loads((P/(t+'-identity.json')).read_text());evidence={'quarter':f['flows']['revenue']['quarter'],'net':f['flows']['net']['quarter'],'cfo':cf,'capex':cap,'cash':f['balances']['cash']}
 if t=='NBIS':evidence={'method':'Manually verified quarterly release; annual-only companyfacts records excluded.','source':p['source'],'period':'2026-06-30','quarter':'2026-04-01 / 2026-06-30','cashflow':'2026-01-01 / 2026-06-30','checkedAt':'2026-10-19'}
 out[t]={'profile':p,'financial':fin,'technical':tech,'evidence':evidence,'cik':meta['cik'],'checkedAt':'2026-10-19','financialSource':p['source'],'chartSource':'https://query1.finance.yahoo.com/v8/finance/chart/'+t+'?range=2y&interval=1d','note':'Yeni kapsam. İlk 10 puanlamasına otomatik eklenmez; teknik görüntü 16 Ekim son tamamlanmış seansıdır. Günlük canlı yenileme değildir.'}
 print(t,fin['revenueQuarter'],fin['netQuarter'],tech['date'],round(tech['rsi14'],1))
(ROOT/'data/neocloud-additions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
