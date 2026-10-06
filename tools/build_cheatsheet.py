"""Render the notebook's 📘 blocks (Book.sections) as one static page: docs/cheatsheet.html (GitHub Pages)."""
import html
import re

PAGE_URL = "https://stanislavsidorovich.github.io/pandas-analyst-path/cheatsheet.html"


def _inline(text):
    codes = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"
    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", text)
    return re.sub("\x00(\\d+)\x00", lambda m: codes[int(m.group(1))], text)


def _cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def md_to_html(md):
    """Just enough Markdown for the lesson blocks: tables, bullets (with continuation lines), paragraphs."""
    lines = [l[2:] if l.lstrip().startswith("- |") and l.startswith("- ") else l for l in md.split("\n")]
    lines = [l.strip() if l.strip().startswith("|") else l for l in lines]
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not re.match(r"^\|[\s|:-]+\|$", r)]
            t = ["<div class='tw'><table><thead><tr>"]
            t += [f"<th>{_inline(c)}</th>" for c in _cells(head)]
            t.append("</tr></thead><tbody>")
            for r in body:
                t.append("<tr class='it'>" + "".join(f"<td>{_inline(c)}</td>" for c in _cells(r)) + "</tr>")
            out.append("".join(t) + "</tbody></table></div>")
        elif s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                buf = [lines[i].strip()[2:]]
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and not lines[i].strip().startswith(("- ", "|")):
                    buf.append(lines[i].strip())
                    i += 1
                items.append(f"<li class='it'>{_inline(' '.join(buf))}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("- ", "|")):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p class='it'>{_inline(' '.join(buf))}</p>")
    return "\n".join(out)


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e3e3e0;--code:#f0efe9;--accent:#2f6fde;--mark:#ffe58a}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--card:#1d1d20;--ink:#ececee;--muted:#a0a0a8;--line:#2e2e33;--code:#2a2a2f;--accent:#7aa7ff;--mark:#6b5a12}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px 10px}
.wrap{max-width:980px;margin:0 auto}
h1{font-size:18px;margin:0 0 8px}
h1 small{color:var(--muted);font-weight:400}
input{width:100%;font:inherit;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
nav{display:flex;gap:6px;overflow-x:auto;padding-top:8px;scrollbar-width:none}
nav a{flex:none;font-size:13px;color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:3px 10px;background:var(--card)}
main{padding:8px 16px 40px}
h2{font-size:15px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin:26px 0 8px;scroll-margin-top:120px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:4px 14px 10px;margin:10px 0;scroll-margin-top:120px}
h3{font-size:16px;margin:10px 0 6px}
h3 span{color:var(--accent);margin-right:6px}
p,ul{margin:6px 0}
ul{padding-left:20px}
code{font:13px/1.4 ui-monospace,Consolas,monospace;background:var(--code);padding:1px 4px;border-radius:4px;overflow-wrap:anywhere}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;margin:6px 0;font-size:14px}
th,td{text-align:left;vertical-align:top;padding:5px 8px;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--muted)}
mark{background:var(--mark);color:inherit}
.hide{display:none!important}
#none{color:var(--muted);padding:20px 0}
"""

JS = """
const q=document.getElementById('q'),none=document.getElementById('none');
const its=[...document.querySelectorAll('.it')];its.forEach(e=>e.dataset.h=e.innerHTML);
function run(){const w=q.value.trim().toLowerCase();let any=false;
 its.forEach(e=>{e.innerHTML=e.dataset.h;const hit=!w||e.textContent.toLowerCase().includes(w);e.classList.toggle('hide',!hit);
  if(hit&&w){const re=new RegExp('('+w.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','gi');
   const tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);const ns=[];while(tw.nextNode())ns.push(tw.currentNode);
   ns.forEach(n=>{if(re.test(n.data)){const s=document.createElement('span');s.innerHTML=n.data.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])).replace(re,'<mark>$1</mark>');n.replaceWith(s)}re.lastIndex=0})}});
 document.querySelectorAll('section').forEach(s=>{const v=!w||s.querySelector('.it:not(.hide)');s.classList.toggle('hide',!v);if(v)any=true;
  s.querySelectorAll('table').forEach(t=>t.closest('.tw').classList.toggle('hide',!!w&&!t.querySelector('.it:not(.hide)')))});
 document.querySelectorAll('h2').forEach(h=>{let n=h.nextElementSibling,v=false;while(n&&n.tagName==='SECTION'){if(!n.classList.contains('hide'))v=true;n=n.nextElementSibling}h.classList.toggle('hide',!v)});
 none.classList.toggle('hide',any)}
q.addEventListener('input',run);
const p=new URLSearchParams(location.search).get('q');if(p){q.value=p;run()}
"""


def build_page(sections, part_titles):
    parts = {}
    for sid, sec in sections.items():
        if sec["md"] and sid != "A.1" and sid != "A.5":
            parts.setdefault(sec["part"], []).append((sid, sec))
    nav, body = [], []
    for part, secs in parts.items():
        anchor = part.lower().replace(" ", "")
        label = part.replace("Part ", "") if part.startswith("Part") else "Cheat sheet · errors · glossary"
        nav.append(f"<a href='#{anchor}'>{html.escape(label)}</a>")
        body.append(f"<h2 id='{anchor}'>{html.escape(part)} · {html.escape(part_titles.get(part, ''))}</h2>")
        for sid, sec in secs:
            body.append(f"<section id='s{sid}'><h3><span>{sid}</span>{_inline(sec['title'])}</h3>\n"
                        f"{md_to_html(sec['md'])}</section>")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pandas Cheat Sheet</title><style>{CSS}</style></head>
<body><header><div class="wrap"><h1>📋 Pandas Analyst Path <small>· cheat sheet, built from the lessons</small></h1>
<input id="q" type="search" placeholder="Search: index, merge, NaN, KeyError…" autocomplete="off">
<nav>{''.join(nav)}</nav></div></header>
<main class="wrap">{''.join(body)}<p id="none" class="hide">Nothing found. Try a shorter word.</p></main>
<script>{JS}</script></body></html>
"""
