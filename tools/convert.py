#!/usr/bin/env python3
"""Turn the live-site snapshot into editable site source.

Run after tools/snapshot.py and tools/fetch_assets.py. It:
  1. points every Webflow-hosted file at its self-hosted copy under /cdn/
     (absolute https://www.trailgenic.com/cdn/... inside meta tags and JSON-LD,
     because outside readers need full addresses there),
  2. rewrites Webflow addresses inside the downloaded stylesheets and scripts,
  3. recomputes integrity hashes for self-hosted files,
  4. replaces blocks shared by every page with partial markers,
  5. writes one source file per page to src/pages/ and text files to src/static/.

Nothing else is changed: the build (build.mjs) reverses step 4 and the parity
check confirms the output matches the snapshot with only step 1-3 applied.
"""
import base64
import collections
import hashlib
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from fetch_assets import PATTERN  # noqa: E402

SNAP = os.path.join(ROOT, "snapshot")
SRC = os.path.join(ROOT, "src")
SITE = "https://www.trailgenic.com"
AMAP = json.load(open(os.path.join(ROOT, "tools", "asset-map.json")))["map"]

SITE_HEAD = open(os.path.join(SNAP, "inputs", "site-head.html"), encoding="utf-8").read()
SITE_FOOTER = open(os.path.join(SNAP, "inputs", "site-footer.html"), encoding="utf-8").read()


def _sub(text, absolute):
    def repl(m):
        u = m.group(0)
        tail = ""
        while u.endswith(")") and u.count("(") < u.count(")"):
            u, tail = u[:-1], ")" + tail
        while u and u[-1] in ".;":
            u, tail = u[:-1], u[-1] + tail
        key = html.unescape(u)
        lp = AMAP.get(key)
        if lp is None:
            return m.group(0)
        return (SITE + lp if absolute else lp) + tail
    return PATTERN.sub(repl, text)


LDJSON = re.compile(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', re.S | re.I)
META = re.compile(r"<meta\b[^>]*>", re.I)


def rewrite(text):
    text = LDJSON.sub(lambda m: m.group(1) + _sub(m.group(2), True) + m.group(3), text)
    text = META.sub(lambda m: _sub(m.group(0), True), text)
    return _sub(text, False)


def page_file(path):
    if path == "/":
        return "index.html"
    return path.strip("/") + ".html"


def raw_file(path):
    return os.path.join(SNAP, "raw", (path.lstrip("/") + ("index.html" if path.endswith("/") else "/index.html")))


INTEGRITY = re.compile(r'<(?:script|link)\b[^>]*?(?:src|href)="(/cdn/[^"]+)"[^>]*?integrity="(sha\d+)-[^"]+"', re.I)


def fix_integrity(text):
    def repl(m):
        local, algo = m.group(1), m.group(2)
        fp = os.path.join(ROOT, "assets", local.split("?")[0].lstrip("/"))
        digest = base64.b64encode(hashlib.new(algo, open(fp, "rb").read()).digest()).decode()
        whole = m.group(0)
        return re.sub(r'integrity="sha\d+-[^"]+"', f'integrity="{algo}-{digest}"', whole)
    return INTEGRITY.sub(repl, text)


def most_common(values):
    c = collections.Counter(v for v in values if v)
    return c.most_common(1)[0] if c else (None, 0)


def main():
    # 2. stylesheets and scripts we host now point at our own copies
    for dirpath, _, files in os.walk(os.path.join(ROOT, "assets", "cdn")):
        for f in files:
            if f.endswith((".css", ".js")):
                fp = os.path.join(dirpath, f)
                t = open(fp, encoding="utf-8", errors="surrogateescape").read()
                n = _sub(t, False)
                if n != t:
                    open(fp, "w", encoding="utf-8", errors="surrogateescape").write(n)

    manifest = json.load(open(os.path.join(SNAP, "manifest.json")))["pages"]
    html_pages = [p for p, r in manifest.items()
                  if r["status"] == 200 and "html" in (r["content_type"] or "")]
    text_files = [p for p, r in manifest.items()
                  if r["status"] == 200 and "html" not in (r["content_type"] or "")]

    pages = {p: fix_integrity(rewrite(open(raw_file(p), encoding="utf-8").read())) for p in html_pages}
    not_found = fix_integrity(rewrite(open(raw_file("/this-page-should-not-exist-404-check"), encoding="utf-8").read()))

    site_head = fix_integrity(rewrite(SITE_HEAD))
    site_footer = fix_integrity(rewrite(SITE_FOOTER))

    # Shared Webflow blocks: the script tags before the site footer, and the head
    # block from the viewport tag to the site head code.
    def scripts_of(t):
        i = t.find(site_footer)
        j = t.rfind('<script src="/cdn/wfjs/', 0, i)
        return t[j:i] if i > 0 and j > 0 else None

    def headbase_of(t):
        i = t.find(site_head)
        j = t.find('<meta content="width=device-width, initial-scale=1" name="viewport"/>')
        return t[j:i] if i > 0 and 0 < j < i else None

    scripts, n_scripts = most_common(scripts_of(t) for t in pages.values())
    headbase, n_head = most_common(headbase_of(t) for t in pages.values())
    partials = {"site-head": site_head, "site-footer": site_footer,
                "webflow-scripts": scripts, "webflow-head": headbase}
    print(f"shared blocks: webflow-scripts on {n_scripts} pages, webflow-head on {n_head} pages")

    for d in ("pages", "partials", "static"):
        shutil.rmtree(os.path.join(SRC, d), ignore_errors=True)
        os.makedirs(os.path.join(SRC, d))
    for name, body in partials.items():
        if "<!--@partial" in body:
            raise SystemExit(f"partial {name} contains a marker")
        open(os.path.join(SRC, "partials", name + ".html"), "w", encoding="utf-8").write(body)

    def to_source(t):
        # longest blocks first so nested matches never split a larger block
        for name, body in sorted(partials.items(), key=lambda kv: -len(kv[1])):
            t = t.replace(body, f"<!--@partial {name}-->")
        return t

    counts = collections.Counter()
    for p, t in pages.items():
        dest = os.path.join(SRC, "pages", page_file(p))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        s = to_source(t)
        counts.update(re.findall(r"<!--@partial ([\w-]+)-->", s))
        open(dest, "w", encoding="utf-8").write(s)
    open(os.path.join(SRC, "pages", "404.html"), "w", encoding="utf-8").write(to_source(not_found))

    for p in text_files:
        shutil.copyfile(os.path.join(SNAP, "raw", p.lstrip("/")), os.path.join(SRC, "static", p.lstrip("/")))

    print(f"pages {len(pages)} + 404, text files {len(text_files)}, partial uses {dict(counts)}")


if __name__ == "__main__":
    main()
