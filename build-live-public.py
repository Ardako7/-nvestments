import pathlib,json,re,html,subprocess
from professional_layout import refine
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'web';cs=json.loads((P/'companies.json').read_text());symbols=json.loads((P/'tradingview-symbols.json').read_text());feeds=json.loads((P/'official-rss-feeds.json').read_text());fallback=json.loads((P/'research-bulletin.json').read_text())
# Build the publication from the last verified source revision; never mutate the original dossiers.
h=(ROOT/'data/build-home-baseline.html').read_text();clean=[]
for c in cs:
 c=json.loads(json.dumps(c));c['price']=None;c['analysis']['technical']['price']=None;c['analysis']['technical']['history']=[]
 c['technical']='\n'.join(line for line in c['technical'].splitlines() if not line.startswith(('Kapanış:','Fiyat:')))
 clean.append(c)
a=h.index('const catalog=');b=h.index('const legacyHashes=',a);h=h[:a]+'const catalog='+json.dumps(clean,ensure_ascii=False,separators=(',',':'))+';\n'+h[b:]
for name,file in [('researchTools','research-tools.json'),('scannerData','scanner-data.json'),('valueChain','value-chain.json')]:
 a=h.index('const '+name+'=');b=h.index(';\n',a)
 h=h[:a]+'const '+name+'='+json.dumps(json.loads((P/file).read_text()),ensure_ascii=False,separators=(',',':'))+h[b:]
