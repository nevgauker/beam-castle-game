"""Headless checks for Journey to the Beam Castle.

Usage:
    pip install playwright && python -m playwright install chromium
    python tests/playtest.py [--chrome /path/to/chrome]

Checks:
  1. Smoke: every level loads, the player can walk, no JS errors.
  2. Reachability: every fragment is touched by some simulated *normal* jump
     (no commands) from a standing spot in the level, including points along
     each moving platform's path. Fragments inside firewall
     cages are expected to be cat-only and are reported separately.
"""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / "index.html").as_uri() + "?debug"

REACH_JS = r"""(lv)=>{G.startLevel(lv);
 const T=16,ROWS=14,map=G.map,COLS=map[0].length,S=new Set(['#','=','%','B','D']);
 const sol=(x,y)=>{const c=Math.floor(x/T),r=Math.floor(y/T);if(c<0||c>=COLS)return true;if(r<0||r>=ROWS)return false;return S.has(map[r][c])||map[r][c]==='G'};
 const spots=[];for(let c=0;c<COLS;c++)for(let r=1;r<ROWS;r++){const t=map[r][c];if((S.has(t)||t==='G')&&t!=='%'&&t!=='D'&&!S.has(map[r-1][c])&&map[r-1][c]!=='G')spots.push([c*T+4,r*T-15])}
 for(const m of G.movers)for(const f of [0,.25,.5,.75,1])for(let dx=4;dx<m.w-8;dx+=8){const mx=m.axis==='x'?m.x0+f*m.range:m.x0,my=m.axis==='y'?m.y0+f*m.range:m.y0;spots.push([mx+dx,my-15])}
 const touched=new Set(),coins=G.coins;
 for(const [sx,sy] of spots)for(const dir of [-1,0,1])for(const hold of [0,8,16,40]){
   let x=sx,y=sy,vx=0,vy=-6.1;
   for(let f=0;f<120;f++){vx=Math.max(-1.9,Math.min(1.9,vx+dir*.4));vy+=(f<hold||vy>0)?.32:.62;vy=Math.min(vy,7);
     x+=vx;if(vx>0&&(sol(x+8,y+1)||sol(x+8,y+14)||sol(x+8,y+7.5))){x=Math.floor((x+8)/T)*T-8.01;vx=0}else if(vx<0&&(sol(x,y+1)||sol(x,y+14)||sol(x,y+7.5))){x=(Math.floor(x/T)+1)*T;vx=0}
     y+=vy;if(vy>0&&(sol(x+1,y+15)||sol(x+7,y+15)))break;if(vy<0&&(sol(x+1,y)||sol(x+7,y))){y=(Math.floor(y/T)+1)*T;vy=0}
     coins.forEach((c,i)=>{if(x<c.x+c.w&&x+8>c.x&&y<c.y+c.h&&y+15>c.y)touched.add(i)})}}
 const caged=i=>{const c=coins[i],col=Math.floor((c.x+6)/T),row=Math.floor((c.y+4)/T);let l=0,r=0;for(let k=1;k<4;k++){if(map[row][col-k]==='%')l=1;if(map[row][col+k]==='%')r=1}return l&&r};
 const miss=[],cat=[];coins.forEach((c,i)=>{if(!touched.has(i))(caged(i)?cat:miss).push([Math.floor(c.x/16),Math.floor(c.y/16)])});
 return {name:G.LEVELS[lv].name,coins:coins.length,unreachable:miss,catOnly:cat}}"""

async def main():
    chrome = None
    if "--chrome" in sys.argv:
        chrome = sys.argv[sys.argv.index("--chrome") + 1]
    ok = True
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=chrome, args=["--no-sandbox"]) if chrome else await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 672})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto(URL); await pg.wait_for_timeout(500)
        n = await pg.evaluate("G.LEVELS.length")
        print("== smoke ==")
        for i in range(n):
            await pg.evaluate(f"G.startLevel({i})"); await pg.wait_for_timeout(200)
            x0 = await pg.evaluate("G.p.x")
            await pg.keyboard.down("ArrowRight"); await pg.wait_for_timeout(1200); await pg.keyboard.up("ArrowRight")
            x1, dead, st = await pg.evaluate("[G.p.x,G.deaths,G.state]")
            good = x1 > x0 + 40 and st == "play"
            ok &= good
            print(f"L{i+1} {'ok ' if good else 'FAIL'} moved {int(x1-x0)}px deaths={dead}")
        print("== reachability (normal jumps only) ==")
        for i in range(n):
            r = await pg.evaluate(REACH_JS, i)
            good = not r["unreachable"]
            ok &= good
            extra = f" cat-only={r['catOnly']}" if r["catOnly"] else ""
            print(f"L{i+1} {'ok ' if good else 'FAIL'} {r['name']}: {r['coins']} fragments, unreachable={r['unreachable']}{extra}")
        if errs:
            ok = False
            print("JS errors:", errs)
        await b.close()
    print("ALL OK" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)

asyncio.run(main())
