"""Parse explicitly downloaded public KAP summary pages for archive gaps.
The latest visible column is a standalone snapshot; never a comparable-period series.
"""
import json,re,sys,datetime,unicodedata
from pathlib import Path
from lxml import html
ROOT=Path(__file__).resolve().parents[1];u=json.loads((ROOT/'data/bist-universe.json').read_text());lookup={c['ticker']:c for c in u['companies']};result={}
labels={'Toplam Varlıklar':'assets','Toplam Özkaynaklar':'equity','Hasılat':'revenue','Net Dönem Kârı (Zararı)':'netIncome'}
for p in Path(sys.argv[1]).glob('*.html'):
 rows=[[' '.join(' '.join(c.itertext()).split()) for c in r.xpath('./td|./th')] for r in html.parse(str(p)).xpath('//tr')]
 header=next((r for r in rows if r and r[0]=='FİNANSAL DURUM TABLOSU'),None)
 if not header or not re.fullmatch(r'202[0-6]/(?:03|06|09|12)',header[-1]):continue
 unit=next(r[-1] for r in rows if r and r[0]=='Sunum Para Birimi');factor=unit.removesuffix('TL').strip().replace('.','');scale=int(factor) if factor.isdigit() else 1
 if not unit.endswith('TL'):continue
 basis=next((r[-1] for r in rows if r and r[0]=='Finansal Tablo Niteliği'),'Belirtilmedi');fields={}
 for r in rows:
  if not r or r[0] not in labels or not re.fullmatch(r'-?[\d.,]+',r[-1]):continue
  fields.setdefault(labels[r[0]],float(r[-1].replace('.','').replace(',','.'))*scale)
 if 'assets' not in fields or 'equity' not in fields:continue
 result[p.stem]={'columnPeriod':header[-1],'currency':'TRY','reportedUnit':unit,'basis':basis,'source':lookup[p.stem]['financialSource'],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fields':fields,'method':'KAP özet ekranının son sütunu; dönemler arası karşılaştırma veya büyüme hesabı yapılmaz. Gelir dönemi süresi özgün rapordan ayrıca kontrol edilmeli.'}
(ROOT/'data/bist-summary-snapshots.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
print('Standalone KAP summaries:',len(result))
