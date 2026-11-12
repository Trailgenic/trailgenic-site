#!/usr/bin/env python3
"""Check the built site against the live-site snapshot, file by file.

Every page in public/ must equal the snapshot page with only the self-hosting
rewrite applied (Webflow file addresses -> /cdn/ copies, integrity hashes
recomputed). Text files must be byte-identical. Writes reports/parity-local.json.
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

os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
json.dump(results, open(os.path.join(ROOT, "reports", "parity-local.json"), "w"), indent=1)
print({k: len(v) for k, v in results.items()})
if results["different"] or results["missing"]:
    print("FIRST PROBLEMS:", (results["different"] + results["missing"])[:10])
    sys.exit(1)
