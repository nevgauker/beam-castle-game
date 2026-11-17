# Journey to the Beam Castle — Game Design Spec

> Living design document. Keep it in sync with `index.html` whenever you change a
> system, a constant or a level. Section numbers are referenced from `CLAUDE.md`.

---

## 1. Vision

A short, cozy-but-clever **2D pixel platformer** where the hero is a coder. Instead of
picking up power-ups, you **open your laptop and type code** to change the world:
build bridges, light caves, freeze time, and finally write your own functions.

- **Fantasy:** "I solve problems with code" — a caped developer and their cat travel
  from a cliff under a pink tree to a castle that beams light into the night sky.
- **Origin:** the art direction is taken from the author's LinkedIn cover image
  (neon pixel night, pink tree, purple mountains, cyan-beam castle, blue moon). The
  ending screen deliberately recreates that image.
- **Audience:** developers and curious non-developers; one sitting (~20–30 min).
- **Platform:** browser, single HTML file, keyboard first, touch supported.

### Design pillars
1. **Code is the power-up.** Every new ability is a command typed into the laptop
   terminal. No hidden buttons.
2. **One new idea per level.** Teach safely → test it → combine it with old ideas.
3. **The world tells you when you need code.** Normal jumps never reach anything
   that requires a skill (see the *Jump Rule*, §4.2). If a jump feels impossible, it is.
4. **Programming concepts, gently.** Calls → arguments → loops → conditionals →
   timing → functions. Each command teaches a real concept without lecturing.
5. **You and your cat.** The cat is a companion with its own role (fetching,
   sensing secrets, boosting with you), not decoration.

---

## 2. Story

The castle's **beam** is the signal that keeps the world's code running. A glitch —
the **Corrupted Compiler** — is wrapped around the beam's core, spilling bugs,
glitch spikes and corrupted pixels across the land. The coder and their cat are the
only ones who can debug it.

- **Start:** the Pink Tree Cliff (the LinkedIn cover).
- **Journey:** foothills → clouds → caverns → storm peak → castle walls.
- **Climax:** inside the Core, defeat the Corrupted Compiler using functions.
- **Ending:** the beam turns clean cyan; final tableau of the coder and cat under the
  pink tree looking at the restored castle ("THE BEAM IS RESTORED").

---

## 3. Controls

| Input | Action |
|---|---|
| ← → / A D | Move |
| Space / ↑ / W | Jump (hold for full height, tap for short hop) |
| Enter (also `/` or `T`) | Open the laptop terminal |
| Esc (in terminal) | Close terminal |
| ↑ ↓ (in terminal) | Command history |
| Esc / P | Pause (then R = restart level, Q = back to map) |
| F | Toggle fullscreen |
| M | Mute |
| Map: ← → | Select level · Enter/Space to play |
| Touch | On-screen ◀ ▶ JUMP `>_` (terminal) `II` (pause); tap map nodes |

The game **pauses while the terminal is open** — typing is never a race against
physics.

---

## 4. Core mechanics

### 4.1 Resolution & grid
- Internal canvas **400 × 224 px**, tiles **16 px**, **14 rows** per level (no vertical
  scrolling; levels scroll horizontally only).
- Scaled to the window keeping aspect ratio; integer scale when close to one,
  otherwise fractional to fill the screen. `image-rendering: pixelated`.
- Fixed 60 Hz simulation (accumulator loop), rendering every animation frame.

### 4.2 Player physics (the Jump Rule)
| Constant | Value |
|---|---|
| Hitbox | 8 × 15 px (sprite 12 × 16) |
| Run accel / max speed | 0.4 / 1.9 px·f⁻¹, friction ×0.7 when idle |
| Gravity (holding jump / falling) | 0.32 px·f⁻² |
| Gravity (jump released while rising) | 0.62 (short hop) |
| Jump velocity | −6.1 → **max rise ≈ 58 px (3.6 tiles)** |
| Boost jump velocity | −8.3 → **max rise ≈ 108 px (6.7 tiles)** |
| Max fall speed | 7 |
| Coyote time / jump buffer | 6 / 7 frames |
| Horizontal reach of a normal jump | ≈ 4.5 tiles |

