import json,pathlib,subprocess,re
P=pathlib.Path('dist');ROOT=pathlib.Path('/workspace/scratch/8dcd55070d2a/research-data');cs=json.loads((P/'companies.json').read_text());business=json.loads((P/'business-models.json').read_text());business.update(json.loads((P/'expansion-business-models.json').read_text()));guidance=json.loads((P/'earnings-guidance.json').read_text());metrics={x['ticker']:x for x in json.loads((ROOT/'metrics.json').read_text())};base=json.loads(subprocess.check_output(['git','show','2d89ba3562aac6b685025aacd587d6e043997c6c:dist/companies.json']));oldhashes=json.loads((P/'legacy-hashes.json').read_text())
def money(v,cur='USD'):
 scale=1e9 if abs(v)>=1e9 else 1e6 if abs(v)>=1e6 else 1;label='milyar' if scale==1e9 else 'milyon' if scale==1e6 else '';return f'{v/scale:,.2f} {label} {cur}'.replace(',',' ')
def fnv(s):
 h=2166136261
 for ch in str(s):h=((h^ord(ch))*16777619)&0xffffffff
 return h
accepted={}
for c in base:
 accepted[c['ticker']]={k:[fnv(v)] for k,v in c.items() if k not in ['analysis']}
for t,fields in oldhashes.items():
 for k,h in fields.items():accepted.setdefault(t,{}).setdefault(k,[]).append(h)