h=h.replace('a.trade.rewardRisk1.toFixed(2)','decimal(a.trade.rewardRisk1)').replace('q.score.toFixed(1)','decimal(q.score)').replace('q(c).score.toFixed(1)','decimal(q(c).score)').replace('c.ranking.reason',"(c.ranking?.reason||c.future)").replace('c.ranking.risk',"(c.ranking?.risk||c.moat)")
h=h.replace('<a href="#top10">İlk 10</a>','<a href="/ai-bulut/">AI bulutu</a><a href="#top10">İlk 10</a>',1)
h=h.replace('101 şirket','107 şirket').replace('101 hisse','107 hisse')
h=h.replace('${priceChart(x)}','${tradingViewPanel(x)}').replace('bindShare(x);', 'bindShare(x);loadLiveQuote(x);')
h=h.replace("['ABD KAPANIŞI',dollars(t.price),'12 Ekim 2026']", "['FİYAT KAYNAĞI','TradingView','Güncel fiyat paneli aşağıda']")
h=h.replace('${price(x.price)}</b>', '<a href="/hisse/${esc(x.ticker)}/">Güncel fiyat ↗</a></b>')
h=h.replace('${price(t.price)} · ${esc(t.date)}', 'Teknik rapor · ${esc(t.date)}')
h=h.replace("price(c.analysis.technical.price)+' · '+c.date", "'TradingView güncel fiyat paneli'")
h=h.replace('<a href="analysis-audit.json" download="arda-research-veri-dokumu.json">Hesaplama verilerini indir</a>', '<a href="/hakkimizda/">Kaynaklar ve hesap yöntemi</a>')
h=h.replace('<h3>Fiyat geçmişi', '<h3>Fiyat geçmişi')
# Replace direct historical quote display in the secondary quality views.
h=h.replace('Kapanış ${price(q.price)} · ${esc(q.priceDate)}', 'Teknik rapor · ${esc(q.priceDate)}')
h=h.replace('<strong>12 Ekim kapanışı</strong>','<strong>Güncel fiyat paneli</strong>')
h=h.replace('Veriler 12 Ekim 2026 ABD kapanışının sabit görüntüsüdür; canlı akış değildir.', 'Güncel fiyatlar TradingView panelinden gelir. Teknik raporlar ve senaryolar 12 Ekim 2026 araştırma görüntüsüdür; otomatik yeniden hesaplanmaz.')
market=(P/'market-panel.html').read_text()
h=h.replace('<section id="research-brief"', market+'<section id="research-brief"')
h=h.replace('<a href="#top10">İlk 10</a>','<a href="#current-prices">Fiyat ekranı</a><a href="#top10">İlk 10</a>',1)
h=h.replace('<h2>Kısa araştırma bülteni</h2>','<h2>Her gün yenilenen şirket açıklamaları</h2>')
h=h.replace('<div id="briefList" class="brief-grid"></div>', '<p id="dailyNewsStatus" class="small-note" aria-live="polite">Resmî kaynaklar kontrol ediliyor…</p><div id="dailyFeedList" class="brief-grid"></div><details style="margin-top:20px"><summary>Tarihli editoryal araştırma notları</summary><div id="briefList" class="brief-grid"></div></details>')
h=h.replace('Editoryal araştırma görüntüsü; otomatik haber veya canlı fiyat akışı değildir. İleri tarihli raporlar henüz gerçekleşmiş sonuçlar olarak sunulmaz.', 'Günlük bölüm on resmî şirket kaynağını tarar; kaynak başlıkları orijinal dilindedir. Editoryal notlar kendi tarihlerini korur. Kaynaklar alınamazsa son başarılı bülten korunur; gelecek olaylar gerçekleşmiş gibi sunulmaz.')
h=h.replace('</style>',(P/'market-panel.css').read_text()+'</style>')
live=(P/'price-widget.js').read_text()+'\n'+(P/'live-public.js').read_text().replace('LIVE_SYMBOLS_PLACEHOLDER',json.dumps(symbols));h=h.replace('initResearch();initTools();renderRanking();render();initPublic();',live+'\ninitResearch();initTools();renderRanking();render();initPublic();initMarket();refreshDailyNews();if(typeof setInterval!==\'undefined\')setInterval(refreshDailyNews,900000);')
h=refine(h)
h=h.replace('<a href="/hakkimizda/">Hakkımızda</a>', '<a href="/hakkimizda/">Hakkımızda</a><a href="/portfoyum/">Portföyüm ↗</a>',1)
h=h.replace('</nav>', '<a class="asset-switch-link" href="/kripto/">Kripto ↔</a></nav>',1)
(P/'public-index.html').write_text(h)
assets={'/price-widget.js':[(P/'price-widget.js').read_text(),'text/javascript; charset=utf-8'],'/index.html':[h,'text/html; charset=utf-8'],'/site-reader.css':[(P/'site-reader.css').read_text()+(P/'market-panel.css').read_text()+(P/'professional-layout.css').read_text(),'text/css; charset=utf-8']}
assets['/ai-bulut/index.html']=[(P/'ai-bulut/index.html').read_text(),'text/html; charset=utf-8']
for c in cs:
 t=c['ticker'];page=(P/'hisse'/t/'index.html').read_text();symbol=symbols[t];cfg={'symbol':symbol,'width':'100%','locale':'tr','colorTheme':'dark','isTransparent':True}
 widget='<article class="card standalone-live"><div class="market-company-header"><div><div class="label" style="margin-bottom:10px">GÜNCEL FİYAT / TRADINGVIEW</div><h3>'+t+' <span>Fiyat ve grafik</span></h3></div><a class="market-analysis-link" href="https://www.tradingview.com/symbols/'+symbol.replace(':','-')+'/" target="_blank" rel="noopener">Tam ekran ↗</a></div><div class="detail-quote-ranges" role="group" aria-label="Fiyat grafiği aralığı">'+''.join('<button data-price-range="'+r+'" aria-pressed="'+str(r=='3M').lower()+'">'+label+'</button>' for r,label in [('1D','1 gün'),('1M','1 ay'),('3M','3 ay'),('12M','1 yıl')])+'</div><div id="readerPrice" class="market-widget"></div><div id="readerDates"></div><p class="market-disclosure">Fiyat sağlayıcıdan yenilenir; veri gecikmeli olabilir. Rapor ve teknik seviyeler araştırma tarihine aittir.</p></article><script src="/price-widget.js"></script><script type="text/javascript">const stockSymbol='+json.dumps(symbol)+';window.mountArdaPrice(document.getElementById("readerPrice"),stockSymbol,"3M");document.querySelectorAll("[data-price-range]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-price-range]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));window.mountArdaPrice(document.getElementById("readerPrice"),stockSymbol,b.dataset.priceRange)});</script>'
 widget=widget.rsplit('</script>',1)[0]+'document.getElementById("readerDates").innerHTML=window.ardaReportDateStrip('+json.dumps({'date':c['date'],'analysis':{'technical':{'date':c['analysis']['technical']['date']},'financial':{'reportDate':c['analysis']['financial']['reportDate']}}})+');</script>'
 page=re.sub(r'<div class="card"><div class="label">12 EKİM 2026 KAPANIŞI</div>.*?</div>', '<div class="card"><div class="label">FİYAT KAYNAĞI</div><strong>TradingView</strong><p>Güncel fiyat paneli yukarıda.</p></div>',page,count=1,flags=re.S)
 page=page.replace('</nav>', '<a href="/kripto/">Kripto ↔</a></nav>',1)
 page=page.replace('<div class="reader-metrics">',widget+'<div class="reader-metrics">')
 page=re.sub(r'Kapanış: \$[^\n<]+\n','',page)
 assets['/hisse/'+t+'/index.html']=[page,'text/html; charset=utf-8']
