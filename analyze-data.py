import json,math,statistics,datetime,pathlib
ROOT=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data'); OUT=pathlib.Path('/workspace/sites/arda-research/dist'); ASOF='2026-10-13'
def day(s):return datetime.date.fromisoformat(s)
def load(t,k):return json.loads((ROOT/(t+'-'+k+'.json')).read_text())
def chart(t):
 d=load(t,'chart')['chart']['result'][0];q=d['indicators']['quote'][0];adj=d['indicators'].get('adjclose',[{}])[0].get('adjclose',q['close']);bars=[]
 for i,stamp in enumerate(d['timestamp']):
  if any(q[k][i] is None for k in ['open','high','low','close','volume']):continue
  date=datetime.datetime.fromtimestamp(stamp,datetime.timezone.utc).date().isoformat()
  if date>ASOF:continue
  c=q['close'][i];factor=(adj[i]/c) if adj[i] is not None and c else 1
  bars.append(dict(date=date,open=q['open'][i],high=q['high'][i],low=q['low'][i],close=c,adjusted=adj[i] or c,volume=q['volume'][i],factor=factor))
 return d['meta'],bars
REVTAGS=['RevenueFromContractWithCustomerExcludingAssessedTax','RevenueFromContractWithCustomerIncludingAssessedTax','Revenues','SalesRevenueNet','Revenue','SalesRevenueGoodsNet','SalesRevenueServicesNet','OperatingRevenues','RegulatedAndUnregulatedOperatingRevenue']
TAGS={'revenue':REVTAGS,'net':['NetIncomeLoss','ProfitLoss','ProfitLossAttributableToOwnersOfParent'],'operating':['OperatingIncomeLoss','ProfitLossFromOperatingActivities'],'gross':['GrossProfit'],'cost':['CostOfRevenue','CostOfGoodsAndServicesSold','CostOfSales'],'cfo':['NetCashProvidedByUsedInOperatingActivities','CashFlowsFromUsedInOperatingActivities'],'capex':['TotalPropertyCapexDerived','PaymentsToAcquirePropertyPlantAndEquipmentAndDevelopSoftware','PaymentsToAcquirePropertyPlantEquipmentAndAcquireIntangibleAssets','PaymentsForCapitalImprovements','PaymentsToDevelopRealEstateAssets','PaymentsToAcquireRealEstate','PaymentsToAcquirePropertyPlantAndEquipment','PaymentsToAcquireProductiveAssets','PurchaseOfPropertyPlantAndEquipment','PurchaseOfPropertyPlantAndEquipmentIntangibleAssets'],'cash':['CashAndCashEquivalentsAtCarryingValue','CashAndCashEquivalents','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'],'shortInvestments':['ShortTermInvestments','MarketableSecuritiesCurrent','AvailableForSaleSecuritiesDebtSecuritiesCurrent'],'assets':['Assets'],'liabilities':['Liabilities'],'currentAssets':['AssetsCurrent','CurrentAssets'],'currentLiabilities':['LiabilitiesCurrent','CurrentLiabilities'],'equity':['StockholdersEquity','StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest','Equity'],'shares':['EntityCommonStockSharesOutstanding','CommonStockSharesOutstanding'],'eps':['EarningsPerShareDiluted','DilutedEarningsLossPerShare'],'debtTotal':['LongTermDebt','LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities','LongTermDebtAndFinanceLeaseObligationsIncludingCurrentMaturities'],'debtCurrent':['DebtCurrent','LongTermDebtCurrent','LongTermDebtAndCapitalLeaseObligationsCurrent','ShortTermBorrowings','CurrentBorrowings'],'debtNoncurrent':['LongTermDebtNoncurrent','NoncurrentBorrowings'],'sbc':['ShareBasedCompensation']}
def rows(d,key,currency=None):
 arr=[];tags=TAGS[key]
 if key=='net' and int(d['cik']) in [1780312,1837240,1844452]:tags=['ProfitLoss','NetIncomeLoss']
 if key=='revenue' and int(d['cik'])==753308:tags=['RegulatedAndUnregulatedOperatingRevenue']+REVTAGS
 if key=='revenue' and int(d['cik'])==1692819:tags=['Revenues']+REVTAGS
 for ns in ['dei','us-gaap','ifrs-full']+[n for n in d['facts'] if n not in ['dei','us-gaap','ifrs-full']]:
  for pri,tag in enumerate(tags):
   for unit,xs in d['facts'].get(ns,{}).get(tag,{}).get('units',{}).items():
    for x in xs:
     if x.get('filed','9999')>ASOF or x['end']>ASOF:continue
     if currency and unit!=currency:continue
     z=dict(x,unit=unit,tag=ns+':'+tag,priority=pri);arr.append(z)
 if not arr:return []
 if currency is None:
  # Choose native reporting currency with most recent observation, preferring USD only on tied dates.
  if key in ['shares']:unit='shares'
  elif key=='eps':unit=max(arr,key=lambda x:(x['end'],x['filed'],x['unit']=='USD/shares'))['unit']
  else:unit=max(arr,key=lambda x:(x['end'],x['filed'],x['unit']=='USD'))['unit']
  arr=[x for x in arr if x['unit']==unit]
 dedup={}
 for x in arr:
  k=(x.get('start'),x['end']);p=dedup.get(k)
  if p is None or (x['filed'],-x['priority'])>(p['filed'],-p['priority']):dedup[k]=x
 return list(dedup.values())
