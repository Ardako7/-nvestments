"""Normalize the official, user-facing KAP bulk financial-table HTML export.
No runtime crawl. Run with an explicitly downloaded KAP ZIP archive argument.
"""
import sys,json,re,unicodedata,zipfile,datetime
from pathlib import Path
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.replace('ı','i').replace('İ','I')) if not unicodedata.combining(c)).upper().strip()
def number(s,scale):
 s=s.strip().replace('\xa0','').replace(' ','').replace('−','-')
 if not s or not re.fullmatch(r'\(?-?[\d.,]+\)?',s):return None
 negative=s.startswith('(');s=s.strip('()').replace('.','').replace(',','.')
 try:return float(s)*scale*(-1 if negative else 1)
 except ValueError:return None
FIELDS={
 'assets':['TOPLAM VARLIKLAR','VARLIKLAR TOPLAMI','AKTİF TOPLAMI'],
 'equity':['TOPLAM ÖZKAYNAKLAR','ÖZKAYNAKLAR','ÖZSERMAYE TOPLAMI'],
 'liabilities':['TOPLAM YÜKÜMLÜLÜKLER'],
 'currentAssets':['TOPLAM DÖNEN VARLIKLAR','CARİ VARLIKLAR TOPLAMI'],
 'currentLiabilities':['TOPLAM KISA VADELİ YÜKÜMLÜLÜKLER','KISA VADELİ YÜKÜMLÜLÜKLER TOPLAMI'],
 'cash':['Nakit ve Nakit Benzerleri'],
 'revenue':['Hasılat'],
 'grossProfit':['BRÜT KAR (ZARAR)'],
 'operatingProfit':['ESAS FAALİYET KARI (ZARARI)'],
 'netIncome':['DÖNEM KARI (ZARARI)','DÖNEM NET KARI VEYA ZARARI','DÖNEM NET KARI (ZARARI)'],
 'parentNetIncome':['Ana Ortaklık Payları'],
 'operatingCashFlow':['İŞLETME FAALİYETLERİNDEN NAKİT AKIŞLARI'],
 'monetaryGain':['Net Parasal Pozisyon Kazançları (Kayıpları)'],
 'interestIncome':['FAİZ GELİRLERİ'],
}
LOOK={norm(label):key for key,labels in FIELDS.items() for label in labels}
z=zipfile.ZipFile(sys.argv[1]);universe=json.loads((ROOT/'data/bist-universe.json').read_text());allowed={c['ticker'] for c in universe['companies']};candidates={}
for n in z.namelist():
 m=re.fullmatch(r'([A-Z0-9-]+)_(\d+)_2026_2\.xls',n)
 if not m:continue
 tickers=set(m[1].split('-'))&allowed
 if not tickers:continue
 raw=z.read(n);doc=html.fromstring(raw)
 rows=[[' '.join(' '.join(c.itertext()).split()) for c in r.xpath('./td|./th')] for r in doc.xpath('//tr')]
 units=next((r[1] for r in rows if len(r)==2 and r[0]=='Sunum Para Birimi'),'')
 basis=next((r[1] for r in rows if len(r)==2 and r[0]=='Finansal Tablo Niteliği'),'')
 if not units.endswith('TL'):continue
 factor=units.removesuffix('TL').strip().replace('.','');scale=int(factor) if factor.isdigit() else 1
 vals={};found={};unknown=[]
 for r in rows:
  if len(r)<5 or r[0]!='':continue
  key=LOOK.get(norm(r[1]))
  if not key or key in vals:continue
  # Bank balance sheets have TRY, FX, TOTAL for each period. Use TOTAL.
  ci,pi=(5,8) if len(r)==9 else (3,4)
  cur,prior=number(r[ci],scale),number(r[pi],scale)
  if cur is None:continue
  # Parent-share row must belong to the income statement (before OCI), not balance sheet.
  if key in ['parentNetIncome','netIncome','revenue','interestIncome','grossProfit','operatingProfit','monetaryGain'] and len(r)!=7:continue
  vals[key]={'current':cur,'previous':prior};found[key]=r[1]
  if len(r)==7:vals[key].update(quarter=number(r[5],scale),previousQuarter=number(r[6],scale))
 if vals.get('assets') and vals.get('equity') and 'liabilities' not in vals:
  vals['liabilities']={k:vals['assets'][k]-vals['equity'][k] if vals['assets'][k] is not None and vals['equity'][k] is not None else None for k in ['current','previous']};found['liabilities']='Toplam varlıklar − toplam özkaynaklar (hesaplanan)'
 r={'period':'2026-06-30','incomePeriod':'2026-01-01 / 2026-06-30','priorBalanceDate':'2025-12-31','priorIncomePeriod':'2025-01-01 / 2025-06-30','currency':'TRY','reportedUnit':units,'scale':scale,'basis':basis,'disclosureId':m[2],'source':'https://www.kap.org.tr/tr/Bildirim/'+m[2],'fields':vals,'labels':found}
 score=(basis=='Konsolide',int(m[2]))
 for ticker in tickers:
  if ticker not in candidates or score>candidates[ticker][0]:candidates[ticker]=(score,r)
result={'source':'https://www.kap.org.tr/tr/api/financialTable/download/2026/2','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'period':'2026-06-30','method':'KAP toplu mali tablo arşivi; varsa konsolide rapor; özgün sunum birimi TL’ye normalize edilir. Gelir karşılaştırması aynı rapordaki önceki yılın 6 aylık dönemiyle; bilanço karşılaştırması 31.12.2025 ile.','companies':{t:r for t,(_,r) in candidates.items()}}
(ROOT/'data/bist-financials.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
print('Reports:',len(candidates),'of',len(allowed));print('Core asset/equity:',sum('assets'in r['fields'] and 'equity'in r['fields'] for _,r in candidates.values()));print('Missing:',sorted(allowed-set(candidates)))