**THE JUMP RULE (mandatory for all level design):**
- Normal platforming steps are **at most 2 tiles up** (32 px). Comfortable, no
  pixel-perfect timing.
- **Never 3 tiles** with a normal jump (technically reachable, feels like a bug).
- **4+ tiles = a deliberate "skill wall"** solved by `jump.boost()`, `stairs(n)`, a
  lift, or a bridge. Put a sign before the first wall of each kind.
- Normal gaps: ≤ 4 tiles wide. 5+ tiles = needs `bridge(n)`/stairs/moving platform.
- Each fragment `</>` must be reachable with normal jumps from some platform near
  it (except fragments intentionally locked behind a firewall for `cat.fetch()`).

### 4.3 RAM (command budget)
- Every command costs RAM (see §5). RAM regenerates **0.12 per frame (~7.2/s)**.
- Default max **100**. Level themes can lower it (`theme.ram`, The Castle Walls = 70).
- On respawn RAM is topped up to at least 60.
- Insufficient RAM → `OutOfMemoryError` in the terminal, nothing happens.
- Functions run their commands at **70% cost** (`costMul = 0.7`).

### 4.4 Death, checkpoints, saving
- Death: falling below the screen, red glitch spikes `^`, touching a bug from the
  side, glitch bolts, beams, the boss body.
- Respawn at the last checkpoint flag after ~50 frames. Built bridges/stairs stay;
  killed bugs stay dead; timers (boost, light, shield, wait) reset; chaser moths
  and bolts are cleared.
- Progress is saved in `localStorage` key **`beamcastle-v2`**:
  `{unlocked:number, done:{[levelIndex]:{frags,total,time,deaths}}, finished?:bool}`.
  Change the key name only with a migration plan.

### 4.5 The cat
- Follows the player with its own physics; auto-jumps when blocked or when the
  player is higher. While `jump.boost()` is active, the cat also gets super jumps
  (−8.6) and an orange glow.
- Fallback: teleports to the player (with sparkles) if it falls or is >170 px away.
- States: `follow`, `fetch` → `return` (carries an item), `lead` → `back`
  (reveals a hidden path). While leading, its eyes light the dark.
- `cat.pet()` is an easter egg (hearts).

---

## 5. Commands (the skill tree)

Commands are typed in the laptop terminal. Parsing lower-cases input and strips
whitespace and trailing semicolons. A command is usable when
`CMDS[x].lvl <= currentLevel + 1`; otherwise the terminal says where it unlocks.

| Command | Unlocks | RAM | Concept | Effect |
|---|---|---|---|---|
| `bridge(n)` | L1 | 4 / block | arguments | Builds up to *n* (1–12) blocks at foot level in the facing direction, starting at the nearest edge (walks up to 10 tiles to find it). |
| `debug()` | L1 | 25 | calling a function | Zaps all bugs/moths within 160 px and nests within 170 px. Zero targets = free. |
| `jump.boost()` | L2 | 35 | methods | 10 s of super jumps for you **and the cat**. |
| `cat.fetch()` | L2 | 20 | objects | Cat flies (through walls) to the key within 300 px, else the nearest fragment within 220 px, and brings it back. |
| `stairs(n)` | L3 | 6 / step | **loops** | Builds *n* (1–8) blocks rising diagonally (1 across, 1 up) from the edge ahead. Logs `for (let i = 0; i < n; i++) step(i);`. Fails if a wall is directly ahead — design pits/gaps in front of stair walls. |
| `light()` | L4 | 20 | — | 8 s large light radius in darkness. |
| `cat.lead()` | L4 | 15 | **conditionals** | Logs `if (cat.senses(secret)) cat.reveal(secret);`. If an unrevealed hidden-tile group is within 340 px, the cat runs to it and reveals it (pink outline, glow). |
| `shield()` | L5 | 40 | — | 6 s bubble: destroys bugs/moths/nests on touch and blocks glitch bolts. Does **not** protect from spikes, beams or falling. |
| `wait(n)` | L6 | 12 / s | **timing** | Freezes the *world clock* for *n* (1–5) s: beams/pulses, sweepers, moving platforms, glitch tiles, bolts, bugs, nests and the boss. A frozen ON beam stays deadly — freeze when it's dark. |
| `function f(){ a; b; }` | L7 | 70% of total | **functions** | Saves a named list of commands (only the commands above, no nesting). Call with `f()`. Returns the set of commands that succeeded — the boss checks this set. |
| `help()` / `clear()` | always | 0 | — | Lists learned commands / clears the log. |
| `cat.pet()`, `sudo …` | always | 0 | easter eggs | Hearts / "Permission denied". |

