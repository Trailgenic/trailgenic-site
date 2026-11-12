#!/usr/bin/env python3
"""Check a deployed copy of the site against the snapshot and the build.

Usage: BASE=https://trailgenic-site.vercel.app python3 tools/parity_remote.py
(run after `node build.mjs`, so public/ holds the exact files that were deployed)

For every address the live Webflow site answered when the snapshot was taken:
  200 pages and files  -> must return 200 with exactly the built bytes
  301 redirects        -> must return 301 to the same target (/about -> /about-us-new by design)
  404 addresses        -> must still return 404
Also checks every self-hosted file, the cited addresses, trailing-slash handling,
and that the 404 page is the built one. Writes reports/parity-remote.json and .md.
"""
import concurrent.futures as cf
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from convert import page_file  # noqa: E402

BASE = os.environ["BASE"].rstrip("/")
PUB = os.path.join(ROOT, "public")
UA = "Mozilla/5.0 TrailGenicParityCheck/1.0"
INTENDED = {"/about": "/about-us-new"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def get(path, method="GET"):
    url = BASE + urllib.parse.quote(path, safe="/%:@&=+$,;~!*'()-._")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            try:
                r = OPENER.open(req, timeout=60)
            except urllib.error.HTTPError as e:
                r = e
            body = r.read() if method == "GET" else b""
            if r.headers.get("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
            return r.code, r.headers.get("Location"), body
        except Exception as e:
            if attempt == 3:
                return 0, str(e), b""
            time.sleep(2 * (attempt + 1))


def loc_path(loc):
    if not loc:
        return None
    return urllib.parse.urlparse(urllib.parse.urljoin(BASE + "/", loc)).path


def main():
    pages = json.load(open(os.path.join(ROOT, "snapshot", "manifest.json")))["pages"]
    checks = []
    for path, rec in pages.items():
        if rec["status"] == 200:
            local = os.path.join(PUB, page_file(path) if "html" in (rec["content_type"] or "") else path.lstrip("/"))
            checks.append(("page", path, 200, open(local, "rb").read(), None))
        elif rec["status"] in (301, 302, 308):
            target = INTENDED.get(path, loc_path(rec["location"]))
            checks.append(("redirect", path, 301, None, target))
        else:
            checks.append(("not_found", path, 404, None, None))
    nf = open(os.path.join(PUB, "404.html"), "rb").read()
    for sample in ("/hiking/", "/science/trailgenic-method/", "/prevention/"):
        checks.append(("trailing_slash", sample, 308, None, sample.rstrip("/")))
    for dirpath, _, files in os.walk(os.path.join(PUB, "cdn")):
        for f in files:
            checks.append(("file", "/" + os.path.relpath(os.path.join(dirpath, f), PUB).replace(os.sep, "/"), 200, None, None))

    def run(c):
        kind, path, want, body, target = c
        status, loc, got = get(path, "HEAD" if kind == "file" else "GET")
        ok = status == want
        note = ""
        if ok and body is not None and got != body:
            ok, note = False, f"content differs ({len(got)} vs {len(body)} bytes)"
        if ok and target is not None and loc_path(loc) != target:
            ok, note = False, f"redirects to {loc_path(loc)}, expected {target}"
        if ok and kind == "not_found" and got != nf:
            ok, note = False, "404 page differs from built 404.html"
        if not ok and not note:
            note = f"status {status}, expected {want}" + (f" ({loc})" if status == 0 else "")
        return {"kind": kind, "path": path, "ok": ok, "status": status, "note": note}

    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(run, checks))

    cited = [l.strip() for l in open(os.path.join(ROOT, "snapshot", "inputs", "cited_paths.txt")) if l.strip()]
    by_path = {r["path"]: r for r in results if r["kind"] == "page"}
    cited_ok = [p for p in cited if by_path.get(p, {}).get("ok")]

    summary = {}
    for r in results:
        s = summary.setdefault(r["kind"], {"checked": 0, "passed": 0})
        s["checked"] += 1
        s["passed"] += r["ok"]
    failures = [r for r in results if not r["ok"]]
    report = {"base": BASE, "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "summary": summary, "cited": {"checked": len(cited), "passed": len(cited_ok)},
              "failures": failures}
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    json.dump(report, open(os.path.join(ROOT, "reports", "parity-remote.json"), "w"), indent=1)
    lines = [f"# Parity check against {BASE}", "", f"Checked {report['checked_utc']}.", "",
             "| Check | Passed | Checked |", "|---|---:|---:|"]
    for k, s in summary.items():
        lines.append(f"| {k} | {s['passed']} | {s['checked']} |")
    lines.append(f"| cited addresses (Grokbot panel) | {len(cited_ok)} | {len(cited)} |")
    lines += ["", f"Failures: {len(failures)}"] + [f"- `{f['path']}` ({f['kind']}): {f['note']}" for f in failures[:200]]
    open(os.path.join(ROOT, "reports", "parity-remote.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))
    print("failures", len(failures))
    missing_cited = sorted(set(cited) - set(cited_ok))
    if failures or missing_cited:
        print(f"PARITY FAILED: {len(failures)} failed comparison(s), {len(missing_cited)} cited address(es) not passing",
              missing_cited[:20])
        sys.exit(1)


if __name__ == "__main__":
    main()
