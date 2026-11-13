#!/usr/bin/env python3
"""List what the build changes compared with the cutover snapshot.

At cutover every page had to match the snapshot exactly. Since then, edits are
intended, so this script reports which pages differ (for the reviewer) and fails
only if a page disappeared without being listed in tools/changes.json.
Writes reports/parity-local.json and reports/changes-since-cutover.md.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import convert  # noqa: E402

PUB = os.path.join(ROOT, "public")
manifest = json.load(open(os.path.join(ROOT, "snapshot", "manifest.json")))
pages = manifest["pages"]
results = {"identical": [], "different": [], "missing": [], "webflow_refs_left": {}}

for p, r in pages.items():
    if r["status"] != 200:
        continue
    raw = convert.raw_file(p) if "html" in (r["content_type"] or "") else os.path.join(ROOT, "snapshot", "raw", p.lstrip("/"))
    if "html" in (r["content_type"] or ""):
        built = os.path.join(PUB, convert.page_file(p))
        expected = convert.fix_integrity(convert.rewrite(open(raw, encoding="utf-8").read())).encode()
    else:
        built = os.path.join(PUB, p.lstrip("/"))
        expected = open(raw, "rb").read()
    if not os.path.exists(built):
        results["missing"].append(p)
        continue
    actual = open(built, "rb").read()
    (results["identical"] if actual == expected else results["different"]).append(p)
    left = re.findall(r"https://(?:cdn\.prod\.website-files\.com|d3e54v103j8qbb\.cloudfront\.net|app-assets\.website-files\.com)[^\s\"'<>]*",
                      actual.decode("utf-8", "replace"))
    if left:
        results["webflow_refs_left"][p] = sorted(set(left))

REMOVED = set(json.load(open(os.path.join(ROOT, "tools", "changes.json"))).get("removed_pages", []))
unexpected_missing = [p for p in results["missing"] if p not in REMOVED]
os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
md = ["# Changes since the 2026-11-11 cutover", "",
      f"- Pages unchanged: {len(results['identical'])}",
      f"- Pages changed: {len(results['different'])}",
      f"- Pages removed on purpose: {len([p for p in results['missing'] if p in REMOVED])}",
      f"- Pages missing without being listed: {len(unexpected_missing)}", "", "## Changed pages", ""]
md += [f"- `{p}`" for p in sorted(results["different"])]
md += ["", "## Removed pages", ""] + [f"- `{p}`" for p in sorted(results["missing"])]
open(os.path.join(ROOT, "reports", "changes-since-cutover.md"), "w").write("\n".join(md) + "\n")
json.dump(results, open(os.path.join(ROOT, "reports", "parity-local.json"), "w"), indent=1)
print({k: len(v) for k, v in results.items()})
if unexpected_missing:
    print("PAGES MISSING WITHOUT BEING LISTED IN tools/changes.json:", unexpected_missing[:20])
    sys.exit(1)
