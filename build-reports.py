import json,math,pathlib,importlib.util,statistics,subprocess
ROOT=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data');OUT=pathlib.Path('dist');spec=importlib.util.spec_from_file_location('calc','scripts/analyze-data.py');calc=importlib.util.module_from_spec(spec);spec.loader.exec_module(calc)
original=json.loads(subprocess.check_output(['git','show','702f044e3a35c6a78b74889b0bb4faea95b239dc:dist/companies.json']));original+=json.loads((OUT/'extra-seeds.json').read_text());original+=json.loads((OUT/'expansion-seeds.json').read_text());allmetrics={x['ticker']:x for x in json.loads((ROOT/'metrics.json').read_text())};quotes=json.loads((ROOT/'quotes.json').read_text())
growth={'NVDA':25,'AMD':25,'AVGO':20,'MRVL':25,'MU':15,'TSM':18,'ASML':10,'AMAT':10,'KLAC':10,'LRCX':12,'ALAB':30,'NVTS':15,'CRDO':30,'CBRS':35,'COHR':20,'LITE':25,'AAOI':25,'FN':15,'CIEN':15,'IPGP':5,'GLW':12,'RKLB':25,'ASTS':50,'IRDM':5,'PL':15,'RDW':20,'LUNR':25,'VRT':20,'ANET':20,'DELL':12,'HPE':8,'EQIX':8,'DLR':8,'CEG':8,'VST':8,'ETN':10,'GEV':12,'NEE':7,'BE':25,'MSFT':15,'GOOGL':12,'AMZN':15,'PLTR':30,'NOW':18,'SNOW':20,'ISRG':12,'TER':10,'ROK':7,'SYM':20,'TSLA':12,'PATH':10,'CRWD':20,'PANW':15,'ZS':18,'FTNT':12,'S':18,'OKTA':10}
growth.update({'SNPS':15,'CDNS':15,'META':12,'ORCL':20,'SMCI':18,'MPWR':15,'AMKR':10,'CRWV':35})
growth.update({t:10 for t in 'INTC QCOM ADI ON NXPI MCHP RMBS LSCC FORM ACLS VECO POWI SITM KEYS VIAV LASR OUST BKSY SPIR VSAT NTAP WDC STX P APLD PWR HUBB BWXT EMR TENB DDOG MDB CRM CGNX ZBRA NET'.split()});growth.update({'OUST':25,'BKSY':20,'SPIR':20,'APLD':25,'DDOG':20,'MDB':18,'NET':20,'OKLO':0,'SMR':0})
AI={'IPGP':'Dolaylı · endüstriyel üretim','ISRG':'Dolaylı · cerrahi robotik','TSLA':'AI / robotik seçenekleri · ana faaliyet araç ve enerji','PATH':'Doğrudan · dijital otomasyon','ASTS':'Dolaylı · uydu bağlantısı','IRDM':'Dolaylı · uydu iletişimi','RKLB':'Dolaylı · uzay altyapısı','RDW':'Dolaylı · uzay / görev sistemleri','LUNR':'Dolaylı · uzay görevleri','PL':'AI destekli · görüntü verisi'}
EURUSD=json.loads((ROOT/'EURUSD=X-fx.json').read_text())['chart']['result'][0]['meta']['regularMarketPrice'];USDTWD=json.loads((ROOT/'TWD=X-fx.json').read_text())['chart']['result'][0]['meta']['regularMarketPrice']
def money(v,cur='USD'):
 if v is None:return 'Uygulanamaz'
 sign='−' if v<0 else '';a=abs(v);unit='milyar' if a>=1e9 else 'milyon' if a>=1e6 else '';n=a/(1e9 if a>=1e9 else 1e6 if a>=1e6 else 1);return f'{sign}{n:,.2f} {unit} {cur}'.replace(',',' ')
def usd(v):return f'${v:,.2f}'.replace(',',' ')
def pct(v):return f'{v:+.1f}%' if v is not None else 'Kısa geçmiş: hesaplanamaz'
def val(x):return x['val'] if x else None
def rate(x):return 1 if x=='USD' else EURUSD if x=='EUR' else 1/USDTWD if x=='TWD' else None
def flowValue(f,key,period):return f['flows'][key].get(period)
def latestMatching(f,key,start,end):
 d=calc.load(f['_ticker'],'facts');xs=[x for x in calc.rows(d,key,f['currency']) if x.get('start')==start and x['end']==end]
 return max(xs,key=lambda x:x['filed']) if xs else None
