import json, pathlib, urllib.request, concurrent.futures, time
P=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data')
T='INTC QCOM ADI ON NXPI MCHP RMBS LSCC FORM ACLS VECO POWI SITM KEYS VIAV LASR OUST BKSY SPIR VSAT NTAP WDC STX P APLD PWR HUBB BWXT EMR TENB DDOG MDB CRM CGNX ZBRA NET'.split()
UA={'User-Agent':'Arda Research contact research@example.com'}
def get(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30) as r:return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(1)
tickers=json.loads((P/'tickers.json').read_text());lookup={x['ticker']:x for x in tickers.values()}
def task(t):
 try:
  if t not in lookup:return t,'NO SEC TICKER'
  cik=lookup[t]['cik_str']
  for kind,url in [('chart',f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=2y&interval=1d'),('facts',f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'),('submissions',f'https://data.sec.gov/submissions/CIK{cik:010d}.json')]:
   f=P/(t+'-'+kind+'.json')
   if not f.exists():f.write_bytes(get(url))
  sub=json.loads((P/(t+'-submissions.json')).read_text());r=sub['filings']['recent'];is_=[i for i,form in enumerate(r['form']) if form in ['10-Q','10-K','20-F'] and r['filingDate'][i]<='2026-10-13'];i=is_[0];acc=r['accessionNumber'][i];url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-","")}/{r["primaryDocument"][i]}'
  f=P/(t+'-latest.html')
  if not f.exists():f.write_bytes(get(url))
  (P/(t+'-filing-meta.json')).write_text(json.dumps(dict(url=url,accn=acc,form=r['form'][i],date=r['filingDate'][i],reportDate=r['reportDate'][i])))
  return t,r['reportDate'][i]
 except Exception as e:return t,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for result in pool.map(task,T):print(*result,flush=True)
