#!/usr/bin/env python3
"""Snapshot the live TrailGenic site exactly as served.

Seeds from the sitemap, the Webflow redirect export, cited addresses and a few
known special paths, then follows internal links. Every response is stored
byte for byte with its status, redirect target and key headers, so the new
build can be compared against what production actually served.
"""
import concurrent.futures as cf
import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ORIGIN = "https://www.trailgenic.com"
OUT = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0 Safari/537.36 TrailGenicMigrationSnapshot/1.0")
MAX_PAGES = 2500

EXTRA = [
    "/", "/robots.txt", "/llms.txt", "/sitemap.xml", "/search-index", "/find",
    "/about-us-new", "/about-us", "/style-guide", "/ai-crawl-ping",
    "/.well-known/tool-registry.json", "/.well-known/ai-plugin.json",
    "/this-page-should-not-exist-404-check", "/favicon.ico",
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    for attempt in range(4):
        try:
            try:
                resp = OPENER.open(req, timeout=40)
            except urllib.error.HTTPError as e:
                resp = e
            body = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
            return resp.status if hasattr(resp, "status") else resp.code, dict(resp.headers), body
        except Exception as e:  # network hiccup or rate limit: back off
            if attempt == 3:
                return 0, {"error": str(e)}, b""
            time.sleep(2 * (attempt + 1))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.add(v)


def internal_paths(base, html):
    p = Links()
    try:
        p.feed(html)
    except Exception:
        pass
    out = set()
    for href in p.links:
        u = urllib.parse.urljoin(base, href)
        pu = urllib.parse.urlparse(u)
        if pu.hostname in ("www.trailgenic.com", "trailgenic.com") and pu.scheme in ("http", "https"):
            path = pu.path or "/"
            if re.search(r"\.(png|jpe?g|gif|webp|svg|ico|css|js|pdf|mp3|mp4|woff2?)$", path, re.I):
                continue
            out.add(path)
    return out


def store_path(path):
    path = urllib.parse.unquote(path)
    if path.endswith("/"):
        path += "index.html"
    elif not os.path.splitext(path)[1]:
        path += "/index.html"
    return os.path.join(OUT, "raw", path.lstrip("/"))


def main():
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
    seeds = set(EXTRA)
    st, _, body = fetch(ORIGIN + "/sitemap.xml")
    for loc in re.findall(r"<loc>(.*?)</loc>", body.decode("utf-8", "replace")):
        seeds.add(urllib.parse.urlparse(loc.strip()).path or "/")
    for f in ("redirects.csv", "cited_paths.txt"):
        fp = os.path.join(OUT, "inputs", f)
        if os.path.exists(fp):
            for line in open(fp, encoding="utf-8"):
                tok = line.strip().split(",")[0]
                if tok.startswith("/"):
                    seeds.add(tok)

    seen, queue, manifest = set(), list(seeds), {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        while queue and len(seen) < MAX_PAGES:
            batch = [p for p in dict.fromkeys(queue) if p not in seen][:64]
            queue = [p for p in queue if p not in seen and p not in batch]
            if not batch:
                break
            seen.update(batch)
            for path, (status, headers, body) in zip(batch, ex.map(lambda p: fetch(ORIGIN + urllib.parse.quote(p, safe="/%:@&=+$,;~!*'()-._")), batch)):
                rec = {
                    "status": status,
                    "location": headers.get("Location") or headers.get("location"),
                    "content_type": headers.get("Content-Type") or headers.get("content-type"),
                    "x_robots_tag": headers.get("X-Robots-Tag"),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "bytes": len(body),
                }
                manifest[path] = rec
                if body:
                    dest = store_path(path)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(dest, "wb") as fh:
                        fh.write(body)
                if rec["location"]:
                    loc = urllib.parse.urlparse(urllib.parse.urljoin(ORIGIN + path, rec["location"]))
                    if loc.hostname in ("www.trailgenic.com", "trailgenic.com"):
                        queue.append(loc.path or "/")
                if status == 200 and "html" in (rec["content_type"] or ""):
                    for p in internal_paths(ORIGIN + path, body.decode("utf-8", "replace")):
                        if p not in seen:
                            queue.append(p)
            print(f"fetched {len(seen)} queued {len(queue)}", flush=True)

    # Host behaviour: bare domain and http should both land on https://www
    hosts = {}
    for u in ("https://trailgenic.com/", "http://trailgenic.com/", "http://www.trailgenic.com/",
              "https://trailgenic.com/hiking", "https://trailgenic.com/.well-known/tool-registry.json"):
        s, h, _ = fetch(u)
        hosts[u] = {"status": s, "location": h.get("Location") or h.get("location")}

    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump({"origin": ORIGIN, "taken_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "pages": dict(sorted(manifest.items())), "hosts": hosts}, fh, indent=1)
    counts = {}
    for r in manifest.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("done", len(manifest), counts)


if __name__ == "__main__":
    main()
