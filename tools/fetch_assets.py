#!/usr/bin/env python3
"""Download every Webflow-hosted file the site uses and record where it lives now.

Input: tools/asset-urls.txt (one URL per line). Stylesheets and scripts are
scanned for further Webflow-hosted files, which are fetched too. Output files go
under assets/cdn/, and tools/asset-map.json maps each original URL to its
new site path.
"""
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOSTS = {
    "cdn.prod.website-files.com": "wf",
    "app-assets.website-files.com": "wfapp",
    "d3e54v103j8qbb.cloudfront.net": "wfjs",
    "uploads-ssl.webflow.com": "wfup",
}
PATTERN = re.compile(r"https://(?:cdn\.prod\.website-files\.com|app-assets\.website-files\.com|"
                     r"d3e54v103j8qbb\.cloudfront\.net|uploads-ssl\.webflow\.com)/[^\s\"'<>\\,]+")


def find_urls(text):
    """Webflow file names can contain parentheses; drop only unbalanced closers."""
    out = []
    for u in PATTERN.findall(text):
        while u.endswith(")") and u.count("(") < u.count(")"):
            u = u[:-1]
        out.append(u.rstrip(".;"))
    return out
UA = "Mozilla/5.0 TrailGenicMigrationAssets/1.0"


def local_path(url):
    u = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(u.path)
    path = re.sub(r"[^A-Za-z0-9._/-]+", "-", path).strip("/")
    return f"/cdn/{HOSTS[u.hostname]}/{path}"


def get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, b""
        except Exception:
            time.sleep(2 * (attempt + 1))
    return 0, b""


def main():
    todo = [l.strip() for l in open(os.path.join(ROOT, "tools", "asset-urls.txt")) if l.strip()]
    done, mapping, failed = set(), {}, {}
    while todo:
        batch = [u for u in dict.fromkeys(todo) if u not in done]
        todo = []
        done.update(batch)
        with cf.ThreadPoolExecutor(max_workers=12) as ex:
            for url, (status, body) in zip(batch, ex.map(get, batch)):
                if status != 200:
                    failed[url] = status
                    continue
                lp = local_path(url)
                dest = os.path.join(ROOT, "assets", lp.lstrip("/"))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as fh:
                    fh.write(body)
                mapping[url] = lp
                if re.search(r"\.(css|js)$", urllib.parse.urlparse(url).path):
                    for found in find_urls(body.decode("utf-8", "replace")):
                        if found not in done:
                            todo.append(found)
        print(f"downloaded {len(mapping)} failed {len(failed)}", flush=True)
    with open(os.path.join(ROOT, "tools", "asset-map.json"), "w") as fh:
        json.dump({"map": dict(sorted(mapping.items())), "failed": failed}, fh, indent=1)
    print("done", len(mapping), "failed", failed)


if __name__ == "__main__":
    main()