**Adding a command:** add an entry to `CMDS` (with `lvl`), add a branch in `run()`
(validate → `learned()` → `pay()` → effect → `ok()`/`er()`), add it to `tokenOf()` if it
can go inside functions, add it to `RESERVED`, show it in the HUD if it has a timer,
and teach it with a sign in its unlock level.

---

## 6. World objects

### 6.1 Tile legend (`map[row][col]`)
| Char | Meaning | Solid |
|---|---|---|
| `.` | empty | no |
| `#` | ground (drawn per theme: rock, violet, cloud, cave, peak, brick, core) | yes |
| `=` | stone platform | yes |
| `B` | code block from `bridge`/`stairs` | yes |
| `%` | firewall (pink grid) — blocks the player, the cat flies through | yes |
| `D` | gate (opens with the key) | yes |
| `^` | glitch spikes — deadly, not solid | no |
| `H` | hidden passage — **looks like ground, is not solid**; revealed by `cat.lead()` | no |
| `G` | glitch tile — solid only while ON (`(wclock + offset) % 250 < 180`); flickers white for 40 frames before switching off | toggles |

### 6.2 Entities
- **Fragments `</>`** — collectibles; count shown per level and on the map.
- **Key** — opens the level's `D` gate; usually locked in a firewall cage.
- **Signs** — tiny terminals; standing near shows a hint (HTML overlay, supports
  `<code>`). The **primary teaching tool**.
- **Checkpoints** — flags; touching activates (cyan).
- **Exit** — waypoint arch (default), ruin gate (with key), or castle door (`door`).
- **Bugs** — ground patrol between two columns; stomp from above or `debug()`.
- **Glitch moths** — fly in a sine pattern around an anchor.
- **Chaser moths** — spawned by nests/boss; home in on the player.
- **Nests** — spawn up to 3 chasers while the player is within 240 px; destroyed by
  `debug()` or by touching them with `shield()`.
- **Movers** — moving platforms (`axis 'x'|'y'`, range in tiles, cosine easing);
  player and cat ride them (one-way from above). Drawn as clouds or stone slabs.
- **Glitch bolts** — spawned in bolt zones near the player; 45-frame flashing pink
  warning marker + dotted line, then fall fast.
- **Beam pulses** — vertical beams from the top to the first solid tile. Rhythm:
  `period`, `on` frames, `offset`; 36-frame flicker warning. **Sweepers** move
  between two columns with the same on/off rhythm.
- **Crystals / moon shafts** — light sources in dark levels.
- **Dark zones** — column ranges where darkness fades in (used in L7).

---

## 7. Levels

Every level: one or two new skills, signs teach them, checkpoints every ~25–40
columns, 12–18 fragments, ends at an exit. Coordinates are `(col)` / `h` = ground
height in tiles from the bottom (top surface row = `14 − h`).

### L1 · The Pink Tree Cliff — *bridge(n), debug()*
Theme: the LinkedIn cover (pink tree, blue rock ground with orange flecks, purple
mountains, distant castle). 124 cols, 14 fragments.
1. Move/jump tutorial, two-step platforms (2 tiles each).
2. 7-tile gap — sign gives the exact answer `bridge(7)`.
3. RAM explanation sign; two patrol bugs (stomp or `debug()`).
4. 5-tile gap — sign says "count the gap" (no number).
5. First spikes; platform pairs; final 6-tile gap with a bug waiting on the far
   side (bridge, then debug). Exit arch.

