"""Add client-feedback cards to a DJ review page and rebuild its sections, filter bar and summary line.

Usage: python3 add_feedback.py PAGE_DIR cards.json
Images must already be in PAGE_DIR/img/.
"""
import json, re, sys
from datetime import date
from pathlib import Path
from PIL import Image

d = Path(sys.argv[1]); cards = json.load(open(sys.argv[2]))
page = d / "index.html"; s = page.read_text()

def fmt(iso):
    y, m, dd = map(int, iso.split("-")); return date(y, m, dd).strftime("%b ") + str(dd) + f", {y}"

i, j = s.index("<main>") + 6, s.index("</main>")
figs = re.findall(r'<figure class="c".*?</figure>', s[i:j])
have = {re.search(r'src="img/([^"]+)"', f).group(1) for f in figs}
for c in cards:
    if c["file"] in have: continue
    w, h = Image.open(d / "img" / c["file"]).size
    t = fmt(c["date"])
    figs.append(f'<figure class="c" data-s="Feedback"><figcaption><span class="b b-Feedback">Client Feedback</span>'
                f'<time>{t}</time></figcaption><img loading="lazy" decoding="async" width="{w}" height="{h}" '
                f'src="img/{c["file"]}" alt="Client feedback, {t}"></figure>')

def key(f):
    n = re.search(r'src="img/([^"]+)"', f).group(1)
    return n[:10] if n[:4].isdigit() else "0000"
figs.sort(key=key, reverse=True)  # stable within a date

groups = {}
for f in figs:
    k = key(f); y = k[:4] if k != "0000" else "Undated"; groups.setdefault(y, []).append(f)
main = ""
for y, fs in groups.items():
    n = len(fs); lab = (f"{n} item" if n == 1 else f"{n} items") if y == "Undated" else (f"{n} review" if n == 1 else f"{n} reviews")
    main += f'<h2 class="yr" id="y{y}"><span>{y}</span><small>{lab}</small></h2>' + "".join(fs)
s = s[:i] + main + s[j:]

# filter bar
src = [re.search(r'data-s="(\w+)"', f).group(1) for f in figs]
names = {"Knot": "The Knot", "WeddingWire": "WeddingWire", "Zola": "Zola", "Google": "Google", "Feedback": "Client Feedback"}
btn = f'<button class="on" data-f="all">All <b>{len(figs)}</b></button>' + "".join(
    f'<button data-f="{k}">{v} <b>{src.count(k)}</b></button>' for k, v in names.items() if src.count(k))
yrs = '<div class="yrs">' + "".join(f'<a href="#y{y}">{y}</a>' for y in groups) + "</div>"
s = re.sub(r'<div class="bar"><div class="in">.*?</div></div></div>', f'<div class="bar"><div class="in">{btn}{yrs}</div></div>', s, count=1, flags=re.S)

# summary line
rev = len(figs) - src.count("Feedback"); fb = src.count("Feedback")
parts = ([f"{rev} review" + ("s" if rev != 1 else "")] if rev else []) + ([f"{fb} client feedback"] if fb else [])
dated = sorted(k for k in map(key, figs) if k != "0000")
mon = lambda k: date(int(k[:4]), int(k[5:7]), 1).strftime("%B %Y")
rng = mon(dated[-1]) if mon(dated[-1]) == mon(dated[0]) else f"{mon(dated[-1])} back to {mon(dated[0])}"
s = re.sub(r'<p class="sub">[^<]*', f'<p class="sub">{" + ".join(parts)} · {rng} · newest first', s, count=1)
page.write_text(s)
print(d.name, " + ".join(parts), "|", rng)
