#!/usr/bin/env python3
"""Organize the researched manuscripts into shared website / PDF chapters."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'content'; OUT.mkdir(exist_ok=True)

def sections(name):
    raw=(ROOT/'manuscripts'/name).read_text()
    chunks=re.split(r'(?m)^(## .+)$',raw)
    return chunks[0],{re.sub(r'^## (?:\d+\. )?','',chunks[i]):re.sub(r'^## (?:\d+\. )?','## ',chunks[i])+chunks[i+1] for i in range(1,len(chunks),2)}

sp,s=sections('01-systems.md'); hp,h=sections('02-healing.md'); xp,x=sections('03-shadow-pvp.md')
catalog=[]
def add(id,title,kicker,description,group,parts):
    text='\n\n'.join(parts)
    text=re.sub(r'(?m)^# .+\n','',text).strip()
    path=f'content/{len(catalog)+1:02}-{id}.md'
    (ROOT/path).write_text('# '+title+'\n\n'+text+'\n')
    catalog.append(dict(id=id,title=title,kicker=kicker,description=description,group=group,markdown=path))

quick='''## The first decisions, in one minute

Start a **Human Priest at level 1 with zero Legacy points**. For mainly solo play, use the continuous **14/0/37 Shadow route**: two wand points first, then Shadow, with Shadowform at 42. You can heal early dungeons with your baseline tools while following it. If healing becomes your main activity, use the separate **20/31/0 Holy route**, not a mixture of the two point tables.

For the account, put gradually earned early points into **Thrill of Adventure** when most of your time is spent questing alone. The complete leveling plan then adds Well Rested and Talented. An established account can front-load the Well Rested → Talented prerequisite chain for an alt; your new account cannot assume those ten points already exist.

For professions, **Tailoring + Herbalism** is the economical default in this guide: cloth utility and a crafting milestone line, plus saleable herbs. First Aid is a secondary profession and now makes healing potions. When your account has money and a second character, distribute crafting professions deliberately rather than repeatedly paying to replace the main's skills.

In combat, train current spells, prioritize a useful early wand, and practice three actions before difficult pulls: a deliberate self-heal, a safe retreat, and a controlled shield. Human **Divine Grace saves an eligible ally, not yourself**. Shadow Word: Death can cost **30% of your maximum health** when it hits without killing. These are core habits, not details to learn after the first dangerous pull.

This is a launch guide checked on **6 November 2026**. The dates and disagreements behind those recommendations appear beside the detailed explanations below and in the source appendix.
'''
add('start','A fresh Human Priest','Begin from zero','Your first choices, the Human toolkit, and the habits that make a fresh account work.','The first character',[quick,sp,s['Choose the world you actually want to play in'],s['Three kinds of progress that must not be confused'],s['Exactly what a fresh account starts without'],s['Human racials and what they change for a Priest'],s['The first sessions: useful habits before any build is complete']])
add('legacy','The account plan','Legacy points','Earn useful milestones, spend each point deliberately, and distinguish your first Priest from a funded alt.','The first character',[s[k] for k in ['Where the account’s points come from','The account arithmetic before choosing a route','Recommended first allocation: the solo-first Priest','Talented: powerful earlier access, no level-60 bonus points','Well Rested and travel perks: what their percentages mean','Different sixteen-point jobs for different characters','Three realistic paths from zero toward sixteen']])
add('fieldcraft','Travel, camps & gold','A sustainable journey','Keep travel, camp benefits and gold decisions aligned with the character you are actually playing.','The first character',[s[k] for k in ['Camping fits naturally into the route','Gold, respecs, and the level-40 decision','A compact account review after every major session']])
add('shadow','The Shadow leveling build','Point by point','One continuous, zero-Legacy route to 14/0/37, with every milestone and tradeoff explained.','Shadow & solo play',[xp,x['What changes the Shadow plan in Forever'],x['The low-cost continuous Shadow leveling build: 14/0/37']])
add('combat','The solo combat playbook','Pull, recover, repeat','Build a sustainable fighting rhythm from your first wand through Shadowform and harder pulls.','Shadow & solo play',[x['How to fight while leveling']])
add('leveling','Northshire to level 60','The Human route','A flexible Alliance itinerary that adapts to new quests, your level and the opportunities you find.','Shadow & solo play',[x['Human quest route: a flexible path that survives Forever changes']])
add('holy','The healing spellbook','Make the right cast','Understand what each heal solves, prepare for your first group, and use your Human tools correctly.','Holy & group play',[hp,h['What the new healer needs to know first'],h['Your first five-person group'],h['A usable healing spellbook']])
add('holy-builds','Building your Holy Priest','Talent investment','A legal 20/31/0 foundation, its exact leveling order, and the cost of reaching Holy milestones sooner.','Holy & group play',[h['Build choices and exact legal point plans']])
add('healing','Healing under pressure','Decisions & practice','Manage mana and spell ranks, solve twelve common emergencies, and prepare for organized healing.','Holy & group play',[h['Mana, ranks, and efficiency without Classic-era traps'],h['Twelve healing situations and what to do']]+[v for k,v in h.items() if 'readiness card' in k]+[h['Moving from dungeon healer to raid healer']])
add('equipment','Gear that earns its place','Upgrade with purpose','Choose equipment for the problem it solves, with practical targets and honest limits on launch BiS claims.','Equipment & economy',[x['Gear for Shadow: buy performance that you can actually use'],h['Equipment decisions for a healer who also quests']])
add('professions','Professions & preparation','Build a useful account','Balance your first gold, healer crafts, account milestones, enchants, consumables and camp supplies.','Equipment & economy',[h['Professions and a fresh-account economy'],h['Enchants, consumables, and camp preparation']])
add('pvp','Shadow & Holy in PvP','Control the next moment','Legal builds and matchup decisions for damage, support, survival and pressure as a Human Priest.','Player versus player',[x['PvP starts with a different objective']])
add('battlegrounds','Objectives & PvP progression','Play for the win','Turn class tools into objective control, understand the progression system, and build a repeatable practice.','Player versus player',[x['Battleground objectives and a first-session plan']]+[v for k,v in x.items() if 'progression' in k.lower() and k!='PvP starts with a different objective']+[x['A mature character’s repeatable weekly practice']])
add('macros','Controls & macros','A usable interface','Put lifesaving actions within reach and adapt the clearly marked macro templates to your live client.','Reference',[h['Interface, keybinds, and safe macro templates'],x['Macros that solve specific problems']])

intro='''## How to read the evidence

This is an independent fan guide for Blizzard's World of Warcraft: Forever. Research was checked on **6 November 2026**; current client data cited by the researchers identifies **1.60.1.70790**. This is a launch snapshot, not a promise that future tuning will preserve every number.

**Official notes** establish announced rules and dated changes. **Client databases** establish extracted spell, talent or item records; they can lag behind a server hotfix. **Community guides** provide secondary checks and practical context. **Our recommendations** are original judgments about a fresh Human Priest, not official rankings or measured speedrun records. Zone routes are flexible baselines. Macro templates were not tested inside the live game.

For conflicts, read the most recent dated official change first, then compare current client data and your live tooltip. The September Priest deep dive is useful context but predates the November 2 changes. In particular, Holy Binding replaces Binding Heal, and Shadow Word: Death's non-killing-hit backlash is 30% of maximum health. The November 5 hotfix listing was checked and did not add a further Priest-specific correction: [Blizzard hotfixes](https://worldofwarcraft.blizzard.com/en-us/news/24315281/wow-forever-hotfixes-november-5-2026).

## Decisions that still need a live check

- **Divine Grace cooldown:** the older official description says five minutes; current database entries show ten. Plan conservatively and use the live spellbook.
- **Reset and dual-specialization prices:** no reliable live price was verified. Do not budget using a beta discount.
- **Legacy prerequisite arrows:** the listed builds follow cited client trees and conservative full-rank prerequisites. Confirm the live interface before a reset, especially Reagent Economy and profession perks.
- **Thrill trigger overlap:** the exact overlap behavior of rapid successive recovery effects was not established. Nominal per-kill examples are not guaranteed regeneration simulations.
- **Old spell ranks:** downranking rules changed. Measure effective healing and talent procs on your actual character rather than assuming Era coefficients.
- **Item availability, quest rewards and dungeon challenge checklists:** verify in the current client. The guide does not invent a full endgame BiS list from incomplete launch data.
- **Future raids and PvP systems:** scheduled content is labelled as future. Do not count an announced reward as something your new account can earn immediately.

## Source register

Sources are linked beside the claims they support. The register below consolidates the research ledgers; titles and notes describe why each source was used. Access date for this edition: **6 November 2026**. Older beta items are retained only where their date or a conflict is relevant.
'''
entries={}
for filename in ['01-sources.json','02-sources.json','03-sources.json','source-index.json']:
    obj=json.loads((ROOT/'research'/filename).read_text())
    items=obj if isinstance(obj,list) else obj.get('sources',[])
    for row in items:
        url=row.get('url')
        if not url:continue
        key=url.rstrip('/')
        if key not in entries:entries[key]=row
for i,row in enumerate(entries.values(),1):
    title=row.get('title') or row.get('name') or 'Research source'
    note=row.get('notes') or row.get('supports') or row.get('purpose') or row.get('evidence') or ''
    if isinstance(note,list):note='; '.join(note)
    if isinstance(note,dict):note=json.dumps(note)
    intro+=f'\n**{i:02}. [{title}]({row["url"]})**\n\n{note}\n'
intro+='''
## Production and reuse

The website and PDF are generated from the same edited Markdown chapters. The HTML includes its fonts, artwork, styles, search index and planner logic; the standalone edition also embeds the PDF. The complete project, editable source text, research ledger and build scripts are in [replycontact/wguide](https://github.com/replycontact/wguide).

The cover and website illustrations are original vector artwork. Noto and DejaVu font license notices accompany the repository. This is an unofficial guide, unaffiliated with Blizzard Entertainment; game names and trademarks belong to their respective owners.
'''
add('sources','Sources & live checks','Research notes','The launch snapshot, evidence hierarchy, unresolved conflicts, and the sources behind this guide.','Reference',[intro])
(OUT/'catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')

raw=json.loads((ROOT/'research/legacy-planner-research.json').read_text())
traits=[]
for trait in raw['traits']:
    item=dict(trait);gates=item['treeTierPrerequisites'];item['treePointsRequired']=gates['pointsInSameTreeBeforePurchase']
    item['prerequisites']={x['id']:x['rank'] for x in gates['requiredTraits']}
    traits.append(item)
plans=[]
for id,p in raw['recommendations'].items():
    plans.append(dict(id=id,name=p['name'],description=p['when'],steps=p['order'],caveat=' '.join(p.get('caveats',[]))))
(OUT/'legacy-planner.json').write_text(json.dumps(dict(checkedAt=raw['checkedAt'],traits=traits,plans=plans),indent=2,ensure_ascii=False)+'\n')
print(f'Compiled {len(catalog)} chapters and {len(plans)} Legacy plans.')
