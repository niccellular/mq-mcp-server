"""
EverQuest per-class knowledge base for agent orchestrators.

Each entry describes:
  - role: one-line class summary
  - combat_priority: ordered list of what to do in a fight
  - spell_categories: groups of spell types with usage timing
  - disciplines: melee combat abilities (/disc) with when to use
  - aas: activated AAs with when to use
  - innates: non-command abilities (procs, passives) worth knowing
  - survival: emergency options ordered by desperation
  - mana_endurance: recovery rules

This is general class knowledge at ~level 65. Specific spell names come
from get_state mem_spells; use this to understand WHAT those spells do
and WHEN to cast them.
"""

CLASS_KNOWLEDGE = {

    # ─────────────────────────────────────────────────────────────────────────
    "Warrior": {
        "role": "Pure melee tank. Highest AC/HP. No mana — endurance only.",
        "combat_priority": [
            "Taunt if off-tank to maintain aggro: /doability 1",
            "Disc: Mighty Strike on cooldown for burst damage",
            "Disc: Defensive when HP drops below 40%",
            "Auto-attack is primary DPS source",
            "Use bashes/kicks as they refresh",
        ],
        "spell_categories": {},  # Warriors have no spells
        "disciplines": {
            "Mighty Strike": "Burst melee damage. Use on cooldown. ~30s CD.",
            "Defensive": "Damage reduction ~50%. Save for when HP < 40% or add waves.",
            "Evasive": "Shorter duration, shorter CD dodge boost. Bridge between Defensives.",
            "Precision": "Accuracy increase. Use vs high-AC targets.",
            "Berserk": "High levels: damage boost with AC penalty. Use when confident in survivability.",
        },
        "aas": {
            "Veteran's Wrath": "Endurance refresh + combat boost. Use when endurance is low.",
            "Fury of Arms": "Melee DPS AA. Use on cooldown.",
        },
        "innates": [
            "Rampage (high level): AoE melee attack, triggered AA",
            "Bashes and kicks proc from auto-attack combat rounds",
        ],
        "survival": [
            "Disc: Defensive",
            "Disc: Evasive",
            "/sit to regen HP out of combat (WARNING: sitting in combat is dangerous)",
        ],
        "mana_endurance": "No mana. Endurance recovers on its own; sit between fights if needed.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Cleric": {
        "role": "Primary healer. Best single-target heals. Also undead nukes and buffs.",
        "combat_priority": [
            "Keep tank above 50% HP — Complete Heal or Wave of Healing",
            "HoT (Celestial Healing line) on tank before pull",
            "Divine Arbitration / Divine Favor for emergency heals",
            "Nuke undead only if heals not needed",
            "Buff (Temperance, Symbol) between fights",
        ],
        "spell_categories": {
            "Main heal": "Complete Heal / Wave of Healing — slow, big heal, cast when tank is 40-60% HP so it lands before they die",
            "Fast heal": "Light Healing line — instant small heals for emergencies",
            "HoT": "Celestial Healing line — cast before pull so it ticks during fight",
            "Undead nuke": "Banish Undead / Yaulp — only when group is safe and heals not needed",
            "Buff - AC/HP": "Temperance / Aegolism — cast before any fight",
            "Buff - Symbol": "Symbol of Kazad — HP/mana regen, cast on tank+self between fights",
            "Cure": "Counteract Poison/Disease — cure debuffs immediately, they reduce effectiveness",
            "Rez": "Resurrection — 96%+ XP return, cast after fight ends",
        },
        "disciplines": {
            "War March": "Self-only haste. Use when solo melee is required.",
        },
        "aas": {
            "Celestial Regeneration": "Powerful self/target HoT AA. Use on cooldown in tough fights.",
            "Turn Undead": "Instant undead DD/fear. Use on cooldown when fighting undead.",
            "Divine Arbitration": "AoE group HP balancing — equalizes group HP. Use when multiple members are low.",
        },
        "innates": [
            "Yaulp line: self-haste/STR disc-like spell. Keep active during melee.",
            "Stun spells: useful to interrupt undead spellcasters",
        ],
        "survival": [
            "Divine Aura: total invulnerability 18s but can't act — absolute last resort",
            "Stun the attacker then run",
            "Lay Hands equivalent: none (that's Paladin)",
        ],
        "mana_endurance": "Sit to meditate when mana < 20%. High mana cost class — pace pulls.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Paladin": {
        "role": "Hybrid tank/healer. Best vs undead. Lay Hands emergency heal. Slower mana regen.",
        "combat_priority": [
            "Disc: Holyforge on undead pulls — huge undead damage bonus",
            "Disc: Pious Fury on cooldown — haste + double attack",
            "Cast Stun spells to interrupt undead casters",
            "Force of Akera (or equivalent DD) vs undead on cooldown",
            "Heal self if HP < 50% with Healing Light line",
            "Buff Armor of Faith on self between fights",
        ],
        "spell_categories": {
            "Undead DD": "Force of Akera / Expel Undead — mana-efficient nuke vs undead only. Spam when fighting undead.",
            "Stun": "Stun line — interrupts, slows, slight damage. Use vs caster undead.",
            "Self-heal": "Healing Light / Supernal Cleansing — medium heal. Cast when below 50% HP.",
            "HoT": "Celestial Healing (lower-tier) — pre-cast before fight for regen ticks.",
            "Buff - AC": "Armor of Faith / Holy Armor — pre-fight self-buff.",
            "Buff - Symbol": "Symbol line — HP buffer, cast between fights.",
            "Undead dot": "Consecrate Undead — tick damage, use when kiting undead.",
            "Hate": "Wave of Holy Wrath — lifetap-like, adds aggro and heals.",
        },
        "disciplines": {
            "Holyforge": "Massive undead damage modifier. Use at the start of EVERY undead fight. ~3min CD.",
            "Pious Fury": "Self haste + double attack. Use on cooldown during melee. ~45s CD.",
            "Slay Undead (disc)": "Triggered via combat. Adds holy damage proc to attacks vs undead.",
            "Charge": "Brief invulnerability charge to close distance. Use to re-engage after kiting.",
        },
        "aas": {
            "Lay Hands": "Emergency 8000+ HP self-heal. 72-minute CD. Use ONLY when HP < 20%.",
            "Turn Undead": "Instant undead fear/DD. Use on cooldown vs undead.",
            "Holy Steed": "Mount summon — not useful in combat.",
            "Improved Lay Hands": "Upgrades Lay Hands heal amount.",
        },
        "innates": [
            "Slay Undead proc: attacks vs undead can proc a holy DD (~3900 damage at level 65)",
            "Resistant to undead fear spells (racial/class resist bonus)",
        ],
        "survival": [
            "Lay Hands (HP < 20% only — 72min CD)",
            "Healing Light self-heal",
            "Divine Aura: 18s invulnerability (can't attack)",
            "Root enemy then back up to cast heals",
        ],
        "mana_endurance": "Sit to meditate when mana < 20%. Slower regen than pure casters. Prioritize mana for heals > nukes.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Ranger": {
        "role": "Hybrid melee/archer/caster. Strong outdoors. Best bow DPS of any class.",
        "combat_priority": [
            "Archery: maintain distance and shoot if possible (outdoors: max damage)",
            "Disc: Trueshot Discipline for archery burst",
            "Melee if target closes distance",
            "Snare kiting for crowd control",
            "Ensnare / Bind Sight for tracking",
        ],
        "spell_categories": {
            "Snare": "Ensnare / Tanglewood — slow movement. Snare before kiting.",
            "DD (fire)": "Firestrike line — mana-efficient outdoors. Nuke at range.",
            "DOT": "Jolt line — quick mana-efficient ticks.",
            "Buff - haste": "Speed of the Shissar — group haste. Cast before pull.",
            "Buff - regen": "Regrowth — HP regen. Cast on tank between fights.",
            "Heal": "Minor heal line — emergency self-heal only.",
            "Root": "Root — stop fleeing enemies or hold adds.",
        },
        "disciplines": {
            "Trueshot": "Archery accuracy + damage. Max bow DPS window. ~10min CD.",
            "Weapon Shield": "Damage reduction. Use when caught in melee without tank.",
            "Flurry": "Multi-strike melee. Use in melee when within range.",
        },
        "aas": {
            "Endless Quiver": "Removes arrow consumption. Required for archery.",
            "Innate Camouflage": "Self-invis. Use to pull or escape.",
            "Archery Mastery": "Passive archery DPS increase.",
        },
        "innates": [
            "Dual wield: always active when two weapons equipped",
            "Double attack rate higher than most hybrids",
            "Archery does max damage outdoors vs indoors",
        ],
        "survival": [
            "Snare + kite to break melee",
            "Camouflage invis to reset aggro",
            "Minor self-heal if available",
        ],
        "mana_endurance": "Medium mana pool. Sit at < 20%. Melee between cast cycles.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Shadowknight": {
        "role": "Dark hybrid tank. Lifetaps sustain HP. Fear kiting strong. Best undead hate tools.",
        "combat_priority": [
            "Disc: Unholy Aura for sustained lifetap DPS",
            "Lifetap spells on cooldown — both DPS and self-heal",
            "Harm Touch on cooldown (or save for emergencies)",
            "Snare/Fear for kiting if outmatched",
            "Disc: Hate's Attraction for aggro generation",
        ],
        "spell_categories": {
            "Lifetap": "Siphon Strength line — drains HP from enemy, heals self. Primary sustain. Cast on cooldown.",
            "Undead only lifetap": "Leach line — stronger lifetap vs undead only.",
            "Fear": "Invoke Fear / Wave of Fear — fear kite. Snare first, then fear, then nuke.",
            "Snare": "Clinging Darkness — snares + minor debuff. Use before fear kiting.",
            "DOT": "Dooming Darkness / Shadow Vortex — tick damage. Apply and let them tick.",
            "Debuff - AC": "Weaken line — reduces enemy AC. Apply early in fight.",
            "Harm Shield": "Screaming Terror — AoE fear for adds.",
        },
        "disciplines": {
            "Hate's Attraction": "Massive aggro spike. Use when tank is losing aggro.",
            "Leechcurse": "Lifetap proc on melee attacks. Use in sustained fights.",
            "Unholy Aura": "Self DPS + hate generation disc. Keep active in combat.",
        },
        "aas": {
            "Harm Touch": "8000+ HP direct damage. 72-minute CD. Use early on tough targets.",
            "Life Burn": "Convert HP to spell damage (risky). Use when target is near death.",
            "Death's Effigy": "Self-targeted hate reduction. Use when overaggro'd with no tank.",
        },
        "innates": [
            "Dual wield and double attack",
            "Fear proc chance on some weapons",
        ],
        "survival": [
            "Lifetap to restore HP during combat",
            "Fear kite: Snare → Fear → nuke at distance",
            "Harm Touch if HP critical (save for true emergencies)",
            "FD (Feign Death) at high levels: /disc FeignDeath",
        ],
        "mana_endurance": "Sit at < 20% mana. Lifetaps are efficient — prioritize them over pure nukes.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Druid": {
        "role": "Outdoor specialist. Best ports/evac. Strong heals + nukes + DoTs. Excellent solo via snare-kite.",
        "combat_priority": [
            "Apply Snare first to enable kiting",
            "DoTs: Immolate + Drifting Death + Winged Death — then kite",
            "Nuke (Blaze / Sunblaze) to finish off low-HP targets",
            "Heal group/self when HP < 60%",
            "Regen + Skin buffs before every fight",
        ],
        "spell_categories": {
            "Snare": "Ensnare / Bonds of Tunare — mandatory before kiting.",
            "DOT - fire": "Immolate / Ros Firebolt — highest tick damage. Apply first.",
            "DOT - poison": "Drifting Death / Winged Death — stacks with fire DoT. Apply both.",
            "Nuke": "Blaze / Sunblaze — finisher when target is under 20% HP.",
            "Heal": "Healing Water / Word of Healing — efficient group heal.",
            "HoT": "Regrowth / Replenishment — pre-cast before fight.",
            "Buff - AC": "Skin like Nature / Barkskin — cast before any fight.",
            "Buff - regen": "Regrowth — always maintain on self and tank.",
            "Root": "Entrapping Roots — stops adds. DoT rooted targets instead of snare-kiting.",
            "Port/Evac": "Succor / Egress — emergency zone exit. Save mana for it.",
        },
        "disciplines": {},
        "aas": {
            "Innate Camouflage": "Self-invis for pulling or escaping.",
            "Convergence of Spirits": "Emergency AoE group heal.",
            "Nature's Recovery": "Fast self-regen AA.",
        },
        "innates": [
            "SoW (Spirit of Wolf) line: movement speed buff. Always maintain outdoors.",
            "Track: find specific NPCs or players by name.",
        ],
        "survival": [
            "Evac (Succor) — instant zone exit, use before wipe",
            "Root and run — root enemy, run to distance, kite",
            "Self-heal while keeping distance",
        ],
        "mana_endurance": "High mana efficiency. DoT-kite for near-free kills. Sit at < 25% mana. SoW self always.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Monk": {
        "role": "Pure melee DPS + Feign Death puller. No mana. Highest sustained melee DPS. Level 66.",
        "combat_priority": [
            "1. /attack on immediately when target acquired",
            "2. Check abilities[] — use any ready disc with disc_cmd_index",
            "3. Flying Kick: /doability 1 (or whichever slot — check doability list)",
            "4. Round Kick / Dragon Punch / Eagle Strike / Tiger Claw on cooldown via /doability",
            "5. Disc: Heel of Kanji on cooldown for burst melee damage",
            "6. Disc: Phantom Silk / Voiddancer when HP < 40% for dodge",
            "7. Disc: Innerflame when fighting single mob and HP stable",
            "8. Mend via /doability when HP < 50% — ~6min CD, use proactively",
            "9. Feign Death if HP < 20% or aggro_count > 3: /disc <FD disc_cmd_index>",
        ],
        "spell_categories": {},
        "disciplines": {
            "Heel of Kanji": "Melee damage proc burst. Use on cooldown in every fight. ~3min CD.",
            "Innerflame": "Sustained DPS disc. Use when fighting single mob and HP is stable. ~5min CD.",
            "Phantom Silk": "Dodge/avoidance disc. Use when HP drops below 40% or adds come. ~10min CD.",
            "Voiddancer": "Evasion + movement disc. Use when overwhelmed or need to reposition.",
            "Ashenhand Discipline": "Extra undead damage modifier. Use at start of every undead fight.",
            "Feign Death": "Drop to ground and shed all aggro. Use to pull singles or escape death. /disc <index>. Wait 3s then stand.",
            "Stunning Kick": "Stuns target briefly. Use to interrupt NPC spellcasting.",
        },
        "aas": {
            "Steal Essence": "Lifetap melee proc — restores HP on hits. Passive when activated.",
            "Flying Kick Mastery": "Passive: increases Flying Kick damage. Always active.",
            "Technique of Master Wu": "Chance for extra attacks on Flying Kick. Passive.",
            "Speed of the Knight": "Endurance regen boost. Passive.",
        },
        "innates": [
            "Mend: self-heal via /doability — restores ~20-30% HP, ~6min CD. Use at < 60% HP proactively.",
            "Feign Death is a discipline (check abilities[] for disc_cmd_index). After FD, wait 3s before standing.",
            "Dual wield + double attack + triple attack proc at level 66.",
            "Monks are the best pullers: FD to shed extras after tagging a group, return with single.",
            "Weight matters: keep equipped weight low for max AC and attack speed.",
        ],
        "survival": [
            "Mend (/doability) at 50% HP — don't wait for emergencies, 6min CD",
            "Phantom Silk disc at 40% HP for damage reduction",
            "Feign Death at 20% HP to fully reset: /disc <FD index> — wait 3s then stand and re-engage or run",
            "If adds are up and FD is down: /nav away from spawn, zone out if needed",
        ],
        "pulling": [
            "Run to mob cluster, hit one to tag it",
            "Immediately FD to drop aggro from all but one (the one running to check corpse)",
            "Stand and lead the single back to camp",
            "If more follow: FD again until clean",
        ],
        "mana_endurance": "No mana. Endurance recovers while standing — no need to sit unless fully depleted.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Bard": {
        "role": "Support/utility. Songs twist every 6 seconds. Buffs, slows, mezzes, haste, regen, speed.",
        "combat_priority": [
            "Twist songs — never sit idle (6-second rotation)",
            "Sustain twist: Chant of Battle (haste) + Psalm of Veeshan (regen) + Largo's Melodic Binding (slow)",
            "Mez adds: Lullaby of Morell — instant mez, no cast time if timed correctly",
            "Selo's for run speed between fights",
            "Brass instruments boost wind songs; string boost singing; drums boost percussion",
        ],
        "spell_categories": {
            "Haste song": "Chant of Battle line — group attack speed. Always in twist.",
            "Regen song": "Psalm of Veeshan / Cantata of Soothing — HP regen. Always in twist.",
            "Slow song": "Largo's Melodic Binding — slows enemy attack speed. High priority vs tough mobs.",
            "Mez song": "Lullaby of Morell / Slumber of Tembr — single or AoE mez. Stop and fully sing for reliability.",
            "Resist song": "Psalm of Cooling / Warmth — cold/fire resist. Swap in vs caster enemies.",
            "Speed song": "Selo's Accelerating Chorus — movement speed. Use between fights.",
            "DOT song": "Vulka's Lament — damage over time. Low priority; DPS is not the bard's job.",
        },
        "disciplines": {
            "Frenzy": "Melee disc for extra attacks. Use when in melee without need to twist.",
        },
        "aas": {
            "Instrument Mastery": "Passive song effectiveness boost.",
            "Jam Fest": "Group haste buff, AA version.",
        },
        "innates": [
            "Songs twist: cast 6-second songs in rotation — each one ticks once then re-cast the next",
            "AoE mezz on undead/animals with appropriate songs",
            "Bards can play instruments for enhanced song effects",
        ],
        "survival": [
            "Mez the attacker: Lullaby of Morell",
            "Run: Selo's + kite while twisting DoT/slow",
            "Disengage and re-mez",
        ],
        "mana_endurance": "Mana drains slowly while twisting. Never sit — keep twisting. Regen song restores mana too.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Rogue": {
        "role": "Pure melee DPS. Highest burst via backstab. Evade + FD to reset aggro.",
        "combat_priority": [
            "Position behind target for Backstab",
            "Disc: Kyv Strike or Twisted Chance for backstab crit bonus",
            "Sneak Attack (level-dependent) on every cooldown",
            "Evade when overaggro'd: /doability Evade",
            "Trick Backstab for highest single hit",
        ],
        "spell_categories": {},
        "disciplines": {
            "Kyv Strike": "Backstab damage multiplier. Use every cooldown for big hits.",
            "Twisted Chance": "Critical backstab chance buff. Stack with Kyv Strike timing.",
            "Assassinate": "Instant-kill skill attempt on non-undead. Rare chance but try it.",
            "Ambidexterity": "Dual wield accuracy. Use in sustained fights.",
        },
        "aas": {
            "Poison Mastery": "Passive poison damage increase.",
            "Murderous Intent": "Backstab damage boost AA.",
        },
        "innates": [
            "Backstab: must be behind the target, 8s+ cooldown — position matters",
            "Evade: /doability — drops aggro if sneak is active",
            "Poison: apply to weapon before fight via /doability",
            "Dual wield + double attack",
        ],
        "survival": [
            "Evade to drop aggro",
            "Feign Death equivalent (high level disc)",
            "No self-heal — run if HP < 25%",
        ],
        "mana_endurance": "No mana. Endurance for discs — rest between fights.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Shaman": {
        "role": "Pet + debuff + DoT specialist. Slows are critical. Best group regen. Strong solo.",
        "combat_priority": [
            "Slow the enemy FIRST: Turgur's / Listless Power — reduces enemy attack speed 60%+",
            "DoTs: Malo + Turgur's + Pox of Bertoxxulous — apply all, then let tick",
            "Pet: summon and buff before fighting",
            "Regen: Regeneration on self/tank always active",
            "Heal as needed, but slow first — it reduces damage taken dramatically",
        ],
        "spell_categories": {
            "Slow": "Turgur's / Listless Power — CRITICAL. Reduces enemy melee 60%. Always cast first in any fight.",
            "Debuff - MR": "Malo / Malosini — lowers magic resist. Cast before magic-based DoTs/slows.",
            "DOT - disease": "Pox of Bertoxxulous / Plague — very long duration ticks. Apply early.",
            "DOT - poison": "Drifting Death variant — stacks. Apply after disease DoT.",
            "Buff - haste": "Spirit of Wolf + Alacrity — haste for group melee.",
            "Buff - regen": "Regeneration / Chloroplast — HP regen, always on tank and self.",
            "Buff - stat": "Fury of the Great Bear / Girdle — STR/STA for melee.",
            "Heal": "Healing Wave / Torpor — Torpor is the best HoT in game, save for emergencies.",
            "Pet": "Companion of Necessity line — melee pet, buff before sending in.",
            "Cure": "Cure Poison / Cure Disease — cure debuffs on group.",
        },
        "disciplines": {
            "Cannibalize": "NOT a disc — it's a spell. Convert HP to mana. Use when low mana and HP > 50%.",
        },
        "aas": {
            "Rabid Bear": "Self-haste + damage AA. Use when solo melee is needed.",
            "Ancestral Aid": "Group HP recovery AA.",
        },
        "innates": [
            "Cannibalize line: trade HP for mana (very efficient mana source)",
            "Spirit shrink (high level): useful for navigation",
        ],
        "survival": [
            "Slow the attacker — single most important survival tool",
            "Torpor HoT — massive HP recovery per tick",
            "Cannibalize to recover mana for continued heals",
            "FD equivalent: none. Run if overwhelmed.",
        ],
        "mana_endurance": "Use Cannibalize when mana < 30% and HP > 50%. Otherwise sit. Never let slow drop in combat.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Necromancer": {
        "role": "Pet + DoT. Best solo class. FD for safety. Lifeburn + mana-to-HP conversions.",
        "combat_priority": [
            "Pet: summon + buff + send in",
            "DoTs: stack as many as possible — let them tick",
            "FD when HP < 30% — reset, recover, re-engage",
            "Lich (self): convert HP to mana — use when mana < 20% and HP > 60%",
            "Nuke only to finish or if fully efficient",
        ],
        "spell_categories": {
            "Pet": "Call of the Grave line — undead pet. Buff with: Augment Death + Malaise.",
            "DOT - fire": "Pyrocruor line — high fire tick DoT. Primary DPS.",
            "DOT - poison": "Venom of the Snake — stacks. Apply after fire DoT.",
            "DOT - magic": "Cascading Darkness — snare + DoT. Useful for kite slowing.",
            "Lifetap": "Blood of Thule line — heals self for portion of damage. Use when low HP.",
            "Fear": "Invoke Fear — fear kite without snare. Run behind fear.",
            "Buff - mana": "Lich / Soul Well — HP to mana conversion. Use proactively.",
            "Debuff - MR": "Malaise equivalent — lower magic resist before magic DoTs.",
            "Snare": "Dooming Darkness — snare + minor DoT. Kiting enabler.",
            "Harm Shield": "None for necromancer; FD is the emergency tool.",
        },
        "disciplines": {
            "Feign Death": "/disc or /doability — drop to ground, lose aggro. Core survivability tool.",
        },
        "aas": {
            "Lich Ward": "Extended Lich effect — more HP-to-mana efficiency.",
            "Death's Malaise": "Improved debuff AA.",
        },
        "innates": [
            "FD (Feign Death): primary escape. Use proactively when swarmed.",
            "Pet survives FD — pet holds aggro while you recover.",
            "Undead pet immune to fear, disease, and some magic.",
        ],
        "survival": [
            "FD immediately when in danger",
            "Lifetap to restore HP while pet tanks",
            "Fear kite if pet is dead",
            "Lich/Soul Well to convert HP to mana for continued casting",
        ],
        "mana_endurance": "Lich line converts HP to mana — use proactively. Sit only when Lich not sufficient.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Wizard": {
        "role": "Highest burst DPS. Pure nuke. No sustained ability — nuke, evac, nuke.",
        "combat_priority": [
            "Open with Synergism (mana-free burst) if available",
            "Nuke rotation: highest damage nuke → medium nuke while big recharges",
            "Align nuke timings to avoid mana drought",
            "If overwhelmed: Evac immediately — do not tank",
            "Bind in zone for quick re-entry after death",
        ],
        "spell_categories": {
            "Nuke - fire": "Conflagration / Lure of Flames — fire nuke. Rotate with ice.",
            "Nuke - ice": "Glacial Roar / Ice Comet — ice nuke. Ice Comet is highest single hit in game.",
            "Nuke - magic": "Mana Burn AA — converts mana to instant damage. Save for bosses.",
            "Bolt": "Sunstrike / Bolt of Karana — mid-range quick cast nuke.",
            "Evac": "Translocate / Circle of <zone> — emergency exit. Always memorized.",
            "Snare": "Minor root or magic slow — rarely used but available.",
        },
        "disciplines": {},
        "aas": {
            "Mana Burn": "Convert mana directly to damage. Max DPS window on boss targets.",
            "Fury of Magic": "Spell crit chance increase. Use before nuke rotation.",
            "Koadic's Endless Intellect": "Mana recovery AA.",
        },
        "innates": [
            "Casting speed is highest of all classes — nukes fire fast",
            "Very low HP/AC — cannot survive melee",
        ],
        "survival": [
            "Evac is first option, always",
            "Bind sight to nuke from range without being targeted",
            "Run and nuke at max range",
            "NO self-heal — Evac or die",
        ],
        "mana_endurance": "Sit at < 20% mana. Wizards go OOM fast — pace pulls. Never Mana Burn unless > 80% mana.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Magician": {
        "role": "Pet + fire nukes. Best DPS pet. Summon gear, food, drink for group.",
        "combat_priority": [
            "Pet: always summoned and buffed (Burnout + Elemental Skins + Focus)",
            "Pet does primary DPS — nuke to supplement",
            "Nuke: Bolt of Jerikor / Magma Burst on cooldown",
            "Reclaim Energy if pet dies for partial mana refund before re-summoning",
            "Summon pet armor between fights",
        ],
        "spell_categories": {
            "Pet": "Elemental pet line — fire/earth/water/air. Earth pet best for tanking; fire for DPS.",
            "Pet buff": "Burnout line — pet DPS boost. Always active on pet.",
            "Pet armor": "Summoned: Muzzle of Mardu etc. — equip pet after summoning.",
            "Nuke - fire": "Bolt of Jerikor / Conflagration — main nuke.",
            "Nuke - cold": "Lava Storm — AoE nuke (use carefully, may aggro extras).",
            "Buff - armor": "Elemental Skins / Shield of Lava — strong AC buff on group.",
            "Summon": "Can summon food, water, arrows, throwing items.",
            "Reclaim Energy": "Destroys pet, returns ~75% mana. Use if pet is about to die.",
        },
        "disciplines": {},
        "aas": {
            "Servant of Ro": "Fire elemental pet AA. Extra DPS pet.",
            "Manaburn (Mage flavor)": "Pet power AA variants.",
        },
        "innates": [
            "Pets inherit group buffs",
            "Earth pet can taunt — use as tank",
            "Air pet has stun proc",
            "Water pet has lifetap proc",
            "Fire pet highest DPS",
        ],
        "survival": [
            "Pet absorbs aggro — keep it alive",
            "Reclaim Energy before pet dies fully",
            "Re-summon and buff new pet",
            "Nuke only when pet has established aggro (wait 5-10s after send)",
        ],
        "mana_endurance": "Sit at < 20% mana. Reclaim Energy for mana emergency. Never let pet go unbuffed.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Enchanter": {
        "role": "Crowd control + haste. Mezz, slow, charm. Most powerful solo via charm pets.",
        "combat_priority": [
            "Mez all adds immediately — mez before anything else",
            "Slow: Tash + Slow on primary target",
            "Charm a strong NPC as pet if solo (highest DPS option)",
            "Haste group: Swift like the Wind on melee",
            "DoT: Color Flux + Cripple to drain enemy stats",
        ],
        "spell_categories": {
            "Mez": "Mesmerize / Cajoling Whispers — single target mez. AoE: Whirl till you Hurl.",
            "Slow": "Tepid Deeds / Shiftless Deeds — reduces enemy attack speed. Cast after tash.",
            "Debuff - MR": "Tashani / Tashania — lowers magic resist. Cast BEFORE slow/mez.",
            "Charm": "Beguile / Cajoling Whispers — charm NPC as pet. Re-charm every 3-5min.",
            "Haste": "Swift like the Wind / Alacrity — group melee haste. Always maintain.",
            "DOT": "Color Flux / Cripple — stat drain + DoT. Use on primary target.",
            "Buff - mana regen": "Clarity line — mana regen on casters. Cast on all casters.",
            "Buff - haste self": "Augmentation — self haste for melee.",
            "Root": "Root — backup CC if mez resisted.",
            "Illusion": "Cosmetic — not combat relevant.",
        },
        "disciplines": {},
        "aas": {
            "Hastened Mesmerization": "Reduced mez cast time.",
            "Beguiler's Directed Banishment": "AoE mez AA.",
        },
        "innates": [
            "Charm break: always watch for charm breaking — it WILL break. Re-charm immediately.",
            "Tash must land before slow or mez for best resist rate",
            "Mez is instant once skilled — time it right vs spell resist",
        ],
        "survival": [
            "Mez the attacker",
            "Charm a nearby NPC to fight for you",
            "Root and run",
            "NO self-heal — prevent damage via CC",
        ],
        "mana_endurance": "Clarity on self always. Sit at < 20% mana. Charm charm charm — free DPS.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Beastlord": {
        "role": "Pet + melee hybrid. Shaman-lite spells. Warder pet is always active.",
        "combat_priority": [
            "Warder pet: always summoned, buffed, and in combat",
            "Slow: Sha's Legacy / Turgur's equivalent — cast first in fight",
            "Disc: Feral Swipe for melee burst",
            "DoT: Spirit Quickening / Fang Fanatacism on target",
            "Mend Companion to heal pet mid-fight",
        ],
        "spell_categories": {
            "Pet": "Warder of <animal> line — spirit animal companion. Always active.",
            "Pet buff": "Ferocity / Primal Essence — pet damage buff. Maintain always.",
            "Slow": "Sha's Legacy / Sha's Ferocity equivalent — slow. Cast first.",
            "DOT": "Spirit Quickening / Pack Hunt — tick damage.",
            "Buff - haste self": "Elongate / Alacrity variant — self haste for melee.",
            "Heal pet": "Mend Companion — heals warder. Use when pet HP < 50%.",
            "Buff - strength": "Nature's Boon — group stat buff.",
        },
        "disciplines": {
            "Feral Swipe": "Melee attack bonus disc. Use on cooldown.",
            "Bestial Frenzy": "Self melee frenzy. High DPS window.",
        },
        "aas": {
            "Savage Spirit": "Warder + self haste AA. Use on cooldown.",
            "Bestial Alignment": "Massive pet + self buff AA. Use at fight start.",
        },
        "innates": [
            "Warder levels with you — never dismiss it",
            "Warder can tank briefly while you cast/recover",
        ],
        "survival": [
            "Slow the enemy — most important survival tool",
            "Mend Companion to keep warder alive and tanking",
            "Self-heal limited — use wisely",
            "No FD. Run if overwhelmed.",
        ],
        "mana_endurance": "Sit at < 20% mana. Warder generates free DPS — focus mana on slow + buffs.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "Berserker": {
        "role": "Pure melee DPS. Two-handed specialist. Frenzy + Axes. No mana.",
        "combat_priority": [
            "Disc: Furious Rampage for burst DPS window",
            "Disc: Reckless Abandon — trade defense for offense",
            "Throw axes between melee rounds for additional hits",
            "Frenzy on cooldown — massive hit",
            "Don't over-aggro — no tank tools, no self-heal",
        ],
        "spell_categories": {},
        "disciplines": {
            "Furious Rampage": "Short-duration max DPS window. Use at fight start every CD.",
            "Reckless Abandon": "Lose AC for damage boost. Only use when tank/healer present.",
            "Brutal Assault": "Multi-attack melee disc.",
            "Axe of Empowerment": "Throw axe ability disc — ranged DPS.",
        },
        "aas": {
            "Decapitation": "Instant-kill attempt vs stunned targets.",
            "Untamed Rage": "Self frenzy AA — massive burst damage.",
        },
        "innates": [
            "Frenzy: unique Berserker attack, different from other melee",
            "Dual wield + double attack + triple attack at high levels",
            "Thrown axe returns (ricochet) at high levels",
        ],
        "survival": [
            "No self-heal, no FD, no CC",
            "Endure Attack disc (if available) for brief DR",
            "Run if HP < 25% — class has no recovery tools",
        ],
        "mana_endurance": "No mana. Endurance powers discs — sit between fights. Never pop all discs at once.",
    },
}


def get_class_context(class_name: str) -> str:
    """
    Returns a formatted string of class knowledge for injection into a system prompt.
    class_name should match EQ class names: 'Paladin', 'Warrior', 'Cleric', etc.
    """
    key = class_name.strip().title()
    data = CLASS_KNOWLEDGE.get(key)
    if not data:
        available = ", ".join(CLASS_KNOWLEDGE.keys())
        return f"[Unknown class: {class_name}. Available: {available}]"

    lines = [
        f"## {key} Class Knowledge",
        f"**Role:** {data['role']}",
        "",
        "**Combat Priority:**",
    ]
    for i, step in enumerate(data["combat_priority"], 1):
        lines.append(f"  {i}. {step}")

    if data.get("spell_categories"):
        lines += ["", "**Spell Usage (what each type does and when to cast):**"]
        for name, desc in data["spell_categories"].items():
            lines.append(f"  - *{name}*: {desc}")

    if data.get("disciplines"):
        lines += ["", "**Disciplines (/disc command) — endurance-based combat abilities:**"]
        for name, desc in data["disciplines"].items():
            lines.append(f"  - *{name}*: {desc}")

    if data.get("aas"):
        lines += ["", "**Activated AAs (/alt activate or named command):**"]
        for name, desc in data["aas"].items():
            lines.append(f"  - *{name}*: {desc}")

    if data.get("innates"):
        lines += ["", "**Innate/Passive Abilities:**"]
        for item in data["innates"]:
            lines.append(f"  - {item}")

    if data.get("pulling"):
        lines += ["", "**Pulling Strategy:**"]
        for item in data["pulling"]:
            lines.append(f"  - {item}")

    lines += ["", "**Survival Options (in order of preference):**"]
    for item in data["survival"]:
        lines.append(f"  - {item}")

    lines += ["", f"**Mana/Endurance:** {data['mana_endurance']}"]

    return "\n".join(lines)


def list_classes() -> list[str]:
    """Returns all supported class names."""
    return list(CLASS_KNOWLEDGE.keys())


if __name__ == "__main__":
    import sys
    cls = sys.argv[1] if len(sys.argv) > 1 else "Paladin"
    print(get_class_context(cls))
    print()
    print(f"Supported classes: {', '.join(list_classes())}")
