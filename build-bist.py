from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'web';B=ROOT/'worker'
u=json.loads((ROOT/'data/bist-universe.json').read_text());fin=json.loads((ROOT/'data/bist-financials.json').read_text());biz=json.loads((ROOT/'data/bist-business.json').read_text())
summaries=json.loads((ROOT/'data/bist-summary-snapshots.json').read_text())
companies=[]
for source in u['companies']:
 c={**source};f=fin['companies'].get(c['ticker']);business=biz.get(c['ticker']);c.update(financial=f,kapSummary=summaries.get(c['ticker']),business=business,date=u['checkedAt'][:10],moat=business['business'] if business else 'KAP sınıflandırması: '+c['industry']+'. Ayrıntılı editoryal iş modeli henüz doğrulanmadı.',future='; '.join(business['drivers']) if business else 'Talep, rekabet, nakit üretimi ve yatırım ihtiyacını KAP faaliyet raporundan izle.',technicalDate=None,levels={'support':None,'support2':None,'resistance':None,'resistance2':None},nextEarnings=None,earningsSummary=None)
 c['analysis']={'financial':{'reportDate':f['period'] if f else None,'revenueGrowth':None,'ps':None,'netQuarter':None,'fcf':None}}
 companies.append(c)
catalog={**{k:v for k,v in u.items() if k!='companies'},'financialCheckedAt':fin['checkedAt'],'financialSource':fin['source'],'companies':companies,'symbols':{c['ticker']:c['tradingview'] for c in companies}}
(W/'bist-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')))
backend='\n'.join((B/f).read_text() for f in ['portfolio-tools.js','portfolio.js','portfolio-market.js'])
names=['portfolioAPI','cleanPortfolio','portfolioMarketAPI','portfolioToolsAPI','getPortfolioQuotes','userKey','pfLedger','pfAdjustment','pfTrade','pfPrices','pfEvaluateAlerts','pfObserve']
for n in names:backend=re.sub(r'\b'+n+r'\b','bist_'+n,backend)
backend=backend.replace('const portfolioHeaders=','const bistPortfolioHeaders=').replace('headers:portfolioHeaders','headers:bistPortfolioHeaders').replace('const pjson=','const bpjson=');backend=re.sub(r'\bpjson\b','bpjson',backend)
backend=backend.replace('private-portfolios/v1/','private-bist-portfolios/v1/').replace('private-quote-cache/v1/','private-bist-quote-cache/v1/').replace('private-ai-budget/v1/','private-bist-ai-budget/v1/').replace("'/api/portfolio","'/api/bist/portfolio").replace('%2Fportfoyum%2F','%2Fbist%2Fportfoyum%2F').replace('holdings.length>101','holdings.length>500').replace('En fazla 101','En fazla 500')
backend=backend.replace("encodeURIComponent(h.ticker)+'?interval", "encodeURIComponent(h.ticker+'.IS')+'?interval").replace("'USD'","'TRY'")
backend=backend.replace('P/S karşılaştırmasının tarihli ve sektör farklarına duyarlı olduğunu belirt.', 'KAP raporları altı aylık kaynak görüntüsüdür; son rapor garantisi vermez. TMS 29 ve yeniden düzenleme etkisini belirt. Bilanço önceki yıl sonuyla, gelir aynı rapordaki önceki altı ayla karşılaştırılır. Banka/sigortaya sanayi cari oranı veya borç/FAVÖK uygulama. Toplam yükümlülüğü finansal borç diye adlandırma. F/K, hedef, destek veya direnç uydurma; altı aylık veriyi yıllıklaştırma.')
backend=backend.replace('financial:c.analysis.financial','financial:c.financial,business:c.business')
backend=backend.replace('function bist_pfTrade(saved,trade,companies){', "function bist_pfTrade(saved,trade,companies){if(trade.type==='buy'&&!saved.holdings.some(h=>h.ticker===trade.ticker)&&saved.holdings.length>=500)throw Error('En fazla 500 hisse.');")
# A bounded refresh protects large portfolios: cached values remain available, missing values stay missing.
backend=backend.replace('async function bist_getPortfolioQuotes(env,holdings){return', 'async function bist_getPortfolioQuotes(env,holdings){let remaining=25;return')
backend=backend.replace("return old;try{const r=await fetch", "return old;if(remaining--<=0)return old?{...old,stale:true}:{ticker:h.ticker,price:null,currency:'TRY',source:'Yahoo Finance',stale:true,error:'Bu yenilemenin 25 sembollük sınırı; yeniden yenile.'};try{const r=await fetch")
(B/'bist-portfolio.generated.js').write_text(backend)
s=(W/'portfolio.html').read_text().replace('Portföyüm · Arda Research','BIST Portföyüm · Arda Research').replace('<body>','<body class="bist-portfolio">').replace('href="/"','href="/bist/"').replace('href="/#research"','href="/bist/#markets"').replace('href="/#current-prices"','href="/bist/#markets"').replace('href="/hakkimizda/"','href="/bist/#method"').replace('%2Fportfoyum%2F','%2Fbist%2Fportfoyum%2F').replace('USD','TL').replace('ABD','BIST').replace('KİŞİSEL ARAŞTIRMA ALANIN','BIST / TL PORTFÖYÜ').replace('Resmî takvim, yönetim rehberliği ve tarihli sonuçlar ayrı ayrı.','KAP raporları ve gelecek bilançoda izlenecekler. Tarihi doğrulanmayan olaylar kesinleştirilmez.')
s=s.replace('</head>','<link rel="stylesheet" href="/bist.css"><link rel="stylesheet" href="/market-navigation.css"></head>').replace('/portfolio-tools.js','/bist-portfolio-tools.js').replace('/portfolio.js','/bist-portfolio.js').replace('<script src="/bist-portfolio-tools.js"','<script src="/bist-core.js" defer></script><script src="/bist-portfolio-tools.js"')
s=s.replace('<script src="/bist-portfolio.js"','<script src="/portfolio-privacy.js" defer></script><script src="/bist-portfolio.js"').replace('Sağlayıcı fiyatı varsa öncelikle o kullanılır.','Sağlayıcı fiyatı varsa önce o kullanılır. Bir yenilemede en fazla 25 sembol kaynaktan sorgulanır; önbellek ve tarih bilgisi korunur.')
s=s.replace('/signout-with-chatgpt?return_to=%2F\"','/signout-with-chatgpt?return_to=%2Fbist%2F\"').replace('class=\"primary\" href=\"/signin-with-chatgpt?', 'id=\"bistSignin\" class=\"primary\" href=\"/signin-with-chatgpt?')
(W/'bist-portfolio.html').write_text(s)
js=(W/'portfolio.js').read_text().replace('/api/portfolio','/api/bist/portfolio').replace('/portfolio-catalog.json','/api/bist/catalog').replace("currency:'USD'","currency:'TRY'").replace(' USD',' TL').replace('America/New_York','Europe/Istanbul').replace("'arda-portfoyum.json'","'arda-bist-portfoyum.json'")
js=re.sub(r'/hisse/\$\{([^}]+)\}/',r'/bist/?hisse=${\1}',js)
a=js.index('function renderAnalysis(z)');b=js.index('function resetForm()',a);js=js[:a]+(W/'bist-portfolio-analysis.fragment.js').read_text()+js[b:]
js=js.replace("render();$('status').textContent='Hesabın hazır", "render();const picked=new URL(location.href).searchParams.get('hisse');if(picked&&byTicker.has(picked)){if(data.holdings.some(h=>h.ticker===picked))openEditor(picked);else{openEditor();$('ticker').value=picked;$('companySearch').value=byTicker.get(picked).name;populateCompanies();}}$('status').textContent='Hesabın hazır")
js=js.replace('window.mountArdaPrice(', 'window.mountArdaBistPrice(')
js="window.mountArdaBistPrice=(target,symbol,range)=>window.mountArdaPrice(target,symbol,range,'light');\n"+js
js=js.replace('async function api(', "const loginHisse=new URL(location.href).searchParams.get('hisse');if(loginHisse&&/^[A-Z0-9]{3,10}$/.test(loginHisse))$('bistSignin').href='/signin-with-chatgpt?return_to='+encodeURIComponent('/bist/portfoyum/?hisse='+loginHisse);\nasync function api(")
(W/'bist-portfolio.js').write_text(js)
tools=(W/'portfolio-tools.js').read_text().replace('/api/portfolio','/api/bist/portfolio').replace("currency:'USD'","currency:'TRY'").replace(' USD',' TL');tools=re.sub(r'/hisse/\$\{([^}]+)\}/',r'/bist/?hisse=${\1}',tools)
a=tools.index('function renderLevels()');b=tools.index('function renderAlarms()',a);tools=tools[:a]+"function renderLevels(){if(!state)return;const c=company($('alertTicker').value),r=c?.dailyTechnical;if(!r){$('alertLevels').textContent='Kendi TL alarm seviyeni gir. Günlük teknik kayıt yok; grafiği şirket ekranından incele.';return;}$('alertLevels').innerHTML='<span>Günlük hesap seansı: '+esc(r.asOf)+'</span>'+[['support','below','Destek'],['resistance','above','Direnç']].filter(([k])=>Number.isFinite(r[k])).map(([k,d,label])=>'<button type=\"button\" data-dt-level=\"'+r[k]+'\" data-dir=\"'+d+'\">'+label+' '+money(r[k])+'</button>').join('');$('alertLevels').querySelectorAll('[data-dt-level]').forEach(b=>b.onclick=()=>{$('alertPrice').value=b.dataset.dtLevel;$('alertDirection').value=b.dataset.dir;alertLevelDate=r.asOf;});}\n"+tools[b:]
a=tools.index('function freshness(');b=tools.index('function renderLedger()',a);tools=tools[:a]+(W/'bist-calendar.fragment.js').read_text()+tools[b:]
(W/'bist-portfolio-tools.js').write_text(tools)
print('BIST catalog:',len(companies),'companies;',len(fin['companies']),'financial snapshots;',len(biz),'business profiles')
