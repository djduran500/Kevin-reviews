"""Render client-feedback cards as 941px-wide WebP images matching the existing site cards.

Usage: python3 render_feedback.py cards.json OUTDIR
cards.json: [{"file": "2025-10-27_Feedback_Kerri-and-Peter.webp", "name": "Kerri and Peter",
              "kind": "Wedding", "text": "..."}]
"""
import json, sys, html, io
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{background:#fff;font-family:Inter,sans-serif;width:941px}
.card{position:relative;padding:30px 36px 38px 36px;background:#fff}
.av{position:absolute;left:36px;top:30px;width:60px;height:60px;border-radius:50%;background:#5e2a95;color:#fff;
 font:600 22px/60px Inter,sans-serif;text-align:center}
.nm{margin-left:78px;padding-top:6px;font:600 18.5px/23px Inter,sans-serif;color:#1a1a1a}
.kd{margin-left:80px;margin-top:4px;font:400 15px/20px Inter,sans-serif;color:#8a8a8a}
.pill{position:absolute;right:36px;top:45px;height:30px;padding:0 12px;border:1.5px solid #6b3fa0;border-radius:999px;
 color:#573474;font:600 13.5px/27px Inter,sans-serif}
.st{margin-top:24px;color:#f5b301;font-size:20px;letter-spacing:2px}.st+.tx{margin-top:8px}.tx{margin-top:29px;padding-right:28px;font:400 17px/28px Inter,sans-serif;color:#262626;white-space:pre-line}
</style></head><body><div class="card"><div class="av">{I}</div><div class="nm">{N}</div><div class="kd">{K}</div>
<div class="pill">{P}</div>{S}<div class="tx">{T}</div></div></body></html>"""

cards = json.load(open(sys.argv[1]))
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 941, "height": 400})
    for c in cards:
        h = (TPL.replace("{I}", html.escape(c["name"][0].upper()))
                .replace("{N}", html.escape(c["name"]))
                .replace("{K}", html.escape(c.get("kind", "Wedding")))
                .replace("{T}", html.escape(c["text"]))
                .replace("{P}", html.escape(c.get("pill", "Client feedback")))
                .replace("{S}", '<div class="st">★★★★★</div>' if c.get("stars") else ""))
        pg.set_content(h)
        pg.evaluate("document.fonts.ready")
        png = pg.locator(".card").screenshot()
        im = Image.open(io.BytesIO(png)).convert("RGB")
        im.save(out / c["file"], "WEBP", quality=90)
        print(c["file"], im.size)
    b.close()
