# TrailGenic Release Ledger

One entry per release, newest first. Record the source dataset and cutoff, affected pages, the review decision, the deployed commit, and the live URLs. Add an entry for a deferred report review too, with what is missing and the next review date.

The site's published dataset snapshot is September 30, 2026 (108 sessions). No release below changed it. The master workbook held 110 sessions as of November 11, 2026 (through Ruck 20 and Walk 27); that difference awaits the first Rhythm 1 release.

---

## 2026-11-13 · Routine edit

- **Source dataset / cutoff:** no dataset change. Published snapshot stays September 30, 2026 (108 sessions).
- **Affected pages:** /prevention, /podcast-episodes/season-2-episode-4-before-the-buyer-arrives, /my-journey, sitemap.xml
- **What changed:**
  - Guideline threshold spelled out as average systolic or diastolic pressure
  - Founder-reported wording on the podcast episode and the My Journey Biomarkers card
  - Sitemap dates set for the 11 pages whose content changed in the Prevention release
- **Decision:** Ella PASS on `098c4ae`
- **Deployed:** `c5de111` (merge to main)
- **Live check:** 0 failures (321 pages, 10 redirects, 6 not-found, 777 files, 29 cited)
- **Live URLs:**
  - https://www.trailgenic.com/prevention#walking-blood-pressure-research
  - https://www.trailgenic.com/podcast-episodes/season-2-episode-4-before-the-buyer-arrives
  - https://www.trailgenic.com/my-journey
  - https://www.trailgenic.com/sitemap.xml

## 2026-11-13 · Prevention release

- **Source dataset / cutoff:** no dataset change. Published snapshot stays September 30, 2026 (108 sessions).
- **Affected pages:**
  - /prevention
  - /, /about-us-new, /outcomes, /my-journey
  - /longevity, /walking
  - /science/trailgenic-method, /playbooks/trailgenic-method, /science/trailgenic-longevity-method
  - Prevention link card added on 196 article pages (science, trail-logs, physiology, ellas-corner, podcast-episodes, longevity)
  - llms.txt and the site-wide entity data
- **What changed:**
  - Founder account and record TG-BP-001
  - Research on walking and blood pressure
  - One shared summary sentence on five pages and llms.txt
  - Prevention linked from navigation and hubs
  - Shared Method definition on the three Method pages
  - Canonical cleanup
  - Parser-based page checker with tests
  - Orphan report
- **Decision:** Ella HOLD on `dffb1f7` (My Journey metadata; Cochrane denominators; 2025 guideline). Then PASS on `1a4662e`.
- **Deployed:** `4ac98b2`
- **Live check:** 0 failures (321 pages, 10 redirects, 6 not-found, 777 files, 29 cited)
- **Live URLs:**
  - https://www.trailgenic.com/prevention
  - https://www.trailgenic.com/prevention#blood-pressure-record
  - https://www.trailgenic.com/science/trailgenic-method
  - https://www.trailgenic.com/llms.txt
- **Citation measurement:** Grokbot panel on or after 2026-11-27. Results to be recorded here.

## 2026-11-13 · Fix list

- **Source dataset / cutoff:** no dataset change.
- **Affected pages:**
  - Every page: one site icon, and the Webflow preconnect hint removed
  - /favicon.ico added; /style-guide removed
  - Four dead internal links repointed, each old address forwarded with a 301
  - /biomarkers/biomarker-index-how-to-calculate (canonical fix)
- **Decision:** Ella HOLD on `2c22c32` (canonical in body; logo size). Then PASS on `9d170c6`.
- **Deployed:** `8fad55d`
- **Live check:** 0 failures
- **Live URLs:**
  - https://www.trailgenic.com/favicon.ico
  - https://www.trailgenic.com/biomarkers/biomarker-index-how-to-calculate

## 2026-11-13 · Dataset structured-data fix

- **Source dataset / cutoff:** no dataset change.
- **Affected pages:** 12 pages (7 physiology, 4 science including /science/research-datasets, 1 protocols): Dataset description and creator markup
- **Decision:** merged as pull request #1 (`fix/dataset-structured-data`)
- **Deployed:** `aa6f212`
- **Live check:** none recorded. Covered by the full live checks after later releases.

## 2026-11-11 · Cutover from Webflow to Vercel

- **Source dataset / cutoff:** live Webflow site as published 2026-11-11T20:59:21Z (dataset snapshot September 30, 2026; 108 sessions)
- **Affected pages:** all 321 addresses moved byte-for-byte; /about now forwards to /about-us-new
- **Decision:** Ella PASS on `8fb4fa8`
- **Deployed:** `8fb4fa8`; DNS switched about 7:45pm PT
- **Live check:** 0 failures (321 pages, 6 redirects, 10 not-found, 777 files, 29 cited)
- **Live URLs:** https://www.trailgenic.com/

---

## Report reviews (Rhythm 2)

| Report | Status | Cohort / cutoff | Next date | Notes |
|---|---|---|---|---|
| 001: Hiking Heart Rate and Recovery in Changing Field Conditions | Published v1.0.0, 2026-11-03 | 38 hikes, 93-session snapshot | — | Zenodo DOI 10.5281/zenodo.23932294 |
| 002: Environmental Load and Cardiovascular Response Across Real-World Hikes | In development (plan v0.1) | Observation cutoff 2026-11-30; freeze 2026-12-01 | Target release 2026-12-18 | Review at freeze. If deferred, record what is missing and the next review date here. |
