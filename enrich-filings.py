from pathlib import Path
import json,re,lxml.html,datetime
P=Path('/workspace/scratch/8dcd55070d2a/research-data')
def parse(t):
 file=P/(t+'-latest.html')
 if not file.exists():return
 root=lxml.html.fromstring(file.read_bytes());meta=json.loads((P/(t+'-filing-meta.json')).read_text());d=json.loads((P/(t+'-facts.json')).read_text());contexts={};units={}
 for ns,fs in d['facts'].items():
  for v in fs.values():
   for unit,xs in v.get('units',{}).items():xs[:]=[x for x in xs if x.get('source')!=meta['url']]
 for el in root.iter():
  tag=str(el.tag).lower()
  if tag.endswith('context') and el.get('id'):
   if any(str(e.tag).lower().endswith(('explicitmember','typedmember')) for e in el.iter()):continue
   vals={str(e.tag).split(':')[-1].lower():''.join(e.itertext()).strip() for e in el.iter()}
   if str(vals.get('identifier','')).lstrip('0')!=str(int(d['cik'])):continue
   if 'instant' in vals:contexts[el.get('id')]={'end':vals['instant']}
   elif 'startdate' in vals and 'enddate' in vals:contexts[el.get('id')]={'start':vals['startdate'],'end':vals['enddate']}
  if tag.endswith('unit') and el.get('id'):
   measures=[e.text for e in el.iter() if str(e.tag).lower().endswith('measure')];parts=[x.split(':')[-1] for x in measures if x];units[el.get('id')]='/'.join(parts)
 n=0
 for el in root.iter():
  if not str(el.tag).lower().endswith('nonfraction'):continue
  context=contexts.get(el.get('contextref'));unit=units.get(el.get('unitref'));name=el.get('name','')
  if not context or not unit or ':' not in name:continue
  txt=''.join(el.itertext()).strip().replace(',','').replace('\u00a0','').replace(' ','')
  if txt in ['-','—','–']:val=0
  else:
   try:val=float(txt.strip('()'))*(10**int(el.get('scale','0')));val=-abs(val) if el.get('sign')=='-' or txt.startswith('(') else val
   except ValueError:continue
  ns,tag=name.split(':',1);f=d['facts'].setdefault(ns,{}).setdefault(tag,{'label':tag,'units':{}});xs=f['units'].setdefault(unit,[]);x=dict(context,val=val,accn=meta['accn'],form=meta['form'],filed=meta['date'],source=meta['url'])
  if not any(z.get('start')==x.get('start') and z['end']==x['end'] and z.get('source')==x['source'] for z in xs):xs.append(x);n+=1
 (P/(t+'-facts.json')).write_text(json.dumps(d));print(t,'supplemented',n)
for t in ['AAOI','GLW','EQIX','DLR','GEV','NEE','BE','SYM','CBRS']:parse(t)
