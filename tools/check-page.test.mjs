// Tests for tools/check-page.mjs. Run with `npm test`; the build runs them first.
import { checkPage } from "./check-page.mjs";

const CANON = '<link rel="canonical" href="https://www.trailgenic.com/sample"/>';
const page = ({ head = CANON, body = "<p>Hello</p>", afterHead = "" } = {}) =>
  `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><title>T</title>${head}</head>${afterHead}<body>${body}</body></html>`;

const cases = [
  ["valid page", "sample.html", page(), []],
  ["missing canonical", "sample.html", page({ head: "" }), ["found 0"]],
  ["duplicate, double quotes", "sample.html", page({ head: CANON + CANON }), ["found 2"]],
  ["duplicate, single quotes", "sample.html",
    page({ head: CANON + "<link rel='canonical' href='https://www.trailgenic.com/sample'>" }), ["found 2"]],
  ["duplicate, unquoted and upper case", "sample.html",
    page({ head: CANON + "<LINK REL=CANONICAL HREF=https://www.trailgenic.com/sample>" }), ["found 2"]],
  ["duplicate, href before rel", "sample.html",
    page({ head: CANON + '<link href="https://www.trailgenic.com/sample" rel="canonical">' }), ["found 2"]],
  ["canonical only inside an HTML comment", "sample.html", page({ head: `<!-- ${CANON} -->` }), ["found 0"]],
  ["real canonical plus a commented-out one", "sample.html", page({ head: `${CANON}<!-- ${CANON} -->` }), []],
  ["canonical only inside a script string", "sample.html",
    page({ head: `<script>var s='${CANON}';</script>` }), ["found 0"]],
  ["<main> inside head", "sample.html", page({ head: CANON + "<main><p>Intro</p></main>" }), ["content inside <head>"]],
  ["<div> inside head", "sample.html", page({ head: CANON + '<div class="x">Intro</div>' }), ["content inside <head>"]],
  ["loose text inside head", "sample.html", page({ head: CANON + "Intro text" }), ["content inside <head>"]],
  ["canonical after content in head", "sample.html", page({ head: "<div>Intro</div>" + CANON }), ["content inside <head>", "not directly inside <head>"]],
  ["canonical in body", "sample.html", page({ head: "", body: CANON + "<p>Hi</p>" }), ["not directly inside <head>"]],
  ["second canonical in body", "sample.html", page({ body: CANON }), ["found 2"]],
  ["canonical names another page", "sample.html",
    page({ head: '<link rel="canonical" href="https://www.trailgenic.com/other"/>' }), ["expected https://www.trailgenic.com/sample"]],
  ["canonical with trailing slash", "sample.html",
    page({ head: '<link rel="canonical" href="https://www.trailgenic.com/sample/"/>' }), ["expected https://www.trailgenic.com/sample"]],
  ["nested page", "science/sample.html",
    page({ head: '<link rel="canonical" href="https://www.trailgenic.com/science/sample"/>' }), []],
  ["homepage", "index.html", page({ head: '<link rel="canonical" href="https://www.trailgenic.com/"/>' }), []],
  ["noindex page without canonical", "sample.html",
    page({ head: '<meta name="robots" content="noindex, nofollow"/>' }), []],
  ["noindex page with canonical", "sample.html",
    page({ head: '<meta name="robots" content="noindex"/>' + CANON }), ["noindex page should not"]],
  ["noindex, content before name, single quotes", "sample.html",
    page({ head: "<meta content='NOINDEX' name='robots'>" }), []],
  ["robots meta in a comment does not make a page noindex", "sample.html",
    page({ head: '<!-- <meta name="robots" content="noindex"/> -->' }), ["found 0"]],
  ["404 page without canonical", "404.html", page({ head: "" }), []],
  ["404 page with canonical", "404.html", page(), ["noindex page should not"]],
  ["content between head and body", "sample.html", page({ afterHead: "<div>Stray</div>" }), ["before the <body> tag"]],
];

let failed = 0;
for (const [name, rel, html, want] of cases) {
  const got = checkPage(rel, html);
  const ok = got.length === want.length && want.every((w, i) => got[i].includes(w));
  if (!ok) {
    failed++;
    console.error(`FAIL  ${name}: expected [${want.join(" | ")}], got ${got.length} problem(s)\n      ${got.join("\n      ")}`);
  }
}
if (failed) {
  console.error(`${failed} of ${cases.length} checker tests failed`);
  process.exit(1);
}
console.log(`${cases.length} checker tests passed`);
