import pathlib,json,subprocess
P=pathlib.Path('dist');h=subprocess.check_output(['git','show','910aa163db3586c4b95c94c9334a093772a88fd9:dist/index.html']).decode();data=json.loads((P/'research-tools.json').read_text())
h=h.replace('<a href="#research">Araştırma masası</a><a href="#detail">Şirket dosyası</a>','<a href="#research">Araştırma masası</a><a href="#workbench">Karşılaştır / Takvim / Portföy</a><a href="#detail">Şirket dosyası</a>')
h=h.replace('<section id="research">',pathlib.Path('scripts/tools-sections.html').read_text()+'<section id="research">')
h=h.replace('${companyQuickView(x)}','${companyQuickView(x)}${qualityCard(x)}${thesisCard(x)}')
h=h.replace('bindCompanyTools(x);', 'bindCompanyTools(x);bindResearchCards(x);')
h=h.replace('<a href="#report-business">İş modeli</a>','<a href="#quality-price">Kalite / fiyat</a><a href="#thesis-tracker">Tez takibi</a><a href="#report-business">İş modeli</a>')
h=h.replace('initResearch();renderRanking();render();', 'const researchTools='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n'+pathlib.Path('scripts/research-tools.js').read_text()+'\ninitResearch();initTools();renderRanking();render();')
h=h.replace('</style>',pathlib.Path('scripts/tools-style.css').read_text()+'</style>')
# Follow-list changes should immediately affect an open calendar.
h=h.replace('favorites.add(id);persist();}', 'favorites.add(id);persist();renderCalendar();}')
(P/'index.html').write_text(h);pathlib.Path('/tmp/arda-script.js').write_text(h.split('<script>')[1].split('</script>')[0]);print('Built five tools')