### L2 · Violet Foothills — *jump.boost(), cat.fetch()*
Purple ground, ruins and hills in the background. 172 cols, 17 fragments.
1. 4-tile ledge: the first skill wall → `jump.boost()` (the cat boosts too).
2. Fragment in a firewall cage → `cat.fetch()`.
3. Bug, small platform, bridge reminder (count the gap).
4. Terraces in 2-tile steps; floating platforms down; spike field (3-wide patch).
5. Key in a firewall cage on a pillar → `cat.fetch()`; 10-tile gap (bridge);
   **ruin gate** opens with the key.

### L3 · Cloud Steps — *stairs(n)*
Floating cloud islands over a lethal sea of clouds; castle at eye level. 180 cols,
18 fragments.
1. `stairs(4)` over a gap up to a higher island (answer given).
2. Drifting horizontal cloud; rising/sinking lift to the high cloud.
3. Glitch moths; a trail of small clouds with a moving one; storm-cloud spikes.
4. Gap + tall cloud: "one step per tile of gap" → `stairs(5)` (number not given).
5. Final drifting cloud, a bridge from a small cloud, exit.

### L4 · Moonlit Caverns — *light(), cat.lead()*
Dark cave (darkness overlay, player sees ~46 px radius), ceiling with stalactites,
crystals and moonlight shafts. 170 cols, 15 fragments.
1. `light()` tutorial; bridge in the dark.
2. Bugs visible only when lit.
3. Dead-end wall → hidden passage at floor level → `cat.lead()`.
4. Pit + 5-tile ledge → `stairs(5)` or boost.
5. Second hidden passage on the upper ledge; spikes; moving stone slab.
6. Final hidden wall before the exit ("you know who to ask").

### L5 · The Glitch Peak — *shield()*
Storm sky with lightning flashes and glitch noise; violet-magenta rock. 180 cols,
14 fragments.
1. Bolt zone → keep moving or `shield()`.
2. 12-tile glitch floor over the void (all tiles share one phase: cross right after
   it turns on).
3. Glitch nest spawning chaser moths → `shield()` bash or `debug()`.
4. Spikes, bug; three staggered glitch steps up to the summit inside a bolt zone
   (offsets 0 / 200 / 150).
5. Summit with another nest; 8-tile bridge; final bolt zone; exit.

### L6 · The Castle Walls — *wait(n)* · **RAM max 70**
Giant castle and beam in the background, brick ramparts with lit windows. 190 cols,
12 fragments.
1. Two pulsing beams → dash between pulses or `wait(3)`.
2. Bridge, pulse, sweeper.
3. Steps with three staggered pulses.
4. Glitch floor under a sweeper → `wait(4)` to freeze both.
5. 4-tile tower → boost (cat follows); a wave of four pulses (`wait(5)`).
6. Lift up to the top walls; pulse + sweeper; **castle door** exit.

### L7 · The Core — *function*
Interior: circuit-grid background, cyan-edged tiles. 140 cols, 5 fragments.
1. **Halls of Memory** (remixes): two void gaps (bridges) · a dark room with a
   hidden wall · bolts + nest · glitch floor under a pulse.
2. **Boss arena** (cols 115–139): entering col 118 activates the boss, seals the
   wall behind (col 114), locks the camera and moves the checkpoint into the arena.

#### Boss · The Corrupted Compiler
- One-eyed glitch mass (eye tracks the player), tendrils into a corrupted beam
  column, 3 HP pips. Touching it kills.
- **Immune to single commands** — `debug()` alone is rejected. Only a **function**
  whose successful commands include the phase requirement deals a hit.
- Phase requirements (`BREQ`):
  1. **Armor:** `shield()` + `debug()` — hint shows a full example function.
  2. **Darkness:** arena goes dark; bolts start → `light()` + `debug()`.
  3. **Fury:** floor between the safe pads becomes staggered glitch tiles over the
     void; faster bolts and moths → `jump.boost()` + `shield()` + `debug()`.
- 150-frame invulnerability after each hit (screen shake, particles).
- Missing commands → "rejected: missing …" in the terminal.
- Death plays a dissolve + white flash, then `finishGame()` → ending.

