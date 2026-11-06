# Controls & macros

## Interface, keybinds, and safe macro templates

The templates below use ordinary secure WoW macro syntax and are **not live-client-tested during this research**. A Forever-specific macro reference publishes the same general mouseover pattern while also labelling most examples untested. Test targeting on friendly players in a safe area before relying on a macro in a dungeon. [Forever Holy macro reference](https://wowfdb.com/classes/priest/holy/macros/)

Use built-in unit frames and any available native mouseover or click-casting settings if you prefer. You do not need an elaborate interface to heal your first dungeon. Do not assume a retail addon package runs in Forever merely because the spell names look familiar.

### Core mouseover heal

```text
#showtooltip Flash Heal
/cast [@mouseover,help,nodead][help,nodead][@player] Flash Heal
```

It tries a living friendly mouseover, then a living friendly selected target, then yourself. Replace Flash Heal with Heal, Greater Heal, Renew, or another appropriate friendly spell to make related buttons. A valid mouseover that is out of range generally causes a range failure; it does **not** guarantee fallback to a different unit just because the cast failed. Understand the targeting before using it.

### Emergency shield, distinct from normal casting

```text
#showtooltip Power Word: Shield
/stopcasting
/cast [@mouseover,help,nodead][help,nodead][@player] Power Word: Shield
```

This deliberately cancels your current cast. Put it on a separate emergency binding rather than adding `/stopcasting` to every heal. It can cancel a nearly completed life-saving heal even when the shield fails because of Weakened Soul. That is why the normal shield button can reasonably omit the stop line.

### Human Divine Grace with no self-fallback

```text
#showtooltip Divine Grace
/stopcasting
/cast [@mouseover,help,nodead][help,nodead] Divine Grace
```

This does not check health percentage; you must select an eligible ally. It has no self branch because Divine Grace cannot heal you. It also does not automatically follow with Shield. The two actions require separate decisions and normal global-cooldown handling.

### Friendly dispel only

```text
#showtooltip Dispel Magic
/cast [@mouseover,help,nodead][help,nodead][@player] Dispel Magic
```

This is intentionally a friendly-cleanse binding. If you also want to remove beneficial Magic from enemies, use a separate hostile binding so you do not accidentally spend your defensive dispel on the wrong unit type during a crowded fight.

### Party-directed Prayer of Healing

```text
#showtooltip Prayer of Healing
/cast [@mouseover,help,nodead][help,nodead][@player] Prayer of Healing
```

Mouse over somebody in the party that needs the heal. In a raid, the important selection is the party membership of that player. Test this while the raid is organized so that you do not discover the targeting rule during an emergency.

### A dedicated cast-cancel key

```text
/stopcasting
```

A separate cancel key is useful when a precast becomes unnecessary. Use it deliberately; repeated accidental cancellation is a major throughput loss. Moving briefly also interrupts many casts, but a dedicated key can keep you in your chosen position.

### Keybind priorities

Your easiest keys should cover the current slow heal, Flash Heal, Shield, Renew, dispel, Fade, and Divine Grace. Add Prayer of Healing and Prayer of Mending as learned. Put self-targeting on a predictable modifier or dedicated binding. Keep Inner Focus visible, and track Weakened Soul somewhere you can see while reading health.

Avoid a castsequence macro for healing. Damage does not arrive in the order your macro expects, and a sequence can strand you on the wrong spell after a target or cooldown condition changes. The interface should reduce targeting effort while preserving your ability to choose the next useful action.



## Macros that solve specific problems

These are standard secure-macro patterns to test on friendly targets and harmless enemies before relying on them. Spell names must match your client language. They do not automate targeting decisions, resource management, or a full rotation. Repeated presses may be necessary where a global cooldown separates actions.

**Shoot without toggling it off by repeated presses:**

```text
#showtooltip Shoot
/cast !Shoot
```

**Mind Flay without restarting an active channel:**

```text
#showtooltip Mind Flay
/cast [nochanneling:Mind Flay] Mind Flay
```

This protects a channel from accidental re-presses; you still need a movement or stop-cast action when a mechanic requires interruption. It is not a rule that every channel must finish regardless of danger.

**A deliberate self-heal that exits Shadowform:**

```text
#showtooltip Flash Heal
/stopcasting
/cancelaura Shadowform
/cast [@player] Flash Heal
```

Before Flash Heal is learned, substitute a heal you actually know. The stop-cast line is useful for emergency response but will cancel a productive cast if pressed unnecessarily. Keep this as an emergency key rather than your normal healing rotation button.

**Friendly mouseover shield with target and self fallback:**

```text
#showtooltip Power Word: Shield
/cast [@mouseover,help,nodead][help,nodead][@player] Power Word: Shield
```

The first eligible condition wins. A valid friendly mouseover takes priority over your selected target; practice that behavior so you do not shield the wrong ally while your mouse is resting on a raid frame.

**Friendly mouseover heal that also works after leaving form:**

```text
#showtooltip Flash Heal
/cancelaura Shadowform
/cast [@mouseover,help,nodead][help,nodead][@player] Flash Heal
```

Holy Binding, if talented, works through Flash Heal on another target. There is no need to put the removed active Binding Heal in this macro.

**A focus Silence for a watched enemy caster:**

```text
#showtooltip Silence
/stopcasting
/cast [@focus,harm,nodead][harm,nodead] Silence
```

This casts at a valid hostile focus before your current enemy target. Clear or change your focus deliberately when the relevant caster changes. A stale focus outside range can prevent the result you expected, so keep the focus frame visible.

**Separate defensive and offensive dispels:**

```text
#showtooltip Dispel Magic
/cast [@mouseover,help,nodead][help,nodead][@player] Dispel Magic
```

```text
#showtooltip Dispel Magic
/cast [@mouseover,harm,nodead][harm,nodead] Dispel Magic
```

Separating these actions reduces accidental offensive dispels when you meant to free yourself or a teammate. It also makes the intended target easier to recognize during an urgent fight.

**Divine Grace without an automatic self fallback:**

```text
#showtooltip Divine Grace
/cancelaura Shadowform
/cast [@mouseover,help,nodead][help,nodead] Divine Grace
```

This macro does not test the health threshold and does not make an ineligible target eligible. It deliberately omits a self fallback because the Human racial cannot be cast on yourself. If your current form interaction differs, test the first line’s necessity in a safe setting; the important invariant is selecting an eligible ally and knowing the cooldown actually shown by the client.
