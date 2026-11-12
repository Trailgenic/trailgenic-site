# TrailGenic: Webflow to Vercel migration

Scope: parity only. The new site serves the same addresses with the same page
content as Webflow served at snapshot time. Editorial corrections are on their
own track (see "Logged for the correction track").

## How the copy was made

1. `tools/snapshot.py` (run on GitHub's servers by `.github/workflows/snapshot.yml`)
   fetched every address in the live sitemap, the Webflow redirect export, the
   Grokbot cited addresses and a few special paths, and followed internal links.
   It stored each response byte for byte with its status and redirect target
   (`snapshot/manifest.json`, `snapshot/raw/`).
2. `tools/fetch_assets.py` (`.github/workflows/assets.yml`) downloaded every
   Webflow-hosted file the pages and stylesheets use into `assets/cdn/`.
3. `tools/convert.py` pointed those references at the self-hosted copies,
   recomputed integrity hashes, and split the four blocks shared by every page
   into `src/partials/`. Pages went to `src/pages/`.
4. `build.mjs` reassembles the pages into `public/`.
5. `tools/parity_local.py` proves the build equals the snapshot with only the
   self-hosting rewrite applied. `tools/parity_remote.py`
   (`.github/workflows/parity.yml`) checks the deployed site address by address.

## Intended differences from Webflow

| Change | Why |
|---|---|
| `/about` redirects to `/about-us-new` | Webflow sent it to `/about-us`, which does not exist. Approved by Mike. |
| Webflow-hosted files served from `/cdn/...` on trailgenic.com | Removes the dependency on Webflow's file servers. In meta tags and JSON-LD the address is absolute (`https://www.trailgenic.com/cdn/...`). |
| Integrity hashes on the stylesheet and scripts recomputed | The stylesheet now points at self-hosted copies, so its bytes changed. |

Everything else (text, markup, JSON-LD, canonicals, hreflang, inline scripts,
llms.txt, robots.txt, sitemap.xml with its dates) is unchanged.

## Verified production behaviour carried over (or confirmed inactive)

| Address | Live on Webflow | New site |
|---|---|---|
| `/llms.txt` | 200, served by Webflow | 200, same bytes |
| `/robots.txt`, `/sitemap.xml` | 200 | 200, same bytes |
| `/find` (search) and `/search-index` | 200; search runs in the browser over `/search-index` | same pages, same behaviour |
| `/.well-known/tool-registry.json`, `/.well-known/ai-plugin.json` | 404 on root and www (Webflow's "Invalid .well-known request") | 404. The Cloudflare program meant to answer this path cannot run: root and www are DNS-only records, and Cloudflare programs only run on proxied records. Restoring it is a separate-track decision. |
| `/ai-crawl-ping` | 404 (no handler anywhere) | 404. Restoring a counter is a separate-track decision. |
| `trailgenic.com/*` | 301 to `https://www.trailgenic.com/*` | Same, via the Vercel domain redirect set at cutover |
| Unknown address | 404 with Webflow's default "Page not found" page | 404 with the same page, files self-hosted |

## Cutover (Mike)

Prerequisites: Ella has recorded PASS against the release commit and preview,
and the final sync below is done.

1. **Vercel:** project `trailgenic-site` → Settings → Domains. Add
   `www.trailgenic.com`. Add `trailgenic.com` and choose **Redirect to
   www.trailgenic.com** (permanent). Vercel shows the DNS values it wants for each.
2. **Cloudflare** (the account holding trailgenic.com) → DNS. Change only these two:

   | Record | Today (Webflow), the rollback values | Change to |
   |---|---|---|
   | `trailgenic.com`, type A | `198.202.211.1`, DNS only | the A value Vercel shows, DNS only |
   | `www.trailgenic.com`, type CNAME | `cdn.webflow.com`, DNS only | the CNAME value Vercel shows, DNS only |

   Keep both on **DNS only** (grey cloud). Do not touch `app`, `mcp`, `alerts`,
   `gear-intel`, `tools`, any MX or TXT record, or the leftover NS lines.
3. Tell Claude. Claude re-runs the parity check against `https://www.trailgenic.com`
   and checks the Ella app, the MCP health check and its datasets, the
   calculator widget, and the root-to-www redirect.
4. Leave the Webflow site published and the plan active for 60-90 days.

## Rollback

Set the two records back to the "Today" values above (A `198.202.211.1`,
CNAME `cdn.webflow.com`, both DNS only). Webflow is still published, so the old
site is back as soon as DNS updates, usually within minutes.

## Final sync (before cutover)

Webflow stays open for publishing during review. Before cutover: short freeze,
then push a new line to `snapshot/REQUEST` (re-snapshot), refresh
`snapshot/inputs/site-head.html` and `site-footer.html` from Webflow's
sitewide custom code, re-run the asset download if new files appear, run
`python3 tools/convert.py`, `node build.mjs`, `python3 tools/parity_local.py`,
and re-run the remote parity check. Every edit since the first snapshot,
including the 9 and 11 November hub changes, is picked up because the whole
site is re-captured, not patched.

## Logged for the correction track (unchanged at cutover)

- Internal links to addresses that already return 404 on Webflow:
  `/biomarker-index-how-to-calculate` (from two biomarker pages),
  `/playbooks/does-eating-break-autophagy-on-fasted-hike` (from a nutrition review),
  `/podcast-episodes` (from the podcast hub),
  `/science/fasted-hiking-autophagy` (from a science article; the live article is
  `/science/fasted-hiking-autophagy-w56d8`).
- A Webflow placeholder image that already fails to load, on `/style-guide`,
  `/science/research-datasets` and `/science/hormesis-in-the-field`.
- `/style-guide` is public and holds Webflow's sample forms.
- `/favicon.ico` returns 404 (the site sets its icon in the page head instead).
- A leftover preconnect hint to Webflow's file server on every page; harmless.
- The crawl ping in the sitewide footer calls an address that returns 404.
- The Fasted Hiking Playbook PDF that Perplexity cited
  (`cdn.prod.website-files.com/687dbbd9b5ac024294bb3226/6983e360f3721341a6ac1565_Fasted%20Hiking%20Playbook.pdf`)
  still resolves on Webflow's file server. No current TrailGenic page links to it
  (the site links the 2026 edition). A TrailGenic-hosted copy is at
  `/cdn/wf/687dbbd9b5ac024294bb3226/6983e360f3721341a6ac1565_Fasted-Hiking-Playbook.pdf`.