about=(P/'hakkimizda/index.html').read_text().replace('Fiyatlar 12 Ekim 2026 kapanışının sabit görüntüsüdür; canlı veya otomatik güncellenen akış yoktur.', 'Güncel fiyat gösterimi TradingView panelleri üzerinden sağlanır; veri gecikmeli olabilir. Teknik raporlar, senaryolar ve puanlar 12 Ekim 2026 araştırma görüntüsüdür; güncel fiyat paneli bunları yeniden hesaplamaz.').replace('Fiyat ve OHLCV kaynağı Yahoo Finance\'tır.', 'Teknik araştırmanın tarihli hesap girdileri Yahoo Finance kaynağındandır; ham fiyat geçmişi halka açık dosya olarak sunulmaz.').replace('Halka açık fiyat gösterimi için veri sağlayıcısının yeniden dağıtım izinleri ayrıca sağlanmalıdır.', 'Güncel fiyatlar doğrudan TradingView’in halka açık gömme panelleriyle gösterilir ve sağlayıcı atfı korunur.').replace('İletişim veya hata bildirimi için şu an bu sohbet kullanılabilir;', 'Bu sürümde iletişim formu bulunmaz;')
about=about.replace('Bülten açıklama ve etkinlik tarihlerini ayırır.', 'Günlük kaynak bülteni on resmî RSS akışından alınır ve İstanbul takvim gününe göre yenilenir. Başlıklar kaynağın orijinal dilindedir; otomatik Türkçe özetleme iddiası yoktur. Kaynak hatasında eski başarılı içerik korunur. Tarihli editoryal notlar açıklama ve etkinlik tarihlerini ayırır.').replace('Halka açık sürümde finansal içerik çerçevesi ve veri kullanım izinleri ayrıca incelenir.', 'İçerik kaynaklı genel araştırma ve koşullu yorum olarak sunulur; kişiye özel danışmanlık değildir.')
about=about.replace('Bu sürüm bunları sunucuya göndermez', 'Eski tarayıcı araçları bunları sunucuya göndermez')
about=about.replace('Cihazlar arasında otomatik eşitleme yoktur;', 'Eski tarayıcı araçlarında cihazlar arasında otomatik eşitleme yoktur;')
about=about.replace('<p class="reader-terms">', '<article class="card reader-section"><h2>Hesaba bağlı portföy</h2><p>Portföyüm sayfasında ChatGPT ile giriş yapılır. Kullanıcı adı, hisse adedi, maliyet ve girilen fiyatlar kimliği doğrulanmış hesabına özel sunucu kaydında tutulur; başka ziyaretçilere sunulmaz. Aynı hesapla farklı cihazlardan erişilebilir. Kayıtlarını sayfadan indirebilir veya temizleyebilirsin. Şifre Arda Research tarafından alınmaz. Portföy fiyatları Yahoo Finance üzerinden kontrol edilir; alınamayan fiyatlarda kullanıcı girişi kullanılır. Veri gecikmeli veya son kapanış olabilir. Kullanıcı AI analizini başlatırsa adet, maliyet, fiyat ve şirket raporları OpenAI API hizmetine gönderilir; kullanıcı adı ve e-posta gönderilmez. İşlem geçmişi, komisyonlar, fiyat gözlemleri ve alarmlar da hesabına özel tutulur. Fiyat alarmları sayfa açıkken kontrol edilir; kapalı sayfaya e-posta veya anlık bildirim gönderimi yoktur. Geçmiş performans, kayıtlanan gözlemlerden başlar. Son AI raporu hesabına özel saklanır ve portföy temizlendiğinde kaldırılır. Sağdaki veri kontrolleri ayrı olarak şeffaf kurallarla hesaplanır.</p></article><p class="reader-terms">')
assets['/hakkimizda/index.html']=[about,'text/html; charset=utf-8']
portfolio_html=(P/'portfolio.html').read_text().replace('<div class="pf-toolbar">', '<div class="pf-toolbar"><a href="/kripto/portfoyum/" class="asset-switch-link">Kripto portföyü ↔</a>',1).replace('<script src="/portfolio.js" defer>', '<script src="/portfolio-privacy.js" defer></script><script src="/portfolio.js" defer>')
assets['/portfolio-privacy.js']=[(P/'portfolio-privacy.js').read_text(),'text/javascript; charset=utf-8']
assets['/portfoyum/index.html']=[portfolio_html,'text/html; charset=utf-8']
assets['/portfolio.js']=[(P/'portfolio.js').read_text(),'text/javascript; charset=utf-8']
assets['/portfolio-tools.js']=[(P/'portfolio-tools.js').read_text(),'text/javascript; charset=utf-8']
assets['/portfolio.css']=[(P/'portfolio.css').read_text(),'text/css; charset=utf-8']
portfolio_companies=[{k:c[k] for k in ['ticker','name','sector','date','moat','future','analysis','nextEarnings','earningsSummary']} for c in cs]
for c in portfolio_companies:
 t=c['analysis']['technical'];c['technicalDate']=t['date'];c['levels']={k:t.get(k) for k in ['support','support2','resistance','resistance2']};c['analysis']={'financial':c['analysis']['financial']}