### Ending
Recreates the LinkedIn cover: pink tree, cliff, coder sitting with the glowing
laptop, cat beside them, castle with a bright restored beam, sparkles. Text: "THE
BEAM IS RESTORED", total fragments, thanks. Enter → map ("THE JOURNEY · COMPLETE ✓").

---

## 8. World map
- Seven nodes on a pixel trail from the pink tree (left) to the castle (right):
  `NODES` in canvas coordinates.
- Node colors: cyan = done (✓), pink = open, gold = coming soon, grey + lock = locked.
- The character and cat walk between nodes; after a level clear they walk to the
  newly unlocked node automatically.
- Bottom panel: level name, new skills, description, best fragments/time.

---

## 9. Art direction

**Look:** neon pixel night. Deep navy sky, purple mountains, cyan glow, pink accents,
warm orange rim light from the laptop and the cape.

| Role | Hex |
|---|---|
| Sky top / mid / bottom | `#070a26` · `#0f1240` · `#1d1658` |
| Cyan (beam, UI, code) | `#39e6ff` · light `#9ff6ff` · `#7ff3ff` |
| Pink accent | `#ff5ad1` · `#ff4fd8` · tree `#ff4f8b` `#c22d6a` |
| Danger red/magenta | `#ff2d6a` |
| Gold (keys, highlights) | `#ffd23a` |
| Orange rim / boost | `#ff8a3d` · `#e0562f` |
| Purple mountains | `#2a1c70` · `#3d2a98` · ridge `#6a44e0` · near `#a45bff` |
| Cape red | `#e63a2e` · `#a21f2a` |

- Sprites are defined as **string arrays + palettes** (`makeSprite`), pre-rendered
  and mirrored once. Everything else is drawn with `fillRect` — no image files.
- Fonts: *Press Start 2P* (titles), *VT323* (UI/terminal) from Google Fonts.
- Subtle scanlines over everything; parallax: stars 0.03, far ridge 0.15, near 0.35.
- Each level has a theme object (§10.3) that selects backgrounds and tile style.

## 10. Audio
WebAudio bleeps only (no files): `sfx(name)` — jump, boost, coin, stomp, die,
build, zap, check, key, win, type, err, step, select, meow, light, shield, freeze,
reveal, boss, bosshit. Audio starts on the first key/tap. `M` mutes.

---

## 11. Code architecture (`index.html`)

One self-contained file: HTML overlays + CSS + one IIFE script. Sections are marked
with `/* ---------- name ---------- */` comments, in this order:

| Section | Key items |
|---|---|
| utils / save / audio | `mulberry32`, `hash`, `prog`, `save()`, `beep`, `sfx` |
| sprites | palettes, `PTOP`/`LEGS` (player), cat, bug, moth, key, digits, moon, tree, ridges |
| commands & levels | `CMDS`, `RESERVED`, `tokenOf`, `BREQ`, `LEVELS`, `makeApi()`, `buildL1…buildL7` |
| state | globals, `startLevel(i)`, `die`, `respawn`, `levelClear`, `finishGame` |
| terminal | `run(raw)` (all command parsing), `callFunc`, `bossTry`, `openTerm` |
| UI | `toast`, `updateHUD`, `setHint`, `showScreens` |
| world map | `NODES`, `updateMapUI`, `enterMap`, `mapSelect`, `mapPlay` |
| input | keyboard, pointer, touch buttons |
| update | `update()`, `updatePlayer`, `ride`, `updateCat`, `updateBugs`, `updateHazards`, `updateBoss` |
| render | tiles, themes, entities, `drawDarkness`, `renderLevel`, `renderMap`, `renderEnding` |
| fullscreen / layout & loop | `toggleFS`, `resize`, fixed-timestep `frame` |

### 11.1 State machine
`title → map → play ⇄ paused → clear → map` · `play → ending → map` (after the
boss). The terminal (`termOpen`) pauses `play`.

