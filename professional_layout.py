import re,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def refine(h):
 nav='<nav class="public-nav" aria-label="Ana gezinme"><a href="#current-prices">Piyasalar</a><a href="#top10">İlk 10</a><a href="#research">Şirketler</a><a href="#research-brief">Haberler</a><a href="#workbench">Araçlar</a><a href="#value-chain">Sektörler</a><a href="/hakkimizda/">Hakkımızda</a></nav>'
 h=re.sub(r'<nav class="public-nav".*?</nav>',nav,h,count=1,flags=re.S)
 hero_end=h.index('</div><aside>',h.index('<section class="hero"'))
 h=h[:hero_end]+'<div class="hero-actions"><a href="#research">Şirketleri keşfet ↗</a><a href="#current-prices">Piyasa ekranını aç</a></div>'+h[hero_end:]
 # Move supplementary directories together below the primary research sections.
 blocks=[]
 for ident in ['ranking-past','value-chain']:
  pattern=r'<section id="'+ident+r'".*?</section>'
  m=re.search(pattern,h,re.S)
  if m:blocks.append(m.group());h=h[:m.start()]+h[m.end():]
 if blocks:h=h.replace('<section id="workbench"','<div class="workspace-directory">'+''.join(blocks)+'</div><section id="workbench"',1)
 css=(ROOT/'web/professional-layout.css').read_text()
 h=h.replace('</style>',css+'</style>',1)
 return h
