import pathlib,json,subprocess,re
P=pathlib.Path('dist');cs=json.loads((P/'companies.json').read_text());accepted=json.loads((P/'accepted-legacy-hashes.json').read_text())
h=subprocess.check_output(['git','show','2d89ba3562aac6b685025aacd587d6e043997c6c:dist/index.html']).decode()
a=h.index('const catalog=');b=h.index('const fnv=',a);h=h[:a]+'const catalog='+json.dumps(cs,ensure_ascii=False,separators=(',',':'))+';\nconst legacyHashes='+json.dumps(accepted)+';\n'+h[b:]
a=h.index('let items;');b=h.index('function earningsRecap',a)
h=h[:a]+pathlib.Path('scripts/site-state.js').read_text()+'\n'+h[b:]
h=h.replace('65 şirket','101 şirket').replace('2026-10-13-r5','2026-10-13-r6')
h=h.replace('<div class="label headerlabel">ABD PİYASALARI · TEMEL + TEKNİK</div>','<nav aria-label="Ana gezinme"><a href="#top10">İlk 10</a><a href="#research">Araştırma masası</a><a href="#detail">Şirket dosyası</a></nav>')
h=h.replace('<body>','<body><a class="skip-link" href="#research">Araştırma masasına geç</a>')
h=h.replace('<section class="card" style="margin-top:28px">',pathlib.Path('scripts/ranking-section.html').read_text()+'<details class="card sector-panel" style="margin-top:28px"><summary>8 sektör · Araştırma evrenini keşfet</summary><section>')
h=h.replace('<div id="sectors" class="grid"></div></section><div class="toolbar">','<div id="sectors" class="grid"></div></section></details><section id="research"><div class="toolbar">')
h=h.replace('<div class="tablewrap"><table>', '<div class="research-controls"><select id="sortBy" aria-label="Tablo sıralaması"><option value="score">Birleşik puana göre</option><option value="name">Sembole göre A–Z</option><option value="growth">Gelir büyümesine göre</option><option value="rsi">RSI değerine göre</option></select><label class="check"><input type="checkbox" id="onlyTop"> Yalnız İlk 10</label><label class="check"><input type="checkbox" id="onlyFavorites"> Takip ettiklerim</label><button id="clearFilters">Filtreleri temizle</button><span id="resultCount" class="label" aria-live="polite"></span></div><div class="tablewrap"><table>')
a=h.index('<thead><tr>');b=h.index('</thead>',a)+8
h=h[:a]+'<thead><tr><th>TAKİP</th><th>ŞİRKET / SEMBOL</th><th>FİYAT</th><th>PUAN / 100</th><th>TREND</th><th>RSI14</th><th>DESTEK</th><th>DİRENÇ</th><th>FİYAT TARİHİ</th></tr></thead>'+h[b:]
h=h.replace('<section id="detail"','</section><section id="detail"')
a=h.index("function render(){");b=h.index("document.querySelectorAll('tr[data-id]')",a)
h=h[:a]+pathlib.Path('scripts/research-table.js').read_text()+'\n'+h[b:]
h=h.replace('<article class="card"><h3>${title}</h3>', '<article class="card" id="report-${key}"><h3>${title}</h3>')
h=h.replace('${snapshotCards(x)}', '${companyToolbar(x)}${snapshotCards(x)}${companyQuickView(x)}')
h=h.replace('<h2>Üç yıl. Üç koşullu senaryo.</h2>', '<h2 id="report-scenarios">Üç yıl. Üç koşullu senaryo.</h2>')
h=h.replace("$('edit').onclick=()=>editor(x);", "bindCompanyTools(x);$('edit').onclick=()=>editor(x);")
h=h.replace('return clean});selected=', "if(typeof x.personalNote==='string')notes[clean.id]=x.personalNote.slice(0,5000);if(x.favorite===true)favorites.add(clean.id);else if(x.favorite===false)favorites.delete(clean.id);return clean});selected=")
h=h.replace('file.size>2000000','file.size>10000000').replace('en fazla 2 MB','en fazla 10 MB')
h=h.replace("id:crypto.randomUUID()};for(let [k]", "id:catalog.find(c=>c.ticker===x.ticker)?.id||crypto.randomUUID()};for(let [k]")
h=h.replace("selected=items[0]?.id;persist();render()}}catch", "selected=items[0]?.id;persist();renderRanking();render()}}catch")
h=h.replace("selected=x.id;persist();$('editor').close();render()", "selected=x.id;persist();$('editor').close();renderRanking();render()")
h=h.replace("persist();$('editor').close();render()}}", "persist();$('editor').close();renderRanking();render()}}")
h=h.replace('<article class="card next-earnings">','<article class="card next-earnings" id="next-report">')
h=h.replace('</style>',pathlib.Path('scripts/site-upgrade.css').read_text()+'</style>')
h=h.replace('</script>',pathlib.Path('scripts/site-chart.js').read_text()+'\n'+pathlib.Path('scripts/site-features.js').read_text()+'\n</script>')
# Hooks must run after feature definitions and lexical state are initialized.
h=h.replace("});render();\n", "});\n")
h=h.replace('</script>','\ninitResearch();renderRanking();render();\n</script>')
(P/'index.html').write_text(h);pathlib.Path('/tmp/arda-script.js').write_text(h.split('<script>')[1].split('</script>')[0]);print('Updated site',len(cs))