reports=[]
for old in original:
 c=dict(old);t=c['ticker'];m=allmetrics[t];a=m['technical'];f=m['fundamental'];f['_ticker']=t;cur=f['currency'];p=a['price'];atr=a['atr14'];q=quotes[t];rev=f['flows']['revenue'];rq=rev['quarter'];rttm=rev['ttm'];reportDate=rq['end'];c['date']=a['date'];c['price']=round(p,2);c['horizon']='1–3 ay teknik / 3 yıl temel';c['trend']=a['trend'];c['status']='Analiz hazır';c['revision']='2026-10-13-r4'
 ai=AI.get(t, 'Dolaylı · elektrik altyapısı' if c['sector']=='Enerji altyapısı' else 'Altyapı · AI kapasitesini destekler' if c['sector'] in ['Yarı iletkenler','Optik ve fotonik','Veri merkezleri'] else 'Doğrudan · AI yazılımı / güvenlik' if c['sector'] in ['Yapay zekâ yazılımları','Siber güvenlik'] else 'AI destekli · otomasyon')
 c['business']=old['business']+'\nAI bağlantısı: '+ai+'. Saf AI gelir oranı raporda ayrı açıklanmıyorsa toplam şirket gelirine eşit kabul edilmez.'
 risk=old['moat'].split('Tezi zayıflatabilecek risk: ')[-1];future=old['future'].split('\n')[0].replace('Potansiyel tez (yorum): ','')
 c['future']='Gelecek tezi (analiz yorumu): '+future+'\nÜrün kalıcılığı: mevcut ürünü sabit kabul etmek yerine yeni nesil ürünlerin müşteri verimliliği, birim maliyet ve entegrasyon avantajını koruması gerekiyor.\nDemode kalma / ikame riski: '+risk
 c['moat']=old['moat'].replace('İncelenecek avantaj: ','Avantaj tezi (yorum): ')
 netq=f['flows']['net']['quarter'];opq=f['flows']['operating']['quarter'];
 if netq and netq['end']!=reportDate:netq=None
 if opq and opq['end']!=reportDate:opq=None
 grossq=f['flows']['gross']['quarter'];costq=f['flows']['cost']['quarter'];netMargin=val(netq)/rq['val']*100 if netq and netq['end']==reportDate else None;opMargin=val(opq)/rq['val']*100 if opq and opq['end']==reportDate else None
 grossMargin=val(grossq)/rq['val']*100 if grossq and grossq['end']==reportDate else (1-val(costq)/rq['val'])*100 if costq and costq['end']==reportDate else None
 # Comparable cash flow period, never subtract a stale capex year from current CFO.
 cf=f['flows']['cfo']['latestPeriod'];cap=latestMatching(f,'capex',cf['start'],cf['end']) if cf else None;specialInvestment=None
 if t=='NEE':
  data=calc.load(t,'facts');x=data['facts'].get('nee',{}).get('CapitalExpendituresIndependentPowerInvestmentsAndNuclearFuelPurchases',{}).get('units',{}).get('USD',[]);z=[x for x in x if x.get('start')==cf['start'] and x['end']==cf['end']];specialInvestment=max(z,key=lambda x:x['filed']) if z else None
 fcfttm=None;cft=f['flows']['cfo']['ttm'];capt=f['flows']['capex']['ttm']
 if cft and capt and cft['end']==capt['end'] and cft['start']==capt['start']:fcfttm=cft['val']-capt['val']
 fcf=cf['val']-cap['val'] if cf and cap else None
 cash=f['balances']['cash'];short=f['balances']['shortInvestments'];balanceDate=cash['end'] if cash else reportDate;data=calc.load(t,'facts');dc=calc.instant(data,'debtCurrent',cur,balanceDate);dn=calc.instant(data,'debtNoncurrent',cur,balanceDate);dt=calc.instant(data,'debtTotal',cur,balanceDate)
 # Display each disclosed balance and its period, do not silently infer missing debt as zero.
 debtLines=[]
 if dn and dn['end']==balanceDate:debtLines.append('Uzun vadeli borç: '+money(dn['val'],cur))
 if dc and dc['end']==balanceDate:debtLines.append('Kısa vadeli borç / cari borç kalemi: '+money(dc['val'],cur))
 if not debtLines and dt and dt['end']==balanceDate:debtLines.append('Raporlanan uzun vadeli borç (tag tanımı): '+money(dt['val'],cur))
 if not debtLines:debtLines.append('Borç kapsamı: cari finansal borç toplamı tek standart tag ile açıklanmıyor; toplam yükümlülük aşağıda gösteriliyor ve nakit varlığından borçsuzluk sonucu çıkarılmıyor.')
 shares=f['shares'];computed=p*shares['val']/(5 if t=='TSM' else 1) if shares else None;capvalue=q['marketCap'];capNote='Piyasa değeri: fiyat sağlayıcısı; pay sınıfları nedeniyle rapor tarihindeki pay sayısıyla birebir aynı olmayabilir.'
 if t in ['TSM','KLAC'] and computed:
  capvalue=computed;capNote='Piyasa değeri yeniden hesaplandı: kapanış × SEC raporlanan pay sayısı'+(' ÷ 5 (ADR oranı).' if t=='TSM' else '. Bölünme sonrası pay adedi kullanıldı.')
 if t in ['SYM','ASTS','LUNR']:capNote+=' Up-C / birden fazla pay sınıfı nedeniyle bu değer üzerinden konsolide P/S veya P/E çıkarılmadı.'
 revUSD=rttm['val']*rate(cur) if rttm and rate(cur) else None;ps=capvalue/revUSD if revUSD and capvalue and t not in ['SYM','ASTS','LUNR'] else None
 nett=f['flows']['net']['ttm'];pe=capvalue/(nett['val']*rate(cur)) if nett and nett['val']>0 and capvalue and rate(cur) and t not in ['SYM','ASTS','LUNR','EQIX','DLR'] and nett['end']==reportDate else None
 valuation=f'Piyasa değeri: {money(capvalue)}. {capNote}'
 if ps:valuation+=f'\nP/S (piyasa değeri / TTM gelir): {ps:.1f}×. '
 if ps and ps>20:valuation+='Çok yüksek gelir çarpanı; büyümenin kâra ve nakde dönüşmesi kritik.'
 elif ps and ps>10:valuation+='Yüksek gelir çarpanı; büyüme yavaşlamasına duyarlı.'
 elif ps:valuation+='Tek başına ucuzluk ölçüsü değildir; sektör marjı, döngü ve yatırım ihtiyacıyla birlikte okunmalı.'
 if pe:valuation+=f'\nP/E (piyasa değeri / raporlanan TTM net kâr): {pe:.1f}×; tek seferlik gelir ve giderler ayıklanmamıştır.'
 elif nett and nett['val']<=0:valuation+='\nTTM net sonuç negatif: P/E ekonomik olarak anlamlı değil.'
 if t=='EQIX':valuation+='\nREIT için gelir çarpanı yerine AFFO/hisse önemlidir. Şirketin 2026 AFFO/hisse beklentisi $42.69–43.29; kapanış / beklenti orta noktası '+f'{p/42.99:.1f}×. Bu GAAP kâr değildir.'
 if t=='DLR':valuation+='\nREIT değerlendirmesi: Q2 2026 Core FFO/hisse $2.13 (Q2 2025 $1.87). Tek çeyrek yıllık kâr gibi kabul edilmedi; kira, borç ve geliştirme yatırımları birlikte izlenmeli.'
 if cur!='USD':valuation+=f'\nDönüşüm yalnız değerleme karşılaştırmasında referans kurla yapıldı: EUR/USD {EURUSD:.4f}; USD/TWD {USDTWD:.3f}. Rapor kalemleri kendi para biriminde gösterildi; kur sabit varsayılmaz.'
 financial=[f'Rapor dönemi: {reportDate} · Kaynak: SEC / şirketin çeyrek finansal tabloları.',f'Çeyrek gelir: {money(rq["val"],cur)} · yıllık değişim: {pct(rev["yoy"])}.',f'TTM gelir: {money(rttm["val"],cur)} ({rttm["method"]}, dönem sonu {rttm["end"]}).' if rttm else f'TTM yerine son raporlanan dönem: {money(rev["latestPeriod"]["val"],cur)}, {rev["latestPeriod"]["start"]}–{rev["latestPeriod"]["end"]}. Eksik dört çeyrekten TTM üretilmedi.',f'Çeyrek net sonuç: {money(val(netq),cur)}'+(f' · net sonuç / gelir: %{netMargin:.1f}.' if netMargin is not None else '.'),(f'Faaliyet sonucu: {money(val(opq),cur)} · faaliyet marjı: %{opMargin:.1f}.' if opq and opMargin is not None else 'Güncel faaliyet sonucu: ayrı, karşılaştırılabilir bir kalem olarak bu veri setinde doğrulanmadı; geçmiş dönemin tutarı güncel kâr gibi kullanılmadı. Net sonuç ve nakit akışı esas alındı.'),f'Brüt marj: %{grossMargin:.1f}.' if grossMargin is not None else 'Brüt marj: gelir ve maliyetler bu raporda tek karşılaştırılabilir brüt kâr kalemi altında sunulmuyor; faaliyet sonucu kullanıldı.',f'Nakit: {money(val(cash),cur)} · bilanço tarihi {balanceDate}.'+(' Kısıtlı nakit içerir; tamamı serbestçe kullanılabilir kabul edilmedi.' if cash and 'Restricted' in cash['tag'] else ''),*debtLines]
 if short and short['end']==balanceDate:financial.append('Kısa vadeli yatırımlar (nakit dışında): '+money(short['val'],cur)+'.')
 liab=f['balances']['liabilities'];asset=f['balances']['assets']
 if liab:financial.append(f'Toplam yükümlülük: {money(liab["val"],cur)} ({liab["end"]}); tamamı faizli borç değildir.')
 if cf:financial.append(f'Faaliyet nakit akışı: {money(cf["val"],cur)} · {cf["start"]}–{cf["end"]}.')
 if cap:financial.append(f'Yatırım harcaması: {money(cap["val"],cur)} · aynı dönem. '+('Yazılım geliştirmesini de içerir.' if 'DevelopSoftware' in cap['tag'] else 'Maddi duran varlık yanında maddi olmayan varlık alımlarını da içerir.' if 'IntangibleAssets' in cap['tag'] else ''))
 if fcf is not None:financial.append(f'Hesaplanan nakit farkı (CFO − yatırım harcaması): {money(fcf,cur)}; şirketin düzeltilmiş FCF tanımıyla aynı olmayabilir.')
 elif specialInvestment:financial.append(f'Yatırım + bağımsız enerji yatırımları + nükleer yakıt nakit çıkışı: {money(specialInvestment["val"],cur)}; CFO sonrası fark {money(cf["val"]-specialInvestment["val"],cur)}. Bu geniş yatırım kalemi standart capex/FCF olarak etiketlenmedi.')
 if fcfttm is not None:financial.append(f'TTM CFO − yatırım harcaması: {money(fcfttm,cur)}.')
 sbc=f['flows']['sbc']['latestPeriod']
 if sbc:financial.append(f'Hisse bazlı ödeme: {money(sbc["val"],cur)} ({sbc["start"]}–{sbc["end"]}); nakit dışı olsa da sulanma riski taşır.')
 if shares:financial.append(f'Raporlanan pay adedi: {shares["val"]:,.0f} ({shares["end"]}); ADR ve pay sınıfı dönüşümleri ayrıca ele alındı.')
 if t=='CBRS':financial.append('GAAP gelir esas alındı; şirketin “core”/düzeltilmiş geliriyle karıştırılmadı. Kısa halka açık geçmiş nedeniyle TTM yerine H1 nakit tablosu ve son çeyrek değerlendirildi.')
 financial.append(valuation)
 financial.append('Şirkete özel izlenecek kalemler: '+old['financial'].split('Şirkete özel kontroller: ')[-1].split('\n')[0])
 c['financial']='\n'.join(financial)
 ma200=usd(a['ma200']) if a['ma200'] else f'{a["bars"]} işlem günü: 200 gün için yetersiz'
 weekly='Yükseliş' if a['weekly40'] and a['weeklyLast']>a['weekly10']>a['weekly40'] else 'Düşüş' if a['weekly40'] and a['weeklyLast']<a['weekly10']<a['weekly40'] else 'Karma' if a['weekly40'] else '40 hafta için yetersiz geçmiş'
 support=a['support'];zoneLow=max(.01,support-.25*atr);zoneHigh=support+.25*atr;breakout=a['breakout']+.1*atr
 bullish=a['trend']=='Yükseliş';entry=(zoneLow+zoneHigh)/2 if bullish else max(breakout,a['ma50'] or 0);stop=max(.01,support-.75*atr) if bullish else max(.01,entry-2*atr);riskDollar=entry-stop;res=a['resistance'];r1=res if res and res>entry else entry+2*riskDollar;r2=a['resistance2'] if a['resistance2'] and a['resistance2']>r1 else max(entry+3*riskDollar,r1+atr)
 rr=(r1-entry)/riskDollar if riskDollar>0 else None
 c['entry']=(f'{usd(zoneLow)}–{usd(zoneHigh)} destek bölgesi. Destekten tepki ve önceki günlük yüksek üzerinde kapanış teyidi; şart gerçekleşmeden otomatik alım değil.' if bullish else f'İlk izleme desteği {usd(zoneLow)}–{usd(zoneHigh)}. Mevcut {a["trend"].lower()} görünümde destekten kör alım yerine {usd(entry)} üzerinde kapanış ve hacim > son 20 gün ortalamasının 1.5× seviyesiyle güçlenme teyidi beklenir.')
 c['exit']=f'1–3 aylık teknik izleme: ilk bölge {usd(r1)}, ikinci bölge {usd(r2)}. '+('İlk bölge geçmiş fiyat direnci.' if res and res>entry else 'İlk bölge 2R risk mesafesi projeksiyonu; gözlenmiş direnç değildir.')+f' Koşullu giriş {usd(entry)} için ilk bölge getiri/risk oranı {rr:.2f}R.'+(' 2R altında: ilk direnç tek başına yeterli risk/getiri sunmuyor.' if rr<2 else '')
 c['invalidate']=f'Koşullu işlem planında fiyat geçersizliği: {usd(stop)} altında günlük kapanış. Fiyat boşluklarında işlem bu seviyeden gerçekleşmeyebilir. Temel tez bozulması: '+risk
 c['technical']=f'12 Ekim 2026 ABD seansı kapanışı: {usd(p)}. {a["bars"]} günlük bar; fiyat sağlayıcısının bölünme düzeltilmiş günlük OHLC verisi.\nGünlük görünüm: {a["trend"]}; son tamamlanmış haftalar: {weekly}.\nSMA20 {usd(a["ma20"])} · SMA50 {usd(a["ma50"])} · SMA200 {ma200}.\nRSI14 {a["rsi14"]:.1f}; '+('aşırı satım bölgesinde, tek başına dönüş sinyali değil.' if a['rsi14']<30 else 'aşırı alım bölgesinde; güçlü trendlerde kalabilir.' if a['rsi14']>70 else '30–70 aralığında.')+f'\nATR14 {usd(atr)} (%{a["atrPct"]:.1f}); yön değil günlük hareket büyüklüğü ölçüsü. Hacim: önceki 20 seans ortalamasının {a["volumeRatio"]:.2f}× seviyesi.\n3 / 6 / 12 ay düzeltilmiş fiyat getirisi: {pct(a["return3m"])} / {pct(a["return6m"])} / {pct(a["return12m"])}.\n3 ay göreli performans: SPY karşısında {pct(a["relativeSPY"])}; {a["benchmark"]} karşısında {pct(a["relativeSector"])}. Sektör ETF’i tam eşleşmeyen şirketlerde yaklaşık karşılaştırmadır.\nDestek merkezleri: {usd(a["support"])} / {usd(a["support2"])}. '+(f'Direnç merkezleri: {usd(res)}'+(f' / {usd(a["resistance2"])}.' if a['resistance2'] else '.') if res else 'Geçmiş pivotlarda mevcut fiyat üzerinde direnç yok; hedefler risk mesafesi projeksiyonları.')+f'\nSon 252 seans / mevcut geçmiş aralığı: {usd(a["yearLow"])}–{usd(a["yearHigh"])}. Pivotlar iki sonraki barla teyit edildi; seviyeler garanti değildir.'
 g=growth[t]/100;speculative=bool(netq and netq['val']<0);dil=0.03 if speculative else .01
 scenarioData={}
 for key,title,gg,compression,dd in [('bull','İyimser',g+.10,1.00,max(0,dil-.01)),('base','Ana',g,.75,dil),('bear','Olumsuz',max(-.10,g-.20),.50,dil+.04)]:
  target=p*((1+gg)/(1+dd))**3*compression;change=(target/p-1)*100
  conditions=(future+' Marj ve nakit üretimi de iyileşir; rekabet avantajı korunur.' if key=='bull' else 'Talep büyür, ancak değerleme çarpanı %25 daralır; gelir büyümesi kârlılığa dönüşmek zorundadır.' if key=='base' else risk+' Büyüme yavaşlar, finansman/sulanma artar ve çarpan yarıya iner.')
  c[key]=f'3 yıllık koşullu fiyat seviyesi: {usd(target)} ({change:+.1f}%).\nVarsayım: yıllık gelir büyümesi %{gg*100:.0f}; yıllık pay artışı %{dd*100:.0f}; terminal gelir çarpanı bugünkü düzeyin %{compression*100:.0f}’i.\nKoşul: {conditions}\nBu bir duyarlılık hesabı; analist konsensüsü veya hesaplanmış gerçekleşme olasılığı değil. Borç krizi / ürün başarısızlığı bu senaryodan daha ağır sonuç yaratabilir.'
  scenarioData[key]=dict(target=round(target,2),returnPct=round(change,1),revenueGrowthPct=round(gg*100,1),dilutionPct=round(dd*100,1),multipleRatio=compression)
 profit='Raporlanan faaliyet sonucu pozitif.' if opq and opq['val']>0 else 'Raporlanan faaliyet sonucu negatif; büyümenin kârlılığa dönüşmesi henüz kritik.' if opq else 'Faaliyet sonucu raporda ayrı bir standart kalem altında açıklanmıyor; net sonuç ve nakit akışı birlikte okundu.'
 cashComment='İlgili dönem faaliyet nakit akışı pozitif.' if cf and cf['val']>0 else 'İlgili dönem faaliyet nakit akışı negatif; sermaye ihtiyacı ve sulanma ön planda.'
 if opq and netq and netq['val']>1.5*max(opq['val'],1):profit+=' Net kâr faaliyet kârını belirgin aşıyor: faaliyet dışı / tek seferlik kalemler sürdürülebilir kâr gibi ele alınmamalı.'
 action='Destek dönüşü teyidiyle koşullu izleme.' if bullish else 'Trend teyidi beklenmeli; güçlü gelecek tezi tek başına mevcut giriş zamanını doğrulamıyor.'
 c['summary']=f'{t} / {ai}\nTemel tez: {future}\nBilanço: son çeyrek gelir {money(rq["val"],cur)}, yıllık değişim {pct(rev["yoy"])}. {profit} {cashComment}\nDeğerleme: '+(f'P/S {ps:.1f}×; yüksek beklenti riski.' if ps and ps>10 else f'P/S {ps:.1f}×; sektör ve nakit üretimiyle birlikte değerlendirilmeli.' if ps else 'Pay yapısı / dönem kapsamı nedeniyle basit çarpan yorumu yerine şirketin mali yapısı esas alındı.')+f'\nTeknik: {a["trend"]}, RSI {a["rsi14"]:.1f}, SPY karşısında 3 ay {pct(a["relativeSPY"])}. {action}\nTemel risk: {risk}\nAna senaryo {usd(scenarioData["base"]["target"])} / 3 yıl; sayısal varsayımlar senaryo kartında. Fiyatlar 12 Ekim kapanışının sabit görüntüsüdür.'
 sources=[old['sources'].split('\n')[1],f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(f["cik"]):010d}.json',f'https://finance.yahoo.com/quote/{t}/history/',f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=2y&interval=1d']
 for k in ['revenue','net','cfo','capex']:
  x=f['flows'][k]['quarter'] if k in ['revenue','net'] else f['flows'][k]['latestPeriod']
  if x:
   if x.get('source'):sources.append(x['source'])
   elif x['accn']!='manual-verified-table':sources.append(f'https://www.sec.gov/Archives/edgar/data/{int(f["cik"])}/{x["accn"].replace("-","")}/{x["accn"]}-index.html')
 if t=='EQIX':sources.append('https://www.sec.gov/Archives/edgar/data/1101239/000110123926000145/a991eqix-q226xpr.htm')
 if t=='DLR':sources.append('https://investor.digitalrealty.com/news-releases/news-release-details/digital-realty-reports-second-quarter-2026-results')
 c['sources']='\n'.join(dict.fromkeys(sources))+f'\nFiyat tarihi: 12 Ekim 2026 seans kapanışı. Bilanço dönemi: {reportDate}. Araştırma tarihi: 13 Ekim 2026.\nTeknikler OHLCV verisinden hesaplandı; gelecek, avantaj ve senaryo koşulları analiz yorumlarıdır. Kaynak kalemleri, dönemler ve formüller veri dökümünde izlenebilir.'
 c['analysis']=dict(technical=a,financial=dict(reportDate=reportDate,currency=cur,revenueQuarter=rq['val'],revenueGrowth=rev['yoy'],revenueTTM=val(rttm),netQuarter=val(netq),operatingQuarter=val(opq),grossMargin=grossMargin,operatingMargin=opMargin,netMargin=netMargin,cash=val(cash),cashDate=balanceDate,marketCap=capvalue,ps=ps,pe=pe,cfo=val(cf),capex=val(cap),fcf=fcf,cashflowPeriod=cf['start']+' / '+cf['end'] if cf else None),scenarios=scenarioData,trade=dict(entry=entry,stop=stop,target1=r1,target2=r2,rewardRisk1=rr,entryType='Destek dönüşü' if bullish else 'Kırılım teyidi'),aiConnection=ai,generatedAt='2026-10-13',snapshot='2026-10-12 ABD kapanışı',model='P3 = P0 × [(1 + gelir büyümesi) / (1 + pay artışı)]^3 × terminal gelir çarpanı / bugünkü gelir çarpanı. Temettüler, vergi, komisyon ve kur değişimi dahil değil; getiri tahmini değil duyarlılık hesabı.')
 reports.append(c)
