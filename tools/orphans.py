#!/usr/bin/env python3
"""List pages that few or no other pages link to. Run after `node build.mjs`.

Counts links in each built page's <body> to other pages on the site, then writes
reports/orphans.md: pages with no inbound links, pages with one, and groups of
pages that share the same meta description. It reports; it does not fail the build.
"""
import collections
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")
SKIP = {"/", "/404", "/find", "/search-index"}

pages = {}
for d, _, files in os.walk(PUB):
    if os.path.relpath(d, PUB).split(os.sep)[0] == "cdn":
        continue
    for f in files:
        if f.endswith(".html"):
            p = "/" + os.path.relpath(os.path.join(d, f), PUB)[:-5].replace(os.sep, "/")
            pages["/" if p == "/index" else p] = open(os.path.join(d, f), encoding="utf-8").read()

inbound = collections.defaultdict(set)
for p, s in pages.items():
    body = s[s.lower().find("<body"):]
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    for h in set(re.findall(r'<a\b[^>]*href="(?:https://www\.trailgenic\.com)?(/[^"#?]*)', body)):
        h = h.rstrip("/") or "/"
        if h != p and h in pages:
            inbound[h].add(p)


def title(p):
    m = re.search(r"<title>([^<]*)", pages[p])
    return html.unescape(m.group(1)).strip() if m else ""


zero = sorted(p for p in pages if p not in SKIP and not inbound[p])
one = sorted(p for p in pages if p not in SKIP and len(inbound[p]) == 1)
desc = collections.defaultdict(list)
for p, s in pages.items():
    m = re.search(r'<meta\b[^>]*name="description"[^>]*>', s)
    c = re.search(r'content="([^"]*)"', m.group(0)) if m else None
    if c and c.group(1).strip():
        desc[html.unescape(c.group(1)).strip()].append(p)
dups = {k: sorted(v) for k, v in desc.items() if len(v) > 1}

out = ["# Orphan and thin-link inventory", "",
       f"Built pages: {len(pages)}. Pages with no inbound links: {len(zero)}. Pages with exactly one: {len(one)}.",
       "Each page should be resolved in context: link it where it helps a reader, merge it, or retire it.", "",
       "## No inbound links", ""]
out += [f"- `{p}` — {title(p)}" for p in zero] or ["- none"]
out += ["", "## Exactly one inbound link", ""]
out += [f"- `{p}` — linked only from `{next(iter(inbound[p]))}`" for p in one] or ["- none"]
out += ["", "## Pages sharing one meta description", ""]
for k, v in sorted(dups.items(), key=lambda x: -len(x[1])):
    out += [f"- {len(v)} pages share: \"{k[:110]}…\"", *[f"  - `{p}`" for p in v]]
if not dups:
    out.append("- none")
os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
open(os.path.join(ROOT, "reports", "orphans.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"no inbound: {len(zero)}, one inbound: {len(one)}, shared descriptions: {len(dups)} group(s)")
print("prevention inbound:", len(inbound["/prevention"]), "| longevity inbound:", len(inbound["/longevity"]))
