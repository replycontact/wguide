#!/usr/bin/env python3
"""Build a fully offline HTML guide from the same Markdown as the PDF."""
from pathlib import Path
import base64, html, json, re, shutil, zipfile
import markdown
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
catalog=json.loads((ROOT/'content/catalog.json').read_text())
legacy=json.loads((ROOT/'content/legacy-planner.json').read_text())
escape=html.escape

def slug(s):
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

chapters=[]; search=[]; nav=[]; directory=[]; words=0; used_ids=set()
last_group=None
for idx,c in enumerate(catalog):
    raw=(ROOT/c['markdown']).read_text()
    words+=len(re.findall(r"\b[\w'-]+\b",raw))
    soup=BeautifulSoup(markdown.markdown(raw,extensions=['tables','fenced_code','sane_lists']), 'html.parser')
    first=soup.find('h1')
    if first:first.decompose()
    toc=[]
    for heading in soup.find_all(['h2','h3','h4']):
        base=c['id']+'--'+slug(heading.get_text())
        aid=base;n=2
        while aid in used_ids:aid=base+'-'+str(n);n+=1
        used_ids.add(aid);heading['id']=aid
        if heading.name=='h2':toc.append(f'<li><a href="#{aid}">{escape(heading.get_text())}</a></li>')
        text=[]
        for el in heading.next_siblings:
            if getattr(el,'name',None) in ['h2','h3','h4']:break
            text.append(el.get_text(' ',strip=True) if hasattr(el,'get_text') else str(el))
        search.append({'id':aid,'title':heading.get_text(),'chapter':c['title'],'text':' '.join(text)})
    search.append({'id':c['id'],'title':c['title'],'chapter':c['kicker'],'text':soup.get_text(' ',strip=True)[:1800]})
    for table in soup.find_all('table'):
        wrap=soup.new_tag('div',attrs={'class':'table-wrap','role':'region','aria-label':'Scrollable reference table','tabindex':'0'});table.wrap(wrap)
    for a in soup.find_all('a',href=True):
        if a['href'].startswith('http'):a['rel']='noopener noreferrer'
    number=f'{idx+1:02}'
    group=c.get('group','Field guide')
    if group!=last_group:nav.append('<div class="nav-group">'+escape(group)+'</div>');last_group=group
    nav.append(f'<a href="#{c["id"]}" data-chapter="{c["id"]}"><span>{number}</span>{escape(c["title"])}</a>')
    directory.append(f'<a class="directory-link" href="#{c["id"]}"><span>{number}</span><div>{escape(c["title"])}<small>{escape(c["kicker"])}</small></div><span>↗</span></a>')
    prev=catalog[idx-1] if idx else {'id':'home','title':'Field guide home'}
    nex=catalog[idx+1] if idx<len(catalog)-1 else {'id':'home','title':'Back to the beginning'}
    count=len(raw.split())
    chapters.append(f'''<article class="chapter" id="{c['id']}" aria-labelledby="title-{c['id']}">
      <header class="chapter-head"><div class="eyebrow"><span>Chapter {number}</span><span>/</span><span>{escape(c['kicker'])}</span></div>
      <h1 id="title-{c['id']}">{escape(c['title'])}</h1><p class="chapter-deck">{escape(c['description'])}</p>
      <div class="chapter-tools"><span>{max(1,round(count/210))} min read · Launch edition / 06 Nov 2026</span><button class="font-toggle" aria-label="Toggle larger reading text">Aa Text size</button><button class="print-guide">Print guide</button><a href="wow-forever-human-priest-guide.pdf" download>Download PDF</a></div></header>
      <details class="chapter-toc"><summary>In this chapter</summary><ul>{''.join(toc)}</ul></details>
      <div class="prose">{soup}</div><nav class="chapter-footer" aria-label="Chapter navigation"><a href="#{prev['id']}"><span>Previous</span>{escape(prev['title'])}</a><a href="#{nex['id']}"><span>Next chapter</span>{escape(nex['title'])}</a></nav></article>''')

fontcss=''
for filename,family,weight,style in [('NotoSans-Regular','Guide Sans',400,'normal'),('NotoSans-Bold','Guide Sans',700,'normal'),('NotoSerifDisplay-Regular','Guide Serif',400,'normal'),('NotoSerifDisplay-Italic','Guide Serif',400,'italic')]:
    encoded=base64.b64encode((ROOT/f'assets/fonts/{filename}.woff').read_bytes()).decode()
    fontcss+=f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};font-display:swap;src:url(data:font/woff;base64,{encoded}) format('woff')}}"