def flow(d,key,currency=None):
 xs=[x for x in rows(d,key,currency) if x.get('start')];qs=[]
 for x in xs:
  days=(day(x['end'])-day(x['start'])).days+1
  if 60<=days<=115:qs.append(dict(x,derived=False))
  elif 140<=days<=400:
   prev=[z for z in xs if z['start']==x['start'] and 60<=(day(x['end'])-day(z['end'])).days<=115]
   if prev:
    p=max(prev,key=lambda z:z['end']);q=dict(x,start=(day(p['end'])+datetime.timedelta(days=1)).isoformat(),val=x['val']-p['val'],derived=True);qs.append(q)
 quarter=max(qs,key=lambda x:(x['end'],not x['derived'],x['filed'])) if qs else None
 annuals=[x for x in xs if 330<=(day(x['end'])-day(x['start'])).days+1<=400];annual=max(annuals,key=lambda x:x['end']) if annuals else None
 ttm=None
 if annual:
  later=[x for x in xs if x['end']>annual['end'] and 0<(day(x['start'])-day(annual['end'])).days<=15 and 60<=(day(x['end'])-day(x['start'])).days<=320]
  if later:
   ytd=max(later,key=lambda x:(x['end'],(day(x['end'])-day(x['start'])).days))
   prev=[x for x in xs if abs((day(ytd['end'])-day(x['end'])).days-365)<=15 and abs((day(ytd['end'])-day(ytd['start'])).days-(day(x['end'])-day(x['start'])).days)<=15]
   if prev:
    p=min(prev,key=lambda x:abs((day(ytd['end'])-day(x['end'])).days-365));ttm=dict(ytd,val=annual['val']+ytd['val']-p['val'],start=(day(ytd['end'])-datetime.timedelta(days=364)).isoformat(),method='FY + YTD − önceki YTD',components=[annual,p,ytd])
  else:ttm=dict(annual,method='Son mali yıl',components=[annual])
 if not ttm and quarter:
  ordered=sorted(qs,key=lambda x:(x['end'],x['derived']));uniq={}
  for x in ordered:
   if x['end'] not in uniq or not x['derived']:uniq[x['end']]=x
  last=sorted(uniq.values(),key=lambda x:x['end'])[-4:]
  if len(last)==4 and all(abs((day(last[i]['start'])-day(last[i-1]['end'])).days-1)<8 for i in range(1,4)):
   ttm=dict(last[-1],start=last[0]['start'],val=sum(x['val'] for x in last),method='Son dört çeyrek',components=last)
 yoy=None;prior=None
 if quarter:
  candidates=[x for x in qs if abs((day(quarter['end'])-day(x['end'])).days-365)<=15]
  if candidates:
   prior=min(candidates,key=lambda x:(abs((day(quarter['end'])-day(x['end'])).days-365),x['derived']))
   if prior['val']>0:yoy=(quarter['val']/prior['val']-1)*100
 latestPeriod=max(xs,key=lambda x:(x['end'],(day(x['end'])-day(x['start'])).days)) if xs else None
 return dict(quarter=quarter,ttm=ttm,annual=annual,yoy=yoy,prior=prior,latestPeriod=latestPeriod)
def instant(d,key,currency=None,end=None):
 xs=[x for x in rows(d,key,currency) if not x.get('start') and (end is None or x['end']<=end)]
 return max(xs,key=lambda x:(x['end'],x['filed'])) if xs else None
def rsi(cs,n=14):
 if len(cs)<n+1:return None
 changes=[cs[i]-cs[i-1] for i in range(1,len(cs))];gain=sum(max(v,0) for v in changes[:n])/n;loss=sum(max(-v,0) for v in changes[:n])/n
 for v in changes[n:]:gain=(gain*(n-1)+max(v,0))/n;loss=(loss*(n-1)+max(-v,0))/n
 return 100 if loss==0 and gain else 50 if gain==loss==0 else 100-100/(1+gain/loss)