for c in cs:
 t=c['ticker'];b=business[t];f=c['analysis']['financial'];raw=metrics[t]['fundamental'];cur=f['currency'];c['revision']='2026-10-13-r6';c['businessDetails']=b
 c['business']='Ne yapıyor?\n'+c['business'].split('\n')[0]+'\n\nNasıl para kazanıyor?\n'+b['revenueModel']+'\n\nMüşterileri kim?\n'+b['customers']+'\n\nMüşteri neden kullanıyor?\n'+b['customerValue']+'\n\nBizim şirket değerlendirmemiz\n'+b['economicAnalysis']
 positives=[];negatives=[];g=f['revenueGrowth'];op=f['operatingQuarter'];net=f['netQuarter'];cf=f['cfo'];fcf=f['fcf'];cap=f['capex'];cash=f['cash'];date=f['reportDate']
 if g is not None and g>0:positives.append(f'Çeyrek gelir geçen yılın aynı dönemine göre %{g:.1f} arttı; ürün talebinin gelire dönüşmesi açısından olumlu.')
 elif g is not None:negatives.append(f'Çeyrek gelir geçen yılın aynı dönemine göre %{abs(g):.1f} geriledi; talep ve ürün karması incelenmeli.')
 if op is not None:
  if op>0:positives.append(f'Raporlanan faaliyet sonucu {money(op,cur)} kâr.'+(f' Faaliyet marjı %{f["operatingMargin"]:.1f}.' if f['operatingMargin'] is not None else ''))
  else:negatives.append(f'Raporlanan faaliyet sonucu {money(op,cur)} zarar; büyüme henüz faaliyet kârlılığını sağlamıyor.')
 if cf is not None and cf>0:positives.append(f'{f["cashflowPeriod"]} döneminde faaliyet nakit akışı {money(cf,cur)} pozitif.')
 if cf is not None and cf<0:negatives.append(f'{f["cashflowPeriod"]} döneminde operasyonlar {money(abs(cf),cur)} nakit tüketti; finansman ihtiyacı izlenmeli.')
 if fcf is not None and fcf<0:negatives.append(f'Aynı dönemde CFO eksi yatırım harcaması {money(fcf,cur)}; yeni yatırım faaliyet nakdini aşıyor.')
 elif cap is not None and cap>0:negatives.append(f'Yatırım harcaması {money(cap,cur)} nakit gerektirdi; bunun gelecekteki getirisi ayrıca doğrulanmalı.')
 if net is not None and net<0 and op and op>0:negatives.append(f'Faaliyet kârına rağmen net sonuç {money(net,cur)} zarar; faaliyet dışı kalemler önemli.')
 sbc=raw['flows']['sbc'].get('latestPeriod')
 if sbc and sbc['val']>0:negatives.append(f'Hisse bazlı ödeme {money(sbc["val"],cur)} ({sbc["start"]}–{sbc["end"]}); kazanç kalitesi ve olası sulanma açısından izlenmeli.')
 if len(positives)<2 and cash is not None:positives.append(f'Bilançoda {money(cash,cur)} nakit var; bu bir likidite tamponu, operasyonel başarı garantisi değil.')
 if len(negatives)<2:
  dn=raw['balances'].get('debtNoncurrent')
  if dn and dn['val']>0:negatives.append(f'Raporlanan uzun vadeli borç {money(dn["val"],cur)} ({dn["end"]}); vade ve faiz yükü kontrol edilmeli.')
 if len(negatives)<2:negatives.append('Sonuçların sürdürülebilirliği için müşteri yoğunlaşması, yeni siparişlerin gelire dönüşümü ve bir sonraki dönemin nakit üretimi takip edilmeli.')
 c['earningsSummary']={'period':date,'summary':f'Son çeyrek gelir {money(f["revenueQuarter"],cur)}'+(f'; yıllık değişim %{g:+.1f}.' if g is not None else '.')+' '+(f'Faaliyet sonucu {money(op,cur)}, net sonuç {money(net,cur)}.' if op is not None and net is not None else '')+'\n'+(f'Nakit {money(cash,cur)}; nakit akışının gelir artışını destekleyip desteklemediği ayrı değerlendirildi.' if cash is not None else ''),'positives':positives[:3],'negatives':negatives[:3]}
 mg=guidance.get(t);sourceFile=ROOT/(t+'-outlook.json');record=json.loads(sourceFile.read_text()) if sourceFile.exists() else {};watch=c['financial'].split('Şirkete özel izlenecek kalemler: ')[-1]
 c['nextEarnings']={'management':mg,'referencePeriod':date,'watchlist':[f'Gelir / talep: son çeyrek {money(f["revenueQuarter"],cur)}'+(f', yıllık büyüme %{g:.1f}.' if g is not None else '.')+' Yeni raporda büyümenin ürün ve müşteri kaynakları incelenecek.',f'Kârlılık: son faaliyet marjı %{f["operatingMargin"]:.1f}; yeni dönemde ürün karması ve maliyet değişimiyle birlikte karşılaştırılacak.' if f['operatingMargin'] is not None else 'Kârlılık: net sonucun operasyonel kaynakları ve tek seferlik kalemler incelenecek.',f'Nakit / finansman: faaliyet nakdi {money(cf,cur)} ({f["cashflowPeriod"]}). Satışın tahsilata dönüşümü, yatırım ihtiyacı ve sulanma takip edilecek.' if cf is not None else 'Nakit: tahsilat, yatırımlar ve finansman birlikte değerlendirilecek.',watch],'positiveTrigger':'Gelir, marj ve nakit üretiminin birlikte güçlenmesi; varsa şirket rehberliğinin karşılanması veya yükseltilmesi.','negativeTrigger':'Büyümenin müşteri/proje yoğunlaşmasına bağlı kalması, marjın zayıflaması, nakit tüketiminin artması veya rehberliğin aşağı çekilmesi.','source':mg['source'] if mg else record.get('source',c['sources'].splitlines()[0]),'sourceDate':mg['published'] if mg else record.get('filingDate',date),'note':'Şirket rehberliği yönetimin beklentisidir; analist konsensüsü değildir. Takip maddeleri bizim analiz çerçevemizdir, sayısal kâr tahmini değildir. Yıl geneli rehberliği çeyrek beklentisi gibi sunulmaz.'}
 if mg:c['sources']+='\nSonraki bilanço rehberliği: '+mg['source']+' · '+mg['published']
 else:c['sources']+='\nSonraki bilanço için referans: '+c['nextEarnings']['source']
older=json.loads(subprocess.check_output(['git','show','2d89ba3562aac6b685025aacd587d6e043997c6c:dist/accepted-legacy-hashes.json']));
for t,fs in older.items():
 for k,hs in fs.items():accepted.setdefault(t,{}).setdefault(k,[]).extend(hs)
(P/'business-models.json').write_text(json.dumps(business,ensure_ascii=False,indent=2))
(P/'companies.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2));(P/'earnings-review.json').write_text(json.dumps({c['ticker']:{'summary':c['earningsSummary'],'nextEarnings':c['nextEarnings']} for c in cs},ensure_ascii=False,indent=2));(P/'accepted-legacy-hashes.json').write_text(json.dumps(accepted));print('Enhanced',len(cs),'companies;',len(guidance),'management outlooks')
