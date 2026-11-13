# TrailGenic Publishing Cadence

Owner: Ella. Adopted November 13, 2026. Either Ella or Claude can pick up from this file and `docs/RELEASES.md`.

## Roles

- **Ella** owns intake, priorities and follow-through, through production verification.
- **Builder and reviewer swap.** When Claude builds, Ella reviews the exact preview. When Ella builds, Claude takes the independent review.
- **Each batch** gets one release review (PASS/HOLD on an exact commit and preview) and one live check after merge.
- **Mike** approves anything published in his first-person voice.

## Rhythm 1: Site and dataset updates (two speeds)

Adopted November 13, 2026. The first hub and aggregate deployments under this rhythm wait until Grokbot captures the November 27 panel.

### Data flow (both speeds)

- Mike logs each session in the master workbook right after it happens. That working file is the only copy anyone edits.
- **Handoff:** Mike hands over the workbook on Sunday night.
- **Freeze:** the verified workbook is committed to the private repository `Trailgenic/world-model-data` under `snapshots/YYYY-MM-DD/`, named for its data cutoff, and logged in that repository's `SNAPSHOTS.md` with its SHA-256.
- **Missing handoff:** no batch that week. Pending sessions carry forward to the next verified workbook.
- **Session counts vary.** About four sessions a week at normal pace (one per modality); October 2026 had none because of an ankle injury.

### Speed 1: Weekly hub batch (Monday)

- **Scope:** the four modality hubs, /walking, /rucking, /running and /hiking. Only hubs with eligible new sessions change.
- **Each changed hub** gets its own release ID (`YYYY-MM-DD.N`) and its own data cutoff (its latest included session date), shown on the page.
- **No new sessions:** no publication. The hub's dates stay as they are.
- **One batch per week:** one independent review and one live check.

### Speed 2: Monthly aggregate release (the 1st)

- **Scope:** the homepage, /longevity, /science, /physiology, /sleep, /prevention, /outcomes, /foundation-comparison, /science/research-datasets, and any other page that states a total across modalities.
- **Data:** reuses the latest verified weekly snapshot. No separate intake.
- **One cutoff** is stated across all aggregate pages, and readers are linked to the hubs for newer sessions.
- **Historical comparison windows keep their original cohorts.** These include the 93-session anniversary audit, the 101-session checkpoint, the September 24 research baseline and Walking's S1–24 windows.
- **One release:** one independent review and one live check.
- **December 1, 2026 (first aggregate release):**
  - Reconcile the 108-session baseline (`2026-09-30.1`) to the latest verified total, preserving the historical cohorts.
  - Check /biomarkers. Its page data carries `counts` with `total: 108` under release `2026-09-30.1`, which reads as a current total, not a historical reference. Confirm that during the pass and update or relabel it accordingly.

### Rules for both speeds

- **Cohort rule:**
  - Foundation's same-route comparisons stay tied to their own cohort.
  - The hiking record stays tied to its terrain, conditions and recovery evidence.
  - The two are never mixed in one claim.
- **Two different dates:**
  - The **data cutoff** is the date of the latest session included.
  - The **page update date** is when the page content changed.
  - For a substantive page edit, the visible "Updated" date, `dateModified` and sitemap `lastmod` change together, and only then.
- **Material corrections** ship when ready, outside the schedule, with their own review and live check.

### Why weekly hubs

- The hubs gain new observations readers can use, at about four sessions a week.
- Ahrefs' analysis of about 17 million AI citations found AI assistants cited more recently published and updated pages on average than organic search did. That study does not estimate the benefit of weekly over monthly publishing for TrailGenic.
- **Measurement:**
  - The November 27 panel is the pre-cadence checkpoint.
  - In the next comparable run, look for verified hub citations and accurate use of the new sessions.
  - Record every intervening site change in the ledger so results can be interpreted.

## Rhythm 2: Longitudinal reports

- **When:** reviewed every seven weeks.
- **At each review:** decide whether the frozen cohort supports a report and its reproducibility package. If it doesn't, record what is missing and the next defensible review date in the ledger.
- **Report 002** (Environmental Load and Cardiovascular Response Across Real-World Hikes): observation cutoff November 30, 2026; freeze December 1; target release December 18, 2026.
- **Citation direction:** TrailGenic cites Zenodo, one way. Report 001 is archived at DOI 10.5281/zenodo.23932294.

## Citation measurement

- Run a citation panel after material changes to what the site can answer, not on a calendar.
- **Next:** Grokbot's panel on or after November 27, 2026, measuring the Prevention release. It is also the checkpoint before the two-speed cadence starts.
- **Method:** the original hiking query is the control, and the same three engines are used each time. Three scores are kept separate: brand mention, verified first-party citation, and accurate use of the evidence.

## Standing rules

- No filler: nothing is published without new data or new evidence.
- No new efficacy claims. The founder record describes one person; outside research describes its own populations.
- Dates are real: a page's visible date, its structured-data date and its sitemap date change together, and only for substantive edits.
- No workflow mentions on the public site.
- Every release is recorded in `docs/RELEASES.md`.

## Queued work

Build items 1 and 2 now, in parallel. Hold their production deployment, and the first weekly hub and monthly aggregate deployments, until Grokbot captures the citation panel (on or after November 27, 2026). Record the live commit and capture date with the panel results.

1. **Structured data.** Start with the strongest evidence pages. Use only dates and fields the visible page supports.
2. **Sitemap dates.** Derive them from substantive edits instead of hand-editing them.
3. **Hub decisions.** /fitness-library and /recovery-conditioning stay open until we know what each destination would carry.
