import urllib.request,urllib.parse,json,pathlib,re,concurrent.futures,lxml.html,datetime
P=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data');OUT=pathlib.Path('dist');companies=json.loads((OUT/'companies.json').read_text());UA={'User-Agent':'Arda Research contact arda-research@example.com'}
def fetch(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25) as r:return r.read()
def task(c):
 t=c['ticker'];record=P/(t+'-outlook.json')
 if record.exists():return json.loads(record.read_text())
 try:
  fact=P/(t+'-facts.json')
  if not fact.exists():return {'ticker':t,'status':'no facts yet'}
  d=json.loads(fact.read_text());cik=int(d['cik']);s=P/(t+'-submissions.json')
  if not s.exists():s.write_bytes(fetch(f'https://data.sec.gov/submissions/CIK{cik:010d}.json'))
  sub=json.loads(s.read_text());r=sub['filings']['recent'];candidates=[i for i,form in enumerate(r['form']) if form=='8-K' and '2.02' in r.get('items',['']*len(r['form']))[i] and r['filingDate'][i]<='2026-10-13']
  if not candidates:return {'ticker':t,'status':'foreign / no 2.02','source':c['sources'].split('\n')[1]}
  i=candidates[0];acc=r['accessionNumber'][i];base=f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-","")}/';filingURL=base+r['primaryDocument'][i];b=fetch(filingURL);root=lxml.html.fromstring(b);links=[]
  for a in root.xpath('//a[@href]'):
   href=a.get('href');txt=a.text_content()
   if (('99' in href.lower() or 'press' in href.lower() or 'earning' in href.lower() or 'financialres' in href.lower() or '99' in txt) and (href.lower().split('?')[0].endswith(('.htm','.html','.pdf')))):
    url=urllib.parse.urljoin(filingURL,href)
    if url not in links and url!=filingURL:links.append(url)
  text='';source=filingURL
  for u in links[:3]:
   try:
    bb=fetch(u)
    if bb[:4]==b'%PDF':
     from pypdf import PdfReader
     from io import BytesIO
     txt='\n'.join(pg.extract_text() for pg in PdfReader(BytesIO(bb)).pages)
    else:
     rr=lxml.html.fromstring(bb);txt='\n'.join(' '.join(e.text_content().split()) for e in rr.xpath('//p|//tr|//h1|//h2|//h3|//li'))
     if len(txt)<500:txt=' '.join(rr.text_content().split())
    if len(txt)>len(text) and re.search(r'outlook|guidance|expects|anticipate',txt,re.I):text=txt;source=u;(P/(t+'-press.html')).write_bytes(bb)
   except Exception:continue
  if not text:text=' '.join(root.text_content().split())
  matches=list(re.finditer(r'(?:Financial|Business|Fiscal|Quarter|Full.Year|2026|2027)[^\n.]{0,65}(?:Outlook|Guidance)|(?:Outlook|Guidance)[^\n.]{0,65}(?:Quarter|Fiscal|2026|2027)|For the (?:third|fourth|first|second) quarter[^\n.]{0,80}',text,re.I));sections=[]
  for m in matches:
   if 'safe harbor' in text[max(0,m.start()-500):m.start()].lower():continue
   excerpt=text[max(0,m.start()-60):m.start()+1800];
   if any(k in excerpt.lower() for k in ['revenue','sales','earnings','eps','ffo','margin']):sections.append(excerpt)
   if len(sections)>=3:break
  obj={'ticker':t,'filingDate':r['filingDate'][i],'source':source,'filing':filingURL,'sections':sections,'status':'collected'};record.write_text(json.dumps(obj,ensure_ascii=False));(P/(t+'-press.txt')).write_text(text);return obj
 except Exception as e:return {'ticker':t,'status':'error','error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for x in pool.map(task,companies):print(x['ticker'],x['status'],x.get('filingDate',''),len(x.get('sections',[])),flush=True)
