# Journey to the Beam Castle

A neon pixel platformer where you code your way to the castle: build bridges,
light caves, freeze time and defeat the Corrupted Compiler with your own functions.

**Play:** open `index.html` in any modern browser. No install, no build.

## Controls
← → / A D move · Space jump · **Enter** open the laptop and type code ·
Esc pause · **F** fullscreen · M mute. Touch controls appear on phones and
tablets (play in landscape).

## Run locally
Double-click `index.html`, or serve the folder (recommended, closer to production):
```bash
python3 -m http.server 8000      # then open http://localhost:8000
```

## Deploy (pick one)

### itch.io (best for games: built-in fullscreen button, game page, comments)
1. Create a free account at itch.io → **Upload new project**.
2. Kind of project: **HTML**. Upload a ZIP that contains `index.html` at the root
   (`zip game.zip index.html`).
3. Tick **"This file will be played in the browser"**.
4. Embed options: viewport **1280 × 720**, tick **Fullscreen button** and
   **Mobile friendly** (orientation: landscape).
5. Save → set visibility to **Public**.

### GitHub Pages (free, your own URL)
1. Create a repo (e.g. `beam-castle`) and push this folder.
2. Repo **Settings → Pages** → Source: *Deploy from a branch* → `main` / root.
3. Your game is live at `https://<user>.github.io/beam-castle/` in a minute or two.

### Netlify Drop (fastest, no account needed to try)
Go to app.netlify.com/drop and drag this folder onto the page. You get a URL
instantly; sign up to keep it and pick a custom name.

### Vercel / Cloudflare Pages
Import the repo; framework preset **Other / None**; no build command; output
directory = root.

## Fullscreen
- Press **F** or click **⛶ FULLSCREEN** (bottom-right). The game scales to fill
  the screen at 16:9 with crisp pixels.
- Browsers only allow fullscreen from a click/keypress on a top-level page. If the
  game is embedded in an iframe (e.g. on a site you don't control), the iframe
  needs `allow="fullscreen"`. itch.io adds its own fullscreen button.
- Phones: hold landscape; on Android the game also tries to lock landscape when
  entering fullscreen. iPhone Safari doesn't support page fullscreen. Use
  "Add to Home Screen" for a fuller view.

## Develop with Claude Code
- `CLAUDE.md` holds the project rules Claude Code reads automatically.
- `docs/GAME_DESIGN.md` is the full design spec (systems, constants, commands,
  every level, art palette, code map, how-tos, backlog).
- `tests/playtest.py` runs headless checks:
  ```bash
  pip install playwright && python -m playwright install chromium
  python tests/playtest.py
  ```

Example prompts:
- "Add Level 8 'The Server Garden' that teaches variables (`let n = 5; bridge(n)`).
  Follow the Jump Rule and the teaching pattern in GAME_DESIGN.md."
- "Add a level editor page that exports a `buildLx` function."
- "Add gamepad support and remappable keys."
