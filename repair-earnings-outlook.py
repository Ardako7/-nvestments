import json,pathlib,urllib.request,urllib.parse,lxml.html,re,concurrent.futures
P=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data');UA={'User-Agent':'Arda Research arda-research@example.com'}
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20) as r:return r.read()
def sections(text):
 matches=list(re.finditer(r'[^\n]{0,30}(?:Outlook|Guidance)[^\n]{0,90}',text,re.I));out=[]
 for m in matches:
  head=m.group()
  if any(x in head.lower() for x in ['including','respect','safe harbor','looking','updated','statements','reaffirmed']):continue
  if len(head)>120:continue
  segment=text[m.start():m.start()+2400]
  if re.search(r'\$|€|\d+%',segment) and any(w in segment.lower() for w in ['revenue','eps','margin','sales','ffo','income']):out.append(segment)
  if len(out)>=2:break
 if not out:
  for m in re.finditer(r'(?:For the (?:third|fourth|first|second) quarter|We expect (?:third|fourth|first|second).{0,30}revenue|revenue is expected)',text,re.I):out.append(text[max(0,m.start()-50):m.start()+1500]);break
 return out

def task(file):
 d=json.loads(file.read_text());t=d['ticker'];cached=P/(t+'-press.html');text=''
 try:
  if d['source']==d['filing'] or 'slides' in d['source'].lower() or not cached.exists():
   root=lxml.html.fromstring(get(d['filing']));urls=[]
   for a in root.xpath('//a[@href]'):
    trs=a.xpath('ancestor::tr[1]');txt=' '.join(trs[0].text_content().split()) if trs else a.text_content();href=a.get('href')
    if '99.1' in txt and href.lower().endswith(('.htm','.html')):urls.append(urllib.parse.urljoin(d['filing'],href))
   for url in dict.fromkeys(urls):
    if url==d['filing']:continue
    bb=get(url);rr=lxml.html.fromstring(bb);candidate='\n'.join(' '.join(e.text_content().split()) for e in rr.xpath('//div[not(div)]|//p|//tr|//h1|//h2|//h3|//li'))
    if len(candidate)>1000 and re.search(r'revenue|sales|earnings',candidate,re.I):cached.write_bytes(bb);d['source']=url;break
  if cached.exists():
   root=lxml.html.fromstring(cached.read_bytes());text='\n'.join(' '.join(e.text_content().split()) for e in root.xpath('//div[not(div)]|//p|//tr|//h1|//h2|//h3|//li'))
   if len(text)<1000:text=' '.join(root.text_content().split())
  d['sections']=sections(text);file.write_text(json.dumps(d,ensure_ascii=False));(P/(t+'-press.txt')).write_text(text);return t,len(d['sections']),d['source']
 except Exception as e:return t,'ERROR',str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for x in ex.map(task,list(P.glob('*-outlook.json'))):print(*x,flush=True)
