import json,pathlib,re
p=pathlib.Path('dist/index.html');s=p.read_text();data=json.loads(pathlib.Path('dist/companies.json').read_text());hashes=json.loads(pathlib.Path('dist/legacy-hashes.json').read_text());a=s.index('const catalog=');b=s.index('let selected=',a)
loader='''const catalog=CATALOG;
+const legacyHashes=HASHES;
+const fnv=s=>{let h=2166136261;for(let i=0;i<String(s).length;i++)h=Math.imul(h^String(s).charCodeAt(i),16777619);return h>>>0};
+let items;try{items=JSON.parse(localStorage.getItem('arda-research-v1'))||[];if(!Array.isArray(items))items=[]}catch{items=[]}
+let installed=[];try{installed=JSON.parse(localStorage.getItem('arda-catalog-installed'))||[]}catch{}
+if(localStorage.getItem('arda-analysis-revision')!=='2026-10-13-r4'){
+const personal=items.filter(x=>!catalog.some(c=>c.ticker===x.ticker)&&x.id!=='demo');
+items=catalog.filter(c=>items.some(x=>x.ticker===c.ticker)||!installed.includes(c.ticker)).map(c=>{const old=items.find(x=>x.ticker===c.ticker);let next={...c};if(old){for(const [key] of schema){if(key in old&&legacyHashes[c.ticker]?.[key]!==undefined&&fnv(old[key])!==legacyHashes[c.ticker][key])next[key]=old[key]}}return next}).concat(personal);
+try{localStorage.setItem('arda-analysis-revision','2026-10-13-r4');localStorage.setItem('arda-catalog-installed',JSON.stringify(catalog.map(x=>x.ticker)));localStorage.setItem('arda-research-v1',JSON.stringify(items))}catch{}
+}
+'''.replace('\n+','\n').replace('CATALOG',json.dumps(data,ensure_ascii=False,separators=(',',':'))).replace('HASHES',json.dumps(hashes))
s=s[:a]+loader+s[b:]
s=s.replace('Manuel giriş','12 Ekim kapanışı')
s=s.replace('Canlı fiyat, otomatik bilanço veya yapay zekâ bağlantısı henüz yok.','57 şirketin bilanço, teknik görünüm ve senaryoları eklendi. Veriler 12 Ekim 2026 ABD kapanışının sabit görüntüsüdür; canlı akış değildir. Her raporun mali dönemi ayrı gösterilir.')
s=s.replace('Profiller tamamlanmış bilanço veya teknik analiz değildir.','Hedefler koşullu model sonuçlarıdır; büyüme, sulanma ve çarpan varsayımları şirket dosyalarında görünür.')
s=s.replace('<th>SEKTÖR</th><th>ANALİZ DURUMU</th><th>TEKNİK GÖRÜNÜM</th><th>VADE</th><th>VERİ / PROFİL TARİHİ</th>','<th>SEKTÖR</th><th>FİYAT</th><th>DURUM</th><th>TEKNİK</th><th>RSI14</th><th>ANA SENARYO · 3Y</th><th>VADE</th><th>FİYAT TARİHİ</th>')
s=s.replace('<td>${esc(x.sector)}</td><td><span','<td>${esc(x.sector)}</td><td><b>${x.price?"$"+Number(x.price).toFixed(2):"—"}</b></td><td><span')
s=s.replace('<td>${esc(x.trend)}</td><td>${esc(x.horizon)}</td>','<td>${esc(x.trend)}</td><td>${x.analysis?.technical?.rsi14?.toFixed(1)||"—"}</td><td>${x.analysis?.scenarios?.base?.target?"$"+x.analysis.scenarios.base.target.toFixed(2):"—"}</td><td>${esc(x.horizon)}</td>')
s=s.replace('colspan="6"','colspan="9"')
s=s.replace("['Profil hazır','İnceleniyor','Olumlu','Nötr','Olumsuz']","['Analiz hazır','Profil hazır','İnceleniyor','Olumlu','Nötr','Olumsuz']").replace("['Veri bekleniyor','Teyit bekliyor','Yükseliş','Yatay','Düşüş']","['Yükseliş','Karma','Düşüş','Kısa geçmiş','Veri bekleniyor','Teyit bekliyor','Yatay']")
s=s.replace("<div class=\"card wide\" style=\"margin-bottom:16px\"><h3>Birleşik değerlendirme</h3>","${snapshotCards(x)}<div class=\"card wide\" style=\"margin-bottom:16px\"><h3>Birleşik değerlendirme</h3>")
s=s.replace('<div class="grid">${card(\'01 / İş modeli\'','${priceChart(x)}<div class="grid">${card(\'01 / İş modeli\'')
s=s.replace('<h2>Bir tahmin değil, üç senaryo.</h2>','<h2>Üç yıl. Üç koşullu senaryo.</h2><p>${esc(x.analysis?.model||"Fiyat seviyesi, vade ve gerçekleşme koşulları birlikte değerlendirilir.")}</p>')
s=s.replace('<div style="margin-top:16px">${card(\'Veri kaynakları ve rapor dönemi\',\'sources\')}</div>','<div style="margin-top:16px">${card(\'Veri kaynakları ve rapor dönemi\',\'sources\')}</div><div class="actions"><button id="printReport">Raporu yazdır / PDF</button><a href="analysis-audit.json" download="arda-research-veri-dokumu.json">Hesaplama verilerini indir</a></div>')
s=s.replace("$('edit').onclick=()=>editor(x)}","$('edit').onclick=()=>editor(x);$('printReport').onclick=()=>window.print()}")
s=s.replace("'Tamamlanmış',", "'Tamamlanmış',")
s=s.replace('Trend, RSI, ATR veya alım/satım sinyali hesaplanmadı.','Teknik göstergeler günlük fiyat serilerinden hesaplandı.')
s=s.replace('Yöntem geçmiş veride maliyetler ve ayrı test dönemiyle doğrulanana kadar kanıtlanmış performans iddiası taşımaz.','Gösterge hesapları doğrulandı; bunları birleştiren işlem stratejisinin kârlılığı için geçmiş performans iddiası yapılmıyor. 3 yıllık hedefler gelir büyümesi, pay artışı ve çarpan değişimi duyarlılıklarıdır; temettü, vergi ve işlem maliyetlerini içermez.')
s=s.replace('<footer><span>','<footer><span>')
s=s.replace('USD} · Veri / profil tarihi','USD} · Veri / profil tarihi')
s=s.replace("let clean={id:crypto.randomUUID()};for(let [k] of schema)","let clean={...(catalog.find(c=>c.ticker===x.ticker)||{}),id:crypto.randomUUID()};for(let [k] of schema)")
helpers='''
function snapshotCards(x){const a=x.analysis;if(!a)return '';const f=a.financial,t=a.technical;const dollars=v=>'$'+Number(v).toFixed(2);const cards=[['ABD KAPANIŞI',dollars(t.price),'12 Ekim 2026'],['GELİR BÜYÜMESİ',f.revenueGrowth===null?'Karşılaştırılamaz':(f.revenueGrowth>=0?'+':'')+f.revenueGrowth.toFixed(1)+'%','Çeyrek / yıllık · '+f.reportDate],['RSI / ATR',t.rsi14.toFixed(1)+' / '+t.atrPct.toFixed(1)+'%','Momentum / oynaklık'],['İŞLEM PLANI',a.trade.rewardRisk1.toFixed(2)+'R',a.trade.entryType+' · ilk hedef']];return '<div class="metrics">'+cards.map(c=>`<div class="card"><div class="label">${esc(c[0])}</div><strong>${esc(c[1])}</strong><p>${esc(c[2])}</p></div>`).join('')+'</div>'}
function priceChart(x){const a=x.analysis?.technical;if(!a?.history?.length)return '';const bars=a.history.filter(b=>Number.isFinite(b.close)&&b.close>0);if(!bars.length)return '';const w=1000,h=220,min=Math.min(...bars.map(b=>b.close)),max=Math.max(...bars.map(b=>b.close)),span=max-min||1;const yy=p=>h-20-(p-min)/span*(h-40);const xx=i=>15+i/(bars.length-1||1)*(w-30);const points=bars.map((b,i)=>xx(i).toFixed(2)+','+yy(b.close).toFixed(2)).join(' ');return `<article class="card" style="margin-bottom:16px"><div class="detailtop"><h3>Fiyat geçmişi · ${bars.length} seans</h3><div class="label">${esc(bars[0].date)} → ${esc(bars.at(-1).date)}</div></div><svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(x.ticker)} günlük kapanış grafiği"><title>Günlük kapanışlar, USD; en düşük ${min.toFixed(2)}, en yüksek ${max.toFixed(2)}</title><line x1="15" x2="985" y1="110" y2="110" stroke="#304039"/><polyline points="${points}" fill="none" stroke="#c5ee93" stroke-width="2.5"/><circle cx="985" cy="${yy(bars.at(-1).close).toFixed(2)}" r="4" fill="#c5ee93"/></svg><div class="detailtop"><span class="label">Düşük kapanış $${min.toFixed(2)} / yüksek kapanış $${max.toFixed(2)}</span><span class="label">Son kapanış $${bars.at(-1).close.toFixed(2)}</span></div></article>`}
'''
s=s.replace('function render(){',helpers+'\nfunction render(){')
s=s.replace('</style>','.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 16px}.metrics strong{display:block;font-size:25px;margin-top:12px;color:var(--green)}.metrics p{font-size:11px;margin-bottom:0}svg{width:100%;height:auto} .report a{overflow-wrap:anywhere}@media(max-width:750px){.metrics{grid-template-columns:repeat(2,1fr)}}@media print{body{background:white;color:#111}header,.hero,.stats,.toolbar,.tablewrap,.notice,.method,footer,#sectors,.detailtop button,.actions{display:none!important}main{padding:0}.card{background:white;border-color:#ddd;color:#111;break-inside:avoid}.report,p,.label{color:#333}.metrics strong,h1 em,a{color:#111}.grid,.scenarios{display:block}.card{margin-bottom:14px}section.card{display:none}.detail{margin:0}svg{max-height:200px}} </style>')
p.write_text(s)
pathlib.Path('/tmp/arda-script.js').write_text(s.split('<script>')[1].split('</script>')[0]);print('Site updated with complete reports and metrics')