(OUT/'companies.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));(OUT/'analysis-audit.json').write_text(json.dumps({'date':'2026-10-13','priceCutoff':'2026-10-12','currencyReference':{'EURUSD':EURUSD,'USDTWD':USDTWD},'metrics':list(allmetrics.values()),'quotes':quotes,'methodology':{'priceModel':reports[0]['analysis']['model'],'rsi':'Wilder 14','atr':'Wilder 14','support':'Son 126 seansta 5 bar pivot, 2 bar teyit','TTM':'Mali yıl + cari YTD − önceki YTD; yoksa ardışık dört çeyrek','capex':'Aynı dönem CFO eksi nakit yatırım harcaması; dönemler karıştırılmaz'}},ensure_ascii=False,indent=2))
# Legacy values hashes preserve personal edits while replacing untouched seeded profiles.
def fnv(s):
 h=2166136261
 for ch in str(s):h=((h^ord(ch))*16777619)&0xffffffff
 return h
hashes={x['ticker']:{k:fnv(v) for k,v in x.items() if k not in ['id']} for x in original}
(OUT/'legacy-hashes.json').write_text(json.dumps(hashes))
print('Completed',len(reports),'reports')
for c in reports:
 f=c['analysis']['financial'];a=c['analysis']['technical'];print(c['ticker'],'Q',f['reportDate'],'price',c['price'],'RSI',round(a['rsi14'],1),'P/S',round(f['ps'],1) if f['ps'] else '-', 'FCF',round(f['fcf']/1e6,1) if f['fcf'] is not None else 'broad investment definition','base',c['analysis']['scenarios']['base']['target'])
