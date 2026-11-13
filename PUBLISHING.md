# Publishing TrailGenic

How a routine change goes from an edit to the live site, and how to undo it.

## Where things live

| What | Where |
|---|---|
| A page (hub or article) | `src/pages/<address>.html`. `/hiking` is `src/pages/hiking.html`; `/science/trailgenic-method` is `src/pages/science/trailgenic-method.html`; the homepage is `src/pages/index.html`. |
| Code shared by every page | `src/partials/site-head.html` (the former Webflow sitewide head code: entity graph, global styles, favicon) and `src/partials/site-footer.html` (former sitewide footer code). `webflow-head.html` and `webflow-scripts.html` are the standard Webflow layout and scripts; leave them alone. |
| Images, PDFs, stylesheets, scripts | `assets/cdn/...`, served at `/cdn/...`. Add a new file anywhere under `assets/cdn/wf/` and link it as `/cdn/wf/<path>`. |
| robots.txt, llms.txt, sitemap.xml | `src/static/`, copied as they are. Add a new page's address to `sitemap.xml` by hand. |
| Redirects | `vercel.json`, `redirects` list. Use `"statusCode": 301`. |

Each page file is the full page as Webflow published it. Lines like `<!--@partial site-head-->` pull in the shared code at build time; leave them in place. The body of a hub is usually one block of HTML inside `<div class="... w-embed">`, exactly as it was in the Webflow embed, so edit it the same way.

## Routine change

1. **Branch.** Create a branch from `main` (for example `edit/hiking-2026-11-20`).
2. **Edit** the page file, partial, file or redirect. For a new page, add `src/pages/<address>.html` (copy the closest existing page) and its sitemap entry.
3. **Push the branch.** Vercel builds a preview automatically and posts its address on the commit (GitHub shows it under the commit's checks). The build stops with a clear message if a page uses an unknown partial, links a `/cdn/` file that does not exist, or carries an out-of-date integrity hash. It also stops if a page breaks the page rules in `tools/check-page.mjs`: the head must be well formed, every indexable page needs exactly one canonical tag in the head naming its own address, and pages marked noindex (and the 404 page) carry none. Those rules have their own tests (`npm test`), which run before every build. A failed build never touches the live site.
4. **Review.** The checker reviews the preview address, not just the file change: the edited page, one neighbouring page, and the page's title and description.
5. **Merge** the branch into `main`. Vercel deploys `main` to production within a minute or two.

Reviewer for routine edits: Ella's builder drafts, Ella's checker reviews the preview (step 4), and the automated build checks must pass. Mike is not required for routine edits. (Pending Mike's confirmation.)

## Undo

- **Fastest:** in Vercel, open the project's Deployments, find the previous production deployment, and choose **Promote to Production** (or **Instant Rollback**). The site switches back in seconds.
- **Then** revert the commit on `main` (`git revert <commit>`) so the repository matches what is live.

## Things to keep true

- Keep every published address. If a page must move, add a 301 in `vercel.json` from the old address.
- Keep each page's canonical tag, title and description in its `<head>` in step with the page.
- Do not edit `public/`; it is rebuilt from scratch on every deploy.
- To check a change locally: `npm ci` once, then `npm test && node build.mjs` (needs Node 20+), then open files in `public/`.
- `python3 tools/orphans.py` (after a build) refreshes `reports/orphans.md`, the list of pages that few or no other pages link to.
- The founder blood-pressure summary is one sentence, used word for word on the homepage, About, Outcomes, My Journey, Prevention and in `llms.txt`. If it changes, change it in all six places and bump the record version on `/prevention#blood-pressure-record`.
- The three Method pages share one core definition (the `#core-definition` box). Change it in all three and in `llms.txt` together.
