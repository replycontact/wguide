# The healing spellbook

Research cutoff: 6 November 2026. This chapter concerns Blizzard's World of Warcraft: Forever, using its launch-era 1.60.1 rules, not Wrath 3.3.5, Classic Era, Season of Discovery, or retail. Recommendations labelled **working build**, **practice exercise**, or **planning rule** are original advice, not claims that a published simulation has established a universal optimum. Item information from the level-20/30 beta is labelled accordingly. Spellbook tooltips and current hotfix notes take precedence over this snapshot.



## What the new healer needs to know first

You can heal early dungeons without spending every point in Holy. A damage-oriented Priest still owns the baseline heal, shield, dispel, and buff toolkit. Your talent choice determines efficiency and specialization, while your trained spells, equipment, mana supply, and decisions determine whether the next pull is manageable. For a first character who quests alone between groups, retaining a useful wand and some solo efficiency usually matters more than forcing a pure healer tree at level 10.

Holy becomes a clear commitment as you buy cast-time reduction, healing efficiency, and group support. It is attractive if you like anticipating damage, selecting the right heal for its deadline, and using a broad toolkit. There is no fixed healing rotation: a spell that is excellent when three allies are injured can waste your entire next global cooldown when only the tank needs help.

The following launch distinctions are especially consequential:

- **Binding Heal is gone.** The November 2 official notes replace it with **Holy Binding**, a passive which makes Flash Heal on somebody else also heal you for half as much, without threat from that self-healing. An old guide telling you to bind and cast Binding Heal is stale.
- Damage absorbed on Warriors and Druids is ignored when determining their incoming-damage rage generation. The old blanket instruction to avoid shielding rage tanks is therefore wrong for the documented Forever implementation.
- Extremely outdated ranks suffer reduced scaling and reduced activation chances for class effects. Do not import a Classic level-60 Rank 1 healing strategy unquestioningly.