events=json.loads((P/'earnings-event-references.json').read_text())['confirmed']
for c in portfolio_companies:c['earningsEvent']=events.get(c['ticker'])
fresh=json.loads((P/'portfolio-calendar-updates.json').read_text())
for c in portfolio_companies:
 if c['ticker'] in fresh:c.update(fresh[c['ticker']])
assets['/portfolio-catalog.json']=[json.dumps({'companies':portfolio_companies,'symbols':symbols},ensure_ascii=False),'application/json; charset=utf-8']
crypto_market=json.loads((ROOT/'data/crypto-market-seed.json').read_text());crypto_histories=json.loads((ROOT/'data/crypto-history-seed.json').read_text());crypto_meta=json.loads((ROOT/'data/crypto-meta-seed.json').read_text())
crypto_histories=json.loads(subprocess.run(['node',str(ROOT/'scripts/build-crypto-technical.mjs')],input=json.dumps(crypto_histories),capture_output=True,text=True,check=True).stdout)
for route,file,mime in [('/kripto/index.html','crypto.html','text/html'),('/crypto.js','crypto.js','text/javascript'),('/crypto.css','crypto.css','text/css'),('/kripto/portfoyum/index.html','crypto-portfolio.html','text/html'),('/crypto-portfolio.js','crypto-portfolio.js','text/javascript'),('/crypto-portfolio-tools.js','crypto-portfolio-tools.js','text/javascript'),('/crypto-chart.js','crypto-chart.js','text/javascript'),('/crypto-portfolio-analytics.js','crypto-portfolio-analytics.js','text/javascript'),('/crypto-workbench.js','crypto-workbench.js','text/javascript'),('/crypto-workbench.css','crypto-workbench.css','text/css')]:assets[route]=[(P/file).read_text(),mime+'; charset=utf-8']
from market_navigation import with_markets,STYLE
assets['/daily-technical.js']=[(P/'daily-technical.js').read_text(),'text/javascript; charset=utf-8']
assets['/daily-technical.css']=[(P/'daily-technical.css').read_text(),'text/css; charset=utf-8']
for route,file,mime in [('/bist/index.html','bist.html','text/html'),('/bist/portfoyum/index.html','bist-portfolio.html','text/html'),('/bist.js','bist.js','text/javascript'),('/bist-core.js','bist-core.js','text/javascript'),('/bist.css','bist.css','text/css'),('/bist-portfolio.js','bist-portfolio.js','text/javascript'),('/bist-portfolio-tools.js','bist-portfolio-tools.js','text/javascript'),('/api/bist/catalog','bist-catalog.json','application/json'),('/veri-durumu/index.html','research-status.html','text/html'),('/research-status.js','research-status.js','text/javascript')]:assets[route]=[(P/file).read_text(),mime+'; charset=utf-8']
assets['/market-navigation.css']=[STYLE,'text/css; charset=utf-8']
for route,asset in assets.items():
 if asset[1].startswith('text/html'):
  market='bist' if route.startswith('/bist/') else 'crypto' if route.startswith('/kripto/') else 'us'
  asset[0]=with_markets(asset[0],market,'portfoyum' in route)
  if route=='/index.html' or route.startswith('/hisse/') or route.startswith('/bist/'):
   asset[0]=asset[0].replace('</head>','<link rel="stylesheet" href="/daily-technical.css"><script src="/daily-technical.js"></script></head>')
  if route.startswith('/hisse/'):
   ticker=route.split('/')[2];asset[0]=asset[0].replace('<div class="reader-metrics">','<div id="readerDailyTechnical"></div><script>window.ArdaDailyTechnical.mount(document.getElementById("readerDailyTechnical"),"us",'+json.dumps(ticker)+');</script><div class="reader-metrics">',1)
