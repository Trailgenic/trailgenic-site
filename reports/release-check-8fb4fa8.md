# Release check: 8fb4fa8

Deployment: https://trailgenic-site-7rigszo7h-trailgenics-projects.vercel.app (dpl_GbiTesArDJ8JrgW2ajHfA1rMDdez, READY)
Checked 2026-11-12 ~01:55 UTC.

## Freeze and final sync
- Webflow last published 2026-11-11T20:59:21Z, both at the start and the end of the freeze.
- Final snapshot 2026-11-12T01:49Z: every response identical to the first snapshot (only the timestamp in manifest.json changed).
- No new Webflow-hosted files. Sitewide head and footer code re-read from Webflow: contained unchanged in all 318 pages.
- convert.py and build.mjs produced no source change. Local parity: 321/321 identical.

## Remote parity against the unique deployment address
The unique address sits behind Vercel's login, so the GitHub-run check
(reports/parity-remote.md) records 302 to the login page for every address and
fails, as designed. The check was run instead from a browser signed in to Vercel:

| Check | Result |
|---|---|
| Pages (sitemap + /find, /search-index, /style-guide, robots, llms, sitemap) | 321/321 return 200, no redirect; SHA-256 equal to the build for 320. The homepage differs only by Vercel's preview toolbar tag appended after `</html>` on protected preview addresses; with it removed, the hash equals the build. |
| Files referenced by pages and the stylesheet | 772/772 return 200 |
| Not-found addresses | 10/10 return 404 |
| Redirects | 6/6 land on the expected page (browser cannot read the 301 code; 301 status verified on the public production alias in reports/parity-remote.md history at 01:37Z) |

## Smoke tests (same inputs on live Webflow and on the deployment)
- /find: "San Gorgonio" 2 results, "LMNT" 3 results, "type:science autophagy" 1 result; identical results and order on both.
- Calculator, age 50, resting HR 60, 8 mi, 3,000 ft, 200 min, avg HR 130, HRV 35: both show 41–46, midpoint 43, VO2max ≈ 40, 62% heart-rate reserve.