### 11.2 Level API (`makeApi`) — used inside `buildLx(L)`
```
COLS = n                         // level width in tiles (set first)
L.ground(c0,c1,h)                // solid from the bottom, h tiles high
L.island(c0,c1,h,thick=3)        // floating cloud island (top row 14-h)
L.cloud(c0,c1,row)               // 2-row floating cloud
L.plat(c,row,w)                  // stone platform
L.ceiling(c0,c1)                 // cave ceiling (rows 0–1, random row 2)
L.wall(c0,c1,r0,r1) / L.hidden(c0,c1,r0,r1)   // solid / secret passage tiles
L.cage(c0,c1,rTop,rBot)          // firewall box (put a coin or key inside)
L.set(c,row,ch)                  // raw tile, e.g. '^' spikes
L.glitch(c0,c1,row,offset=0)     // glitch tiles (phase offset in frames)
L.coin(c,row) · L.key(c,row) · L.sign(c,h,html) · L.check(c,h)
L.bug(c,colA,colB,h=3) · L.moth(c,row,ampTiles) · L.nest(c,h)
L.mover(c,row,wTiles,'x'|'y',rangeTiles,speed=.02)   // negative range = up/left
L.pulse(c,period,on,offset) · L.sweeper(c0,c1,speed)
L.boltZone(c0,c1,rateFrames) · L.darkZone(c0,c1) · L.crystal(c,row) · L.shaft(c)
L.exit(c,h) · L.door(c,h) · L.gate(c,r0,r1) · L.arena(c0,c1)
```
`startLevel` calls the builder twice (first pass only reads `COLS`), so builders
must be deterministic. The spawn point is column 2, on the first floor below any
ceiling.

### 11.3 Level theme object
```
theme:{ tile:'rock'|'violet'|'cloud'|'cave'|'peak'|'brick'|'core',
        tree, ruins, hills, sky, cave, dark, storm, castle, core,  // background flags
        cS, cE, cY,            // background castle: screen-x start/end (0–1), base y
        farY, nearY,           // ridge baselines
        ram }                  // RAM max override
```

### 11.4 World clock
`wclock` advances every frame unless `wait()` is active (`freezeT > 0`). Use
`wclock` (never `tick`) for anything `wait()` should freeze: movers, glitch tiles,
pulses, bolts, bugs, nests, boss timers.

### 11.5 Debug hook (for automated tests)
Open `index.html?debug` to expose `window.G` (live getters: `p`, `cat`, `map`,
`coins`, `state`, `deaths`, `ram` (settable), `boss`, `movers`, `pulses`, `wclock`,
`LEVELS`, `startLevel(i)`, …) and `window.RUN(cmd)` to run terminal commands.

---

## 12. How-tos

### Add a new level
1. Write `buildL8(L)` next to the others; set `COLS` first.
2. Add an entry to `LEVELS` (`name`, `desc`, `skills`, `build`, `theme`).
3. Add a map node to `NODES` (and adjust landmarks in `renderMap`).
4. If it introduces a command, add it (§5) with `lvl: 8` and teach it with a sign.
5. Follow the Jump Rule and the teaching pattern: safe intro → test → combine.
6. Run `tests/playtest.py` (smoke + reachability) and play it yourself.

### Tune difficulty
- Gaps/heights: the Jump Rule. Timing windows: pulse `period/on`, glitch phase
  (`glitchPh`: 250-frame cycle, ON for 180), mover speed.
- Pressure: bolt zone `rate`, nest spawn interval (150 frames), boss timers in
  `updateBoss` (spawn 210/260/200, bolts 75/55).
- Budget: `RAM_REGEN`, command costs in `run()` and `CMDS`, `theme.ram`.

---

## 13. Backlog / ideas
- **Level editor** (paint tiles in the browser, export a `buildLx` function).
- Hard mode / speedrun timer with leaderboard (needs a backend).
- Collectible "dev log" story lines for 100% fragments per level.
- Variables: `let n = 5; bridge(n)`; `while`/`for` syntax for stairs.
- Gamepad support; remappable keys; colorblind palette for danger vs. safe.
- Split the single file into modules (`/src`) with a tiny build step if it grows
  past ~2,500 lines.
- More cat abilities (`cat.sit()` on pressure plates, `cat.scout()` camera peek).
- Accessibility: reduced flashing option (storm lightning, boss flashes).
