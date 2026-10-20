import json,pathlib
P=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data');rows='''NVDA|Mali Q3 2027|Gelir $108 milyar ±%2; GAAP ve non-GAAP brüt marj %74 ±0,5 puan.
AMD|Q3 2026|Gelir $13 milyar ±$300 milyon; non-GAAP brüt marj yaklaşık %56.
AVGO|Mali Q4 2026|Gelir yaklaşık $34,8 milyar; non-GAAP faaliyet marjı yaklaşık %66.
MRVL|Mali Q3 2027|Gelir $3,15 milyar ±%5; GAAP brüt marj %52,9–53,9, non-GAAP %57,5–58,5; GAAP EPS $0,53 ±$0,05, non-GAAP EPS $1,10 ±$0,05.
MU|Mali Q1 2027|Gelir $61,5 milyar ±$1,5 milyar; GAAP brüt marj yaklaşık %85,95, non-GAAP %86,25; GAAP EPS $37,84 ±$1,00, non-GAAP EPS $38,15 ±$1,00.
TSM|Q3 2026|Gelir rehberliği $44,6–45,8 milyar (USD).
ASML|Q3 2026|Gelir €11–12 milyar; brüt marj %55–57.
AMAT|Mali Q4 2026|Gelir $10,25 milyar ±$500 milyon; non-GAAP EPS $4,02 ±$0,20.
LRCX|27 Eylül 2026 biten çeyrek|Gelir $8,10 milyar ±$400 milyon; GAAP/non-GAAP brüt marj %52 ±1 puan; EPS $2,15 ±$0,15.
ALAB|Mali Q3 2026|Gelir $540–560 milyon; GAAP/non-GAAP brüt marj yaklaşık %72; GAAP EPS $0,87–0,92, non-GAAP EPS $1,16–1,21.
CRDO|Mali Q2 2027|Gelir $525–535 milyon; GAAP brüt marj %62,9–64,9, non-GAAP %67–69.
CBRS|Q3 2026 · Core non-GAAP|Core gelir $214–216 milyon; core brüt marj %38–40; core faaliyet marjı −%25 ila −%23. 2026 core gelir beklentisi $880–890 milyon. Bunlar GAAP gelir/kâr değildir.
LITE|Mali Q1 2027|Gelir $1,225–1,275 milyar; non-GAAP faaliyet marjı %39,5–40,5; non-GAAP EPS $4,05–4,35.
AAOI|Q3 2026|Gelir $255–290 milyon; non-GAAP brüt marj %29–30,5; non-GAAP EPS $0,11–0,26.
FN|Mali Q1 2027 · 25 Eylül 2026 biten dönem|Gelir $1,375–1,425 milyar; GAAP EPS $3,39–3,54, non-GAAP EPS $4,10–4,25.
IPGP|Q3 2026|Gelir $265–295 milyon; düzeltilmiş brüt marj %37,5–40,5; düzeltilmiş EPS $0,30–0,60.
RKLB|Q3 2026|Gelir $250–265 milyon; GAAP brüt marj %29–31, non-GAAP %35–37; düzeltilmiş EBITDA zararı $17–23 milyon.
PL|Mali Q3 2027 · 31 Ekim 2026 biten dönem|Gelir $101–105 milyon; non-GAAP brüt marj %56–58; düzeltilmiş EBITDA zararı $1–6 milyon; yatırım harcaması $30–37 milyon.
LUNR|2026 yıl geneli · çeyrek tahmini değil|Gelir $900 milyon–$1 milyar; düzeltilmiş EBITDA'nın pozitif olması hedefleniyor.
VRT|Q3 2026|Gelir $3,65–3,85 milyar; organik büyüme %34–36; düzeltilmiş faaliyet marjı %24–25; düzeltilmiş EPS $1,77–1,83.
ANET|Q3 2026|Gelir yaklaşık $3,3 milyar; non-GAAP faaliyet marjı %48–49; non-GAAP EPS $1,06–1,08.
DELL|Mali 2027 yıl geneli · çeyrek tahmini değil|Gelir rehberliği yaklaşık $192 milyar; GAAP EPS $24,37 ve non-GAAP EPS $25,50.
HPE|Mali Q4 2026|Gelir $13,9–14,8 milyar; GAAP EPS $1,12–1,22; non-GAAP EPS $1,20–1,30.
EQIX|Q3 2026|Gelir $2,525–2,575 milyar. 2026 yıl geneli AFFO/hisse $42,69–43,29; AFFO, GAAP net kâr değildir.
DLR|2026 yıl geneli · çeyrek tahmini değil|Core FFO/hisse (net promote hariç) $8,15–8,20; sabit kurla $8,10–8,15. FFO, GAAP net kâr değildir.
CEG|2026 yıl geneli · çeyrek tahmini değil|Düzeltilmiş faaliyet kazancı/hisse $11,50–12,50.
VST|2026 yıl geneli · çeyrek tahmini değil|Devam eden operasyonlarda düzeltilmiş EBITDA $6,8–7,6 milyar; düzeltilmiş FCFbG $3,925–4,725 milyar. Şirketin özel nakit tanımıdır.
ETN|2026 yıl geneli · çeyrek tahmini değil|GAAP EPS $10,36–10,56; düzeltilmiş EPS $13,40–13,60.
BE|2026 yıl geneli · çeyrek tahmini değil|Gelir rehberliği $3,9–4,2 milyar.
META|Q3 2026|Gelir $61–64 milyar. 2026 yıl geneli sermaye harcaması (finansal kira anapara ödemeleri dahil) $130–145 milyar.
PLTR|Q3 2026|Gelir $2,160–2,164 milyar; düzeltilmiş faaliyet kârı $1,292–1,296 milyar. Düzeltilmiş kâr GAAP net kâr değildir.
SNOW|Mali Q3 2027|Ürün geliri $1,588–1,593 milyar, yıllık büyüme %37–38; non-GAAP faaliyet marjı %15,5. Ürün geliri toplam gelirle aynı değildir.
TER|Q3 2026|Gelir $1,2–1,3 milyar; GAAP EPS $1,79–2,09, non-GAAP EPS $1,85–2,15.
ROK|Mali 2026 yıl geneli · çeyrek tahmini değil|Gelir orta noktası yaklaşık $9 milyar; satış büyümesi %7,5–9,5; GAAP EPS $12,72–13,02, düzeltilmiş EPS $13,00–13,30.
SYM|Mali Q4 2026|Gelir $760–780 milyon; düzeltilmiş EBITDA $100–105 milyon.
PATH|Mali Q3 2027|Gelir $440–445 milyon; 31 Ekim 2026 ARR $1,992–1,997 milyar; non-GAAP faaliyet kârı yaklaşık $100 milyon.
PANW|Mali Q1 2027|Gelir $3,300–3,310 milyar; NGS ARR $9,54–9,56 milyar; non-GAAP EPS $0,96–0,98.
ZS|Mali Q1 2027|Gelir $935–939 milyon; non-GAAP brüt marj yaklaşık %80; non-GAAP faaliyet kârı $215–217 milyon; EPS $1,15–1,16.
FTNT|Q3 2026|Gelir $2,01–2,10 milyar; non-GAAP brüt marj %79–81; non-GAAP faaliyet marjı %35–37; non-GAAP EPS $0,83–0,87.
S|Mali Q3 2027|Gelir $309–311 milyon; non-GAAP faaliyet kârı $38–40 milyon; non-GAAP EPS $0,08–0,09.
OKTA|Mali Q3 2027|Gelir $813–817 milyon; non-GAAP faaliyet marjı %24–25; non-GAAP EPS $0,92–0,94; non-GAAP FCF $175–185 milyon.
CDNS|Q3 2026|Gelir $1,595–1,625 milyar; GAAP faaliyet marjı %27,5–28,5, non-GAAP %43,5–44,5; GAAP EPS $1,11–1,17, non-GAAP $2,01–2,07.
ORCL|Mali Q2 2027|Toplam gelir büyümesi %30–34; bulut geliri büyümesi USD bazında %65–71; non-GAAP EPS USD bazında $1,85–1,93.
SMCI|Mali Q1 2027 · 30 Eylül 2026 biten dönem|Gelir $14,5–15,5 milyar; GAAP EPS $0,89–0,98; non-GAAP EPS $1,01–1,10.
MPWR|Q3 2026|Gelir $1,14–1,16 milyar; GAAP brüt marj %55,2–55,8; non-GAAP %55,4–56,0.
AMKR|Q3 2026|Gelir $1,95–2,05 milyar; brüt marj %18,5–19,5; net kâr $180–205 milyon ve EPS $0,72–0,82.'''
result={}
for line in rows.splitlines():
 t,period,text=line.split('|');r=P/(t+'-outlook.json');d=json.loads(r.read_text()) if r.exists() else {};result[t]={'period':period,'text':text,'source':d.get('source',''),'published':d.get('filingDate','2026-07-16' if t=='TSM' else '2026-07-15')}
result['TSM']['source']='https://www.sec.gov/Archives/edgar/data/1046179/000104617926000451/a2q26presentatione.htm'
result['ASML']['source']='https://www.investor.asml.com/news-releases/news-release-details/q2-2026-financial-results'
result['BE']['source']='https://www.sec.gov/Archives/edgar/data/1664703/000162828026050150/ex991_q226financialresults.htm'
pathlib.Path('dist/earnings-guidance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('Verified guidance',len(result))
