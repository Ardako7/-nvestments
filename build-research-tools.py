import json,pathlib,statistics,datetime,importlib.util
P=pathlib.Path('dist');R=pathlib.Path('/workspace/scratch/8dcd55070d2a');cs=json.loads((P/'companies.json').read_text());audit=json.loads((P/'analysis-audit.json').read_text());ms={x['ticker']:x for x in audit['metrics']};eventrefs=json.loads((P/'earnings-event-references.json').read_text());confirmed=eventrefs['confirmed']
risks=json.loads((P/'risk-footprints.json').read_text());riskSources=json.loads((P/'risk-sources.json').read_text())
medians={s:statistics.median([c['analysis']['financial']['ps'] for c in cs if c['sector']==s and c['analysis']['financial']['ps'] is not None]) for s in {c['sector'] for c in cs}}
out={}
for c in cs:
 t=c['ticker'];f=c['analysis']['financial'];a=c['analysis']['technical'];p=c['ranking']['parts'];raw=ms[t]['fundamental'];b=raw['balances'];ca=b.get('currentAssets');cl=b.get('currentLiabilities');ratio=ca['val']/cl['val'] if ca and cl and cl['val']>0 and ca['end']==cl['end']==f['reportDate'] else None
 liquidity=10 if ratio is not None and ratio>=2 else 8 if ratio is not None and ratio>=1.5 else 6 if ratio is not None and ratio>=1 else 3 if ratio is not None else 5
 parts={'Ürün kalıcılığı':round(p['Ürün kalıcılığı']*1.5,1),'Kârlılık':round(p['Kârlılık']*25/15,1),'Gelir büyümesi':round(p['Gelir büyümesi']*20/15,1),'Nakit üretimi':round(p['Nakit üretimi']*1.5,1),'Cari likidite':liquidity};score=round(sum(parts.values()),1);ps=f['ps'];median=medians[c['sector']];peer=ps/median if ps else None
 valLabel='FFO / AFFO ile değerlendirmeli' if t in ['EQIX','DLR'] else 'Pay yapısı / veri kapsamı sınırlı' if ps is None else 'Yüksek beklenti yükü' if ps>20 or (f['pe'] and f['pe']>65) else 'Sektörüne göre primli' if peer>1.4 else 'Sektörüne göre düşük çarpan' if peer<.75 else 'Sektör bandına yakın'
 entryGap=(a['price']-a['support'])/a['atr14'];timing='Kırılım teyidi gerekiyor' if a['trend']!='Yükseliş' else 'Destek bölgesine yakın' if entryGap<=1.5 else 'Destekten uzak; seçici giriş'
 interpretation=('Temel güç yüksek; yüksek fiyat beklentilerini ve giriş koşulunu ayrı kontrol et.' if valLabel in ['Yüksek beklenti yükü','Sektörüne göre primli'] else 'Temel güç yüksek; görece çarpanı, borcu ve giriş teyidini birlikte değerlendir.') if score>=80 else 'İş modeli ve nakit üretimini izlemek gerekiyor; düşük çarpan tek başına fırsat sayılmaz.'
 quality={'score':score,'parts':parts,'label':'Temel gücü yüksek' if score>=80 else 'Dengeli / seçici' if score>=60 else 'Gelişme bekleniyor','currentRatio':ratio,'peerMedianPS':median,'peerRatio':peer,'valuationLabel':valLabel,'timingLabel':timing,'interpretation':interpretation,'price':a['price'],'priceDate':a['date'],'reportDate':f['reportDate']}
 rev=raw['flows']['revenue'];op=raw['flows']['operating'];prior=rev['prior'];opprior=op['prior'];delta=None
 if opprior and prior and opprior['end']==prior['end'] and prior['val']>0 and f['operatingMargin'] is not None:delta=f['operatingMargin']-opprior['val']/prior['val']*100
 changes=[f'Gelir yıllık %{f["revenueGrowth"]:+.1f} değişti.' if f['revenueGrowth'] is not None else 'Önceki yıl aynı çeyrek gelir karşılaştırması doğrulanamadı.',f'Faaliyet marjı geçen yılın aynı çeyreğine göre {delta:+.1f} puan değişti.' if delta is not None else 'Faaliyet marjı için dönemleri eşleşen yıllık karşılaştırma yok.',('Faaliyet nakdi pozitif.' if f['cfo']>0 else 'Faaliyet nakdi negatif.')+' Nakit akışının dönemi: '+f['cashflowPeriod'] if f['cfo'] is not None else 'Faaliyet nakdi karşılaştırması doğrulanmadı.']
 rr=risks.get(t,{});thesis={'why':c['ranking']['reason'],'invalidation':rr.get('thesisInvalidation',c['ranking']['risk']),'watchMetrics':rr.get('watchMetrics',c['nextEarnings']['watchlist'][:3]),'changes':changes,'referencePeriod':f['reportDate'],'comparisonPeriod':prior['end'] if prior else None,'source':c['nextEarnings']['source']}
 if t in confirmed:
  cal={**confirmed[t],'status':'confirmed','start':confirmed[t]['date'],'end':confirmed[t]['date']}
 elif t in eventrefs['targeted']:
  v=eventrefs['targeted'][t];cal={**v,'status':'targeted','start':v['date'],'end':v['date'],'method':'Şirketin açıkladığı hedef tarih; kesin rapor duyurusu değil.'}
 else:
  ref=eventrefs['previousResults'][t];published=ref['published'];source=ref['source']
  center=datetime.date.fromisoformat(published)+datetime.timedelta(days=91) if published else None
  cal={'status':'estimated' if center and center+datetime.timedelta(days=14)>=datetime.date(2026,10,13) else 'unknown','start':(center-datetime.timedelta(days=14)).isoformat() if center else None,'end':(center+datetime.timedelta(days=14)).isoformat() if center else None,'time':'Doğrulanmadı','source':source,'published':published,'checkedAt':'2026-10-13','method':'Son doğrulanmış sonuç açıklamasının tarihi + 91 gün, ±14 gün. Şirketin açıkladığı tarih değildir.'}
  if cal['status']=='unknown':cal['start']=cal['end']=None
 cal.update(ticker=t,name=c['name'],sector=c['sector'],guidance=c['nextEarnings']['management'],watchMetrics=thesis['watchMetrics'],referencePeriod=f['reportDate'])
 out[t]={'quality':quality,'thesis':thesis,'calendar':cal,'risks':rr.get('risks',[]),'riskSources':riskSources.get(t,[]), 'primarySource':c['nextEarnings']['source']}
(P/'research-tools.json').write_text(json.dumps({'asOf':'2026-10-13','priceAsOf':'2026-10-12','companies':out},ensure_ascii=False,indent=2));print('Research tools',len(out),'confirmed calendars',len(confirmed),'risk coverage',len(risks))