def technical(t,sector):
 meta,bars=chart(t);p=bars[-1]['close'];cs=[b['close'] for b in bars];acs=[b['adjusted'] for b in bars];trs=[max(b['high']-b['low'],abs(b['high']-bars[i-1]['close']),abs(b['low']-bars[i-1]['close'])) for i,b in enumerate(bars) if i>0];atr=sum(trs[:14])/14
 for v in trs[14:]:atr=(atr*13+v)/14
 ma=lambda n:sum(cs[-n:])/n if len(cs)>=n else None
 def ret(n):return (acs[-1]/acs[-n-1]-1)*100 if len(acs)>n else None
 bench={'Yarı iletkenler':'SMH','Optik ve fotonik':'QQQ','Uzay ve uydu':'UFO','Veri merkezleri':'DTCR','Enerji altyapısı':'XLU','Yapay zekâ yazılımları':'IGV','Robotik ve otomasyon':'BOTZ','Siber güvenlik':'CIBR'}[sector]
 def relative(symbol):
  _,bb=chart(symbol);lookup={b['date']:b['adjusted'] for b in bb};aligned=[b for b in bars if b['date'] in lookup]
  if len(aligned)<=63:return None
  a,z=aligned[-64],aligned[-1];return ((z['adjusted']/a['adjusted'])/(lookup[z['date']]/lookup[a['date']])-1)*100
 lows=[];highs=[]
 for i in range(max(2,len(bars)-126),len(bars)-2):
  if bars[i]['low']==min(b['low'] for b in bars[i-2:i+3]):lows.append(bars[i]['low'])
  if bars[i]['high']==max(b['high'] for b in bars[i-2:i+3]):highs.append(bars[i]['high'])
 supports=sorted(set(x for x in lows if x<p),reverse=True);resists=sorted(set(x for x in highs if x>p))
 support=supports[0] if supports else min(b['low'] for b in bars[-20:]);resistance=resists[0] if resists else None
 m50,m200=ma(50),ma(200);trend='Yükseliş' if m50 and m200 and p>m50>m200 else 'Düşüş' if m50 and m200 and p<m50<m200 else 'Karma' if m200 else 'Kısa geçmiş'
 weeks={}
 # Completed weeks only.
 current=datetime.date.fromisoformat(bars[-1]['date']).isocalendar()[:2]
 for b in bars:
  w=day(b['date']).isocalendar()[:2]
  if w!=current:weeks[w]=b['close']
 wc=list(weeks.values());w10=sum(wc[-10:])/10 if len(wc)>=10 else None;w40=sum(wc[-40:])/40 if len(wc)>=40 else None
 return dict(price=p,date=bars[-1]['date'],bars=len(bars),ma20=ma(20),ma50=m50,ma200=m200,rsi14=rsi(cs),atr14=atr,atrPct=atr/p*100,volumeRatio=bars[-1]['volume']/(sum(b['volume'] for b in bars[-21:-1])/20),return3m=ret(63),return6m=ret(126),return12m=ret(252),relativeSPY=relative('SPY'),benchmark=bench,relativeSector=relative(bench),support=support,support2=supports[1] if len(supports)>1 else min(b['low'] for b in bars[-60:]),resistance=resistance,resistance2=resists[1] if len(resists)>1 else None,breakout=max(b['high'] for b in bars[-21:-1]),trend=trend,weekly10=w10,weekly40=w40,weeklyLast=wc[-1] if wc else None,yearHigh=max(b['high'] for b in bars[-252:]),yearLow=min(b['low'] for b in bars[-252:]),history=[dict(date=b['date'],close=round(b['close'],4)) for b in bars[-252:]])
def fundamental(t):
 d=load(t,'facts'); rev=flow(d,'revenue');latest=(rev['quarter'] or rev['annual']);curr=latest['unit'] if latest else 'USD';metrics={k:flow(d,k,curr) for k in ['net','operating','gross','cost','cfo','capex','sbc']};metrics['revenue']=rev
 balances={k:instant(d,k,curr) for k in ['cash','shortInvestments','assets','liabilities','currentAssets','currentLiabilities','equity','debtTotal','debtCurrent','debtNoncurrent']}
 shares=instant(d,'shares','shares');return dict(cik=d['cik'],entity=d['entityName'],currency=curr,flows=metrics,balances=balances,shares=shares)
def build():
 companies=json.loads((OUT/'companies.json').read_text());out=[]
 for c in companies:
  try:
   x=dict(ticker=c['ticker'],technical=technical(c['ticker'],c['sector']),fundamental=fundamental(c['ticker']));out.append(x)
  except Exception as e:print('ERROR',c['ticker'],repr(e));raise
 (ROOT/'metrics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 for x in out:
  f=x['fundamental'];r=f['flows']['revenue'];cash=f['balances']['cash'];cf=f['flows']['cfo']['ttm'];cap=f['flows']['capex']['ttm'];latest=(r['quarter'] or r['annual']);print(x['ticker'],latest['end'] if latest else 'NO_REV','ttm',r['ttm']['end'] if r['ttm'] else '-', 'cash',cash['end'] if cash else '-', 'cfo',cf['end'] if cf else '-', 'capex',cap['end'] if cap else '-', 'bars',x['technical']['bars'])
if __name__=='__main__':build()
