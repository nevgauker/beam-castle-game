# CLAUDE.md — Journey to the Beam Castle

A browser pixel platformer where the hero types code into a laptop to change the
world. **Read `docs/GAME_DESIGN.md` before changing gameplay.** It is the source of
truth for systems, constants, commands and level layouts.

## Project layout
- `index.html` — the entire game (HTML overlays + CSS + one IIFE script). No build
  step, no dependencies except Google Fonts.
- `docs/GAME_DESIGN.md` — design spec. Update it in the same change whenever you
  change a constant, a command, a level layout or a system.
- `tests/playtest.py` — headless Playwright checks (smoke for every level, fragment
  reachability for normal jumps).

## Rules
1. **Keep it a single self-contained file** unless asked to split it. No external
   scripts, images or network calls (fonts are the only exception).
2. **The Jump Rule (GAME_DESIGN §4.2):** normal platform steps ≤ 2 tiles up, never
   3; 4+ tiles must be a deliberate skill wall with a sign before the first one.
   Gaps ≤ 4 tiles for normal jumps.
3. **One new idea per level:** teach with a sign → test → combine. Signs are the
   tutorial; keep them short and put commands in `<code>`.
4. Anything `wait(n)` should freeze must run on `wclock`, not `tick`.
5. New commands: `CMDS` entry (with `lvl`), branch in `run()` using `learned()`,
   `pay()`, `ok()`/`er()`; add to `tokenOf()` + `RESERVED` if it can be used inside
   functions; HUD timer if it has a duration.
6. Level builders must be deterministic (they run twice). Set `COLS` first.
7. Don't rename the save key `beamcastle-v2` without migrating old saves.
8. Pixel art stays procedural (string-array sprites + `fillRect`). Use the palette in
   GAME_DESIGN §9.
9. The game pauses while the terminal is open. Keep it that way.

## Testing
```bash
pip install playwright && python -m playwright install chromium
python tests/playtest.py            # smoke + reachability, must print "ALL OK"
```
For targeted checks open `index.html?debug` and use `window.G` (state getters,
`G.startLevel(i)`, settable `G.ram`) and `window.RUN('bridge(5)')`. Teleport the
player with `Object.assign(G.p,{x:col*16+4,y:topRow*16-15})`.

Always play a changed level manually too, since feel can't be fully automated.

## Style
- Plain modern JS, compact one-liners are fine but keep functions named and
  grouped under the existing `/* ---------- section ---------- */` headers.
- Player-facing text: friendly, short, no jargon beyond the command names.