These three corrections come from [Blizzard's development notes](https://us.forums.blizzard.com/en/wow/t/wow-forever-beta-development-notes-%E2%80%93-updated-november-2/2360696/1), including the downranking explanation under User Interface and the damage-absorb correction under Classes.

Prayer of Healing targets the party of the ally you select. Prayer of Mending occupies the deep Holy capstone. Divine Spirit is baseline rather than a Discipline investment. These changes make party selection and actual tree depth important. [Blizzard Priest deep dive](https://worldofwarcraft.blizzard.com/en-gb/news/24301514/world-of-warcraft-forever-class-deep-dives-priest-and-warrior)



## Your first five-person group

Before accepting the healer role, buy current water, repair, train the relevant healing ranks, and put your emergency buttons somewhere reachable while moving. Check the party's levels and explain if this is your first visit. Being able to say “I need a drink before the next pack” is part of healing well; trying to conceal an empty mana bar is not.

Use party frames large enough to show health, range, and removable debuffs. Put your own frame beside the others. A healer who loses track of their own health is especially vulnerable during an otherwise routine pull. Learn where your tank is standing before the tank rounds a corner. Your healing range does not remove the need for line of sight.

At the first pack, observe rather than assume. Does the tank lose health steadily or in sudden chunks? Do enemies run loose immediately? Does the party interrupt casts? How long does a pack live? This information tells you whether you can use measured direct heals, need to cover spikes, or must reserve mana for an unusually long fight. A small, controlled first pull is effectively a gear and teamwork check.

Position a short distance behind the tank, with a safe path toward the group if a creature attacks you. Avoid standing at the far edge of your maximum range purely because you can: a doorway or a few steps from the tank may turn that into a missed heal. Also avoid standing inside frontal attacks simply to make Holy Nova convenient. Move to a useful position while health is stable, then cast; repeated last-second movement wastes more healing time than a deliberate reposition.

Your first goal is to make the pull predictable. Your second is to keep enough mana for something unexpected. Damage contribution comes after those two. Wanding a nearly dead enemy can be helpful, but continuing to wand through a tank's sudden health drop because “the mob is almost dead” is a common avoidable wipe.



## A usable healing spellbook

### Lesser Heal, Heal, and Greater Heal

These are successive tools in the slow direct-heal family. At the beginning, Lesser Heal is what you have. Heal arrives at level 16. Greater Heal arrives at level 40. Do not erase the previous spell from your bars the instant a new name appears, but make the new current-rank spell available and compare actual results.

The recorded first-rank Heal tooltip is 155 mana, 3 seconds, and 260–300 healing before your character's modifiers. Its displayed raw coefficient is 0.857. These are database records, not a guarantee that a level-60 character receives full scaling from this old rank. [Heal spell record](https://www.wowhead.com/forever/spell=2054/heal)

The first Greater Heal record is 370 mana, 3 seconds, and 819–920 base healing, also showing a raw 0.857 coefficient. [Greater Heal spell record](https://www.wowhead.com/forever/spell=2060/greater-heal)

**Practical use:** choose a slow heal when its landing time is safe and its amount will mostly become useful health. Start earlier than you would with Flash Heal. You can begin a cast while the tank is still fairly healthy if the next incoming swing is predictable; cancel if the damage never happens and no one needs the heal. Do not intentionally let a beginner tank fall into lethal range just to maximize a large heal's efficiency.

### Flash Heal

Flash Heal is the short direct cast. The first-rank record, learned at 20, gives a 1.5-second cast, 125 mana, 184–223 base healing, and a raw 0.429 coefficient. [Flash Heal spell record](https://www.wowhead.com/forever/spell=2061/flash-heal)

**Practical use:** buy time when the slower heal would arrive too late. A fast heal is also appropriate for a modest injury that matters immediately, such as a damage dealer who must survive one more unavoidable hit. It is not automatically wrong outside an emergency: Holy Binding can make it solve two injuries at once. It is usually wrong to use speed without a reason and then blame your mana pool.

When Holy Binding is learned, first look for an injured ally if you and somebody else need health. Flash Heal on that ally can cover both problems. If you alone are low, healing a full-health ally solely to trigger self-healing is normally an inefficient workaround; choose a direct self-heal or another appropriate defensive instead. Do not assume the passive is an independent button, and do not let the temptation of two-target healing delay a truly urgent self-save.

### Renew

Renew is an instant heal over time, useful when the target will continue taking damage or when you must move. Think in terms of **usable ticks**. If only one tick will land before another healer tops the target, the spell may be a poor purchase. If the tank will take steady damage while you handle a dispel, Renew can be useful preparation.

Avoid reflexively refreshing it while substantial duration remains. A full-duration Renew is not the same thing as immediate health. A tank about to die before its next tick needs an immediate intervention. Multiple Priest Renews can coexist in Forever; coordinate assignments anyway, because stacking many heal-over-time effects on a nearly healthy target still wastes mana. The coexistence change is described in [Blizzard's Priest overview](https://worldofwarcraft.blizzard.com/en-gb/news/24301514/world-of-warcraft-forever-class-deep-dives-priest-and-warrior).

### Power Word: Shield

Shield is prevention, not a replacement for every direct heal. Use it to cover damage before it arrives, protect a cast from pushback, or bridge a short emergency. Track Weakened Soul: a failed repeated shield attempt consumes attention without solving anything. The spell's standard lockout remains relevant even though absorbing a tank's damage no longer blocks the documented rage calculation.

Do not treat a pre-pull shield as mandatory on every harmless pack. Ask whether it will actually absorb relevant damage, and whether paying for it now leaves enough mana for recovery. On a difficult pull it can create the opening seconds you need. On a trivial pull the tank might finish with health to spare without it.

### Prayer of Healing

This is the deliberate party-healing cast, learned at level 30. Its cast is long enough that you must judge who will survive until completion. It operates on the selected ally's party, so in raids you must select a member of the group you intend to heal. It is not a smart heal that automatically repairs the five lowest players across the raid. [Holy Priest abilities overview](https://www.wowhead.com/forever/guide/classes/priest/holy/healer-abilities)

Before starting it, check: are several people in that party actually injured, are they positioned to receive it, and will the tank survive while you cast? If only one party member is endangered, a direct heal is often the correct first move. A party heal that lands after the tank dies has not solved the encounter.

### Holy Nova

Holy Nova is an instant close-range party heal with damage around you. Its effects do not generate threat, but its damage can still wake an enemy from breakable crowd control or engage something you should have left alone. Zero threat is not permission to press it beside a Polymorphed creature. Its short radius also means it is not a substitute for a ranged party heal. [Holy talent data](https://wowfdb.com/classes/priest/holy/talents/)

A useful moment is a tightly grouped party taking moderate damage while you need to move, provided the damage component will not cause trouble. If the party is spread out, do not sprint into danger just to use it. Evaluate the cost for the number of allies actually healed.

### Prayer of Mending

Prayer of Mending is the reason to commit at least 31 points to Holy. The current tooltip describes a reactive heal that can trigger from damage **or non-periodic healing**, then jump to a nearby party or raid member. It has a 10-second cooldown and only one application per caster may be active. [Current Priest talent records](https://www.foreverdb.app/en/forever/classes/priest)

Put it where a trigger is likely and another useful recipient is nearby. The tank is a natural opening target, but not automatically the best target at every moment. A ranged player isolated from everyone else can strand the bounce. Recasting merely because the cooldown ended can replace an application that still had useful work to do. Watch where it is, not just whether your button is available.

If it sits on a player who will not take damage, a necessary direct heal can trigger the next jump. Do not spend an otherwise unnecessary heal just to make an animation move. The bounce's benefit must justify the extra mana and time.

### Human emergency: Divine Grace

Do the level-10 Human Priest class quest. The Goldshire breadcrumb runs from Priestess Josetta to High Priestess Laurena in Stormwind, and awards Divine Grace. [Quest record](https://www.wowhead.com/forever/quest=94774/divine-grace)

Divine Grace instantly heals a friendly target below 50% health and clears that target's Weakened Soul. It cannot target you. The current spell database shows a **10-minute** cooldown, whereas the earlier Blizzard deep dive described five minutes; until directly checked in the live client, treat the cooldown as a source conflict and plan conservatively around the spellbook's displayed value. [Current Divine Grace record](https://www.wowhead.com/forever/spell=1277370/divine-grace)

The meaningful emergency sequence is: Divine Grace on an eligible ally, reassess health, and shield if the next damage event still needs coverage. Clearing Weakened Soul enables a new shield; it does not cast the shield for you. This is especially valuable when the ally was already locked out of being shielded. Humans no longer have the Dwarf-only self-heal Desperate Prayer, so do not leave your self-survival plan depending on a button your character cannot learn.

### Inner Focus, Fade, and Spirit of Redemption

Inner Focus is an activated Discipline talent that makes the next qualifying spell free and improves its non-periodic critical chance. **Meditation**, a separate talent, is the passive which preserves part of Spirit regeneration during casting. Do not confuse the two. [Current Discipline talent data](https://www.foreverdb.app/en/forever/classes/priest)

Use Inner Focus deliberately on a valuable heal, especially an expensive group heal when several allies need it. Saving it throughout an entire dungeon “for the real emergency” can be less helpful than using it early enough to make it available again. Conversely, automatically attaching it to every Flash Heal can spend it on an insignificant injury.

Fade temporarily lowers your threat. Use the interval to move toward the tank and let the tank collect the creature. Running away from the tank through fresh enemies makes the problem harder. Fade does not permanently erase the healing threat that caused the problem.

Spirit of Redemption is a post-death healing window, not an invulnerability cooldown that you choose to activate. If it occurs, immediately heal the people who can finish the pull. Do not open chat to apologize while the window runs out. It does not make ordinary resurrection into an in-combat resurrection, and it is not a reason to stand in lethal mechanics.