runtime=(ROOT/'worker/daily-technical.js').read_text()+'\n'+(ROOT/'worker/bist-portfolio.generated.js').read_text().replace('export async function','async function')+'\n'+(ROOT/'worker/research-status.js').read_text()+'\n'+(ROOT/'worker/crypto-data.js').read_text()+'\n'+(ROOT/'worker/crypto.js').read_text()+'\n'+(ROOT/'worker/crypto-portfolio.generated.js').read_text().replace('export async function','async function')+'\n'+(ROOT/'worker/portfolio-tools.js').read_text()+'\n'+(ROOT/'worker/portfolio-market.js').read_text()+'\n'+(ROOT/'worker/portfolio.js').read_text().replace('export async function','async function')+'\n'+(ROOT/'worker/runtime.js').read_text().replace('export function','function').replace('export async function','async function')
code=runtime+'\nconst cryptoCmcIdMap='+json.dumps(json.loads((ROOT/'data/crypto-cmc-ids.json').read_text()),separators=(',',':'))+';\nconst cryptoLegacySeed='+json.dumps(json.loads((ROOT/'data/crypto-legacy-market.json').read_text()),separators=(',',':'))+';\nconst cryptoMarketSeed='+json.dumps(crypto_market,ensure_ascii=False,separators=(',',':'))+';\nconst cryptoHistories='+json.dumps(crypto_histories,separators=(',',':'))+';\nconst cryptoMetadata='+json.dumps(crypto_meta,ensure_ascii=False,separators=(',',':'))+';\nconst assets='+json.dumps(assets,ensure_ascii=False,separators=(',',':'))+';\nconst bistCatalog=JSON.parse(assets[\"/api/bist/catalog\"][0]);\nconst feeds='+json.dumps(feeds)+';\nconst fallback='+json.dumps(fallback,ensure_ascii=False)+';\nexport default makeWorker(assets,feeds,fallback,'+json.dumps(portfolio_companies,ensure_ascii=False,separators=(',',':'))+');\n'
(ROOT/'worker/index.js').write_text(code);(ROOT/'worker/public-asset-paths.json').write_text(json.dumps(list(assets),indent=2));print('Built public Worker with',len(assets),'routes and',len(feeds),'news sources; raw audit and OHLCV routes excluded')
