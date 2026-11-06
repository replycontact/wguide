#!/usr/bin/env python3
"""Validate self containment, navigation, shared content and PDF integrity."""
from pathlib import Path
import json,re,zipfile
from collections import Counter
from urllib.parse import unquote
from bs4 import BeautifulSoup
import fitz
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def check(condition,message):
    if not condition:errors.append(message)
catalog=json.loads((ROOT/'content/catalog.json').read_text())
page=(ROOT/'dist/index.html').read_text();soup=BeautifulSoup(page,'html.parser')
ids=[e['id'] for e in soup.find_all(id=True)]
check(not [i for i,n in Counter(ids).items() if n>1],'Duplicate HTML ids')
for a in soup.find_all('a',href=True):
    href=a['href']
    if href.startswith('#'):check(unquote(href[1:]) in ids,'Missing anchor: '+href)
    elif not href.startswith(('http:','https:','data:','mailto:')):check((ROOT/'dist'/href).exists(),'Missing file: '+href)
for el in soup.select('script[src],img[src],link[href],iframe[src]'):
    source=el.get('src',el.get('href',''))
    check(source.startswith(('data:','#')),'External runtime resource: '+source)
check(not re.search(r'(?:src|url)\s*\(?(?:["\']?)https?://',page),'Remote rendering dependency')
check(not re.search(r'\[S\d{2}(?:[;,\]])',soup.get_text()),'Unresolved manuscript citation')
check(len(soup.select('.chapter'))==len(catalog),'Chapter count differs')
check(len(catalog)>=15,'Missing expected scope')
check(len(soup.get_text().split())>24000,'Guide unexpectedly short')
for c in catalog:
    check(bool(soup.select_one('#'+c['id']+' .prose')),'Missing chapter '+c['id'])

pdfpath=ROOT/'output/pdf/wow-forever-human-priest-guide.pdf'
doc=fitz.open(pdfpath)
check(len(doc)>50,'PDF unexpectedly short')
check(len(doc.get_toc())>=len(catalog),'Missing PDF bookmarks')
links=0;bound_issues=[]
for n,p in enumerate(doc,1):
    text=p.get_text()
    check(bool(text.strip()),f'Empty PDF page {n}')
    check('\ufffd' not in text,f'Replacement glyph on page {n}')
    links+=len(p.get_links())
    for block in p.get_text('dict')['blocks']:
        if 'lines' not in block:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>p.rect.width+.5 or y1>p.rect.height+.5:
                    bound_issues.append({'page':n,'text':span['text'][:50],'box':span['bbox']})
check(not bound_issues,'PDF text outside page: '+str(bound_issues[:5]))
check(links>100,'PDF source/navigation links missing')
alltext=' '.join(p.get_text() for p in doc)
for word in ['Divine Grace','Holy Binding','Thrill of Adventure','First Aid','Shadowform','Prayer of Mending']:
    check(word in alltext,'Missing core topic from PDF: '+word)
with zipfile.ZipFile(ROOT/'dist/wguide-offline.zip') as z:
    check('index.html' in z.namelist(),'ZIP has no HTML')
    check(pdfpath.name in z.namelist(),'ZIP has no PDF')
    check(z.read(pdfpath.name)==pdfpath.read_bytes(),'ZIP contains stale PDF')
single=(ROOT/'output/site/wow-forever-priest-guide.html').read_text()
check('id="embedded-pdf"' in single,'Standalone HTML missing embedded PDF')
check('href="wow-forever-human-priest-guide.pdf"' not in single,'Standalone HTML needs separate PDF')
report={'chapters':len(catalog),'html_words':len(soup.get_text().split()),'pdf_pages':len(doc),'pdf_bookmarks':len(doc.get_toc()),'pdf_links':links,'pdf_bytes':pdfpath.stat().st_size,'self_contained':not errors,'errors':errors,'browser_qa':'Unavailable: managed Sites requires cua_repl.js, not exposed in this session.'}
(ROOT/'output/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
