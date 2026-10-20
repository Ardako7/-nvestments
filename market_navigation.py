import re
STYLE='''
.arda-markets{display:flex!important;align-items:center;gap:3px!important;border:1px solid var(--line,#304039);border-radius:10px;padding:4px!important;background:rgba(127,150,135,.06);font-family:system-ui,sans-serif;flex-shrink:0;margin-left:12px;max-width:100%}.arda-markets>a{display:inline-block!important;padding:7px 11px!important;border:0!important;border-radius:6px!important;text-decoration:none!important;white-space:nowrap;font-size:11px!important;line-height:1.4;color:var(--muted,#a2b3a9)!important;background:none!important;font-weight:550}.arda-markets>a[aria-current=page]{background:var(--green,#c5ee93)!important;color:var(--bg,#101817)!important}.arda-markets>a:last-child{border-left:1px solid var(--line,#304039)!important;border-radius:0!important;font-size:10px!important;padding-left:12px!important}.arda-markets>a:focus-visible{outline:2px solid var(--green,#c5ee93);outline-offset:2px}.bist-page .arda-markets>a[aria-current=page],.bist-portfolio .arda-markets>a[aria-current=page]{background:#126450!important;color:white!important}.arda-data-link{font-size:11px}@media(max-width:1050px){header:has(.arda-markets){flex-wrap:wrap;gap:16px}.arda-markets{margin-left:0}}@media(max-width:600px){header>.arda-markets{justify-content:center;width:100%;order:5}header>.arda-markets>a{flex:1;text-align:center}}
'''
def with_markets(markup,market='us',portfolio=False):
 markup=re.sub(r'<div class="asset-switch"[^>]*>.*?</div>','',markup,flags=re.S)
 markup=re.sub(r'<a\b[^>]*class="asset-switch-link"[^>]*>.*?</a>','',markup,flags=re.S)
 markup=re.sub(r'<a\b[^>]*>\s*(?:Kripto|ABD)(?: portföyü)?\s*↔\s*</a>','',markup)
 dest={'us':'/portfoyum/' if portfolio else '/', 'crypto':'/kripto/portfoyum/' if portfolio else '/kripto/', 'bist':'/bist/portfoyum/' if portfolio else '/bist/'}
 nav='<nav class="arda-markets" aria-label="Piyasa seçimi">'+''.join('<a href="'+dest[k]+'"'+(' aria-current="page"' if k==market else '')+'>'+label+'</a>' for k,label in [('us','ABD'),('crypto','Kripto'),('bist','BIST')])+'<a href="/veri-durumu/" aria-label="Veri kaynakları ve güncellik">Veri durumu ↗</a></nav>'
 markup=markup.replace('</header>',nav+'</header>',1)
 if '/market-navigation.css' not in markup:markup=markup.replace('</head>','<link rel="stylesheet" href="/market-navigation.css"></head>')
 return markup