css=(ROOT/'assets/style.css').read_text()
art=(ROOT/'assets/chapel.svg').read_text()
data={'chapters':[{k:v for k,v in c.items() if k!='markdown'} for c in catalog], 'search':search, 'legacy':legacy}
payload=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
scripts=(ROOT/'assets/planner.js').read_text()+'\n'+(ROOT/'assets/app.js').read_text()
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#161b24"><meta name="description" content="An extensive WoW: Forever Human Priest guide. Start with zero Legacy points and learn Shadow leveling, Holy healing, professions and PvP. Includes an offline Legacy planner."><title>Light &amp; Shadow — Human Priest / WoW: Forever</title><style>{fontcss}{css}</style></head><body>
<a class="skip" href="#main-content">Skip to content</a><div class="reading-progress" id="reading-progress" aria-hidden="true"></div>
<header class="topbar"><button id="menu-toggle" class="toolbtn menu-btn" aria-label="Open chapter menu" aria-controls="sidebar" aria-expanded="false">☰</button><a class="brand" href="#home"><span class="sigil" aria-hidden="true"></span>Light &amp; Shadow</a><nav class="toplinks" aria-label="Quick navigation"><a href="#start">Start here</a><a href="#legacy">Legacy</a><a href="#shadow">Shadow</a><a href="#holy">Holy</a><a href="#pvp">PvP</a></nav><button class="toolbtn search-open" id="search-open" aria-label="Search the guide">Search the guide <kbd>⌘ K</kbd></button><button class="toolbtn theme-btn" id="theme-toggle" aria-label="Toggle night reading mode" aria-pressed="false">◐</button></header>
<div class="layout"><aside class="sidebar" id="sidebar" aria-label="Guide chapters"><div class="eyebrow">A Human Priest field guide</div><a href="#home" data-chapter="home" class="active"><span>◇</span>Overview &amp; planner</a>{''.join(nav)}<div class="sidebar-foot">WoW: Forever · Launch edition<br>Research checked 06 November 2026<a class="download-link" href="wow-forever-human-priest-guide.pdf" download>↓ Download the complete PDF</a><a class="download-link" href="wguide-offline.zip" download>↓ Offline edition (.zip)</a></div></aside>
<main class="content" id="main-content"><noscript><div class="no-js-note">Every chapter is available below. JavaScript adds chapter navigation, search and the Legacy planner; the complete guide needs no internet connection.</div></noscript>
<div class="home" id="home"><section class="hero" aria-labelledby="hero-title"><div class="hero-copy"><div class="edition"><span>WoW: Forever</span>Launch field guide · 2026</div><h1 id="hero-title">Two paths.<br><em>One calling.</em></h1><p class="hero-deck">From your first steps in Northshire to the moment a party trusts you with its life. A complete Human Priest guide to Shadow, Holy, and a fresh account.</p><div class="hero-actions"><a class="btn" href="#start">Begin from zero ↗</a><a class="btn ghost" href="wow-forever-human-priest-guide.pdf" download>Get the field guide ↓</a></div></div><div class="hero-art" role="img" aria-label="An original illustration of a Human Priest beneath a stained-glass arch, holding light and shadow">{art}</div><span class="hero-caption">Light for your allies. Shadow for the road.</span></section>
<div class="stats"><div class="stat"><b>0 → 60</b><span>Your complete first-character journey</span></div><div class="stat"><b>16</b><span>Legacy points spendable per character</span></div><div class="stat"><b>51</b><span>Priest talent points at level 60</span></div><div class="stat"><b>{len(catalog):02}</b><span>Chapters · {round(words/1000):,}k words of guidance</span></div></div>
<section class="home-section"><div class="section-top"><h2>Choose your next step.</h2><span class="small">One character. Three ways to play.</span></div><p class="intro-line">Start at zero, keep your account moving forward, and learn the decisions behind each build.</p><div class="path-grid"><a class="path" href="#shadow"><span class="num">I</span><h3>Walk in Shadow</h3><p>A sustainable solo rhythm, exact talent sequences, gear priorities, and a route from Elwynn to level 60.</p><span class="go">The leveling playbook ↗</span></a><a class="path" href="#holy"><span class="num">II</span><h3>Keep them standing</h3><p>Read incoming damage, manage your mana, choose the right heal, and grow into a dependable Holy Priest.</p><span class="go">The healing playbook ↗</span></a><a class="path" href="#pvp"><span class="num">III</span><h3>Hold your ground</h3><p>Survive pressure, create space, protect an objective, and turn your class tools into meaningful team advantage.</p><span class="go">The PvP playbook ↗</span></a></div><div class="rule-strip"><h3>Forever has its own rules.</h3><p>This edition follows the launch snapshot of 6 November 2026. Dated changes take precedence over older guides; client-data conflicts are marked in the relevant chapters. Recommendations are original practical judgments, with their assumptions explained.</p></div></section>
<section class="home-section" id="legacy-planner"><div class="section-top"><h2>Make every Legacy point count.</h2><a class="small" href="#legacy">Read the full account strategy ↗</a></div><p class="intro-line">Account points are shared in availability. Each character chooses its own allocation, with a launch spending cap of sixteen.</p><div class="planner"><div class="planner-heading"><h3>Your next point, explained.</h3><span class="eyebrow">Offline allocation planner</span></div><div class="planner-controls"><div><label for="plan-choice">Choose a progression goal</label><select id="plan-choice"></select></div><div><label for="earned-points">Legacy points earned on your account (0–65)</label><input id="earned-points" type="number" min="0" max="65" step="1" value="0" inputmode="numeric"></div></div><p id="plan-description"></p><div class="point-summary"><div><strong id="account-points">0</strong><span>Account points</span></div><div><strong id="spent-points">0</strong><span>Assigned / 16</span></div><div><strong id="banked-points">0</strong><span>Unspent on this character</span></div></div><div class="allocations" id="allocations" aria-live="polite"></div><p class="planner-note" id="plan-next"></p><p id="plan-caveat"></p><a class="planner-source" href="#legacy">Check prerequisites, evidence and reset assumptions in the Legacy chapter ↗</a></div></section>
<section class="home-section"><div class="section-top"><h2>The complete field guide.</h2><span class="small">Read in order or go straight to the decision.</span></div><div class="chapter-directory">{''.join(directory)}</div></section></div>
{''.join(chapters)}<footer class="site-footer"><span>Light &amp; Shadow · Independent, unofficial fan guide.<br>World of Warcraft and related marks belong to Blizzard Entertainment.</span><span>Research snapshot: 06 Nov 2026<br><a href="#sources">Sources &amp; editorial method</a> · <a href="https://github.com/replycontact/wguide">Source repository</a></span></footer></main></div>
<div id="search-dialog" class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-label" hidden><div class="search-panel"><div class="search-header"><label id="search-label" class="eyebrow" for="search-input" style="position:absolute;clip-path:inset(50%)">Search the guide</label><input id="search-input" type="search" placeholder="Search a spell, build, profession…" autocomplete="off"><button id="search-close" aria-label="Close search">Esc</button></div><p class="search-hint" id="search-count" role="status">Search the entire guide, including builds, tables and sources.</p><div id="search-results"></div></div></div>
<script>window.GUIDE_DATA={payload};</script><script>{scripts}</script></body></html>'''
(OUT/'index.html').write_text(page)
pdf=ROOT/'output/pdf/wow-forever-human-priest-guide.pdf'
if pdf.exists():shutil.copy2(pdf,OUT/pdf.name)
# A single HTML file, with the PDF embedded in its download links.
standalone=page
if pdf.exists():
    encoded_pdf=base64.b64encode(pdf.read_bytes()).decode()
    standalone=standalone.replace('href="wow-forever-human-priest-guide.pdf" download','href="#embedded-pdf" data-embedded-pdf download="wow-forever-human-priest-guide.pdf"')
    embedded=f'<script id="embedded-pdf" type="application/octet-stream">{encoded_pdf}</script><script>document.querySelectorAll(\'[data-embedded-pdf]\').forEach(a=>a.href=\'data:application/pdf;base64,\'+document.getElementById(\'embedded-pdf\').textContent);</script>'
    standalone=standalone.replace('</body>',embedded+'</body>')
standalone=re.sub(r'<a class="download-link" href="wguide-offline.zip" download>.*?</a>','',standalone)
local=ROOT/'output/site';local.mkdir(exist_ok=True)
(local/'wow-forever-priest-guide.html').write_text(standalone)
with zipfile.ZipFile(OUT/'wguide-offline.zip','w',zipfile.ZIP_DEFLATED) as z:
    offline_page=re.sub(r'<a class="download-link" href="wguide-offline.zip" download>.*?</a>','',page)
    z.writestr('index.html',offline_page)
    if pdf.exists():z.write(pdf,pdf.name)
    z.writestr('READ-ME.txt','Open index.html in a browser. All guide text, artwork, fonts and interactive features work offline. Keep the PDF beside index.html for the download links. The source repository is https://github.com/replycontact/wguide\n')
shutil.copy2(OUT/'wguide-offline.zip',local/'wguide-offline.zip')
print(json.dumps({'chapters':len(catalog),'words':words,'search_sections':len(search),'html_bytes':(OUT/'index.html').stat().st_size,'standalone_bytes':(local/'wow-forever-priest-guide.html').stat().st_size}))
