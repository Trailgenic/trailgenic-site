// Page checks run by build.mjs on every built page. They read the page the way a
// browser does (a real HTML parser), not with text patterns, so quoting style,
// attribute order, comments and misplaced tags cannot fool them.
//
// Rules:
//   1. <head> must be explicitly opened and closed, and <body> explicitly opened.
//      Page content inside <head> (a <div>, <main>, loose text ...) makes a browser
//      end the head early; the parser shows that as a head with no closing tag.
//   2. An indexable page carries exactly one canonical tag, as a direct child of
//      <head>, whose address is the page's own address.
//   3. A page marked noindex, and the 404 page, carry no canonical tag.
import { parse } from "parse5";

const SITE = "https://www.trailgenic.com";

function attr(node, name) {
  const a = (node.attrs || []).find((x) => x.name === name);
  return a ? a.value : undefined;
}

function elements(node, out = [], parent = null) {
  if (node.tagName) out.push({ node, parent });
  // <template> content is inert, so it is deliberately not visited.
  for (const child of node.childNodes || []) elements(child, out, node);
  return out;
}

export function pageUrl(rel) {
  const p = rel.replace(/\\/g, "/").replace(/\.html$/, "");
  return SITE + "/" + (p === "index" ? "" : p);
}

export function checkPage(rel, html) {
  const errors = [];
  const doc = parse(html, { sourceCodeLocationInfo: true });
  const root = (doc.childNodes || []).find((n) => n.tagName === "html");
  const head = root && root.childNodes.find((n) => n.tagName === "head");
  const body = root && root.childNodes.find((n) => n.tagName === "body");
  const headLoc = head && head.sourceCodeLocation;
  const bodyLoc = body && body.sourceCodeLocation;

  if (!headLoc || !headLoc.startTag) errors.push(`${rel}: no <head> tag`);
  else if (!headLoc.endTag) errors.push(`${rel}: page content inside <head> (the head ends before its closing tag)`);
  else if (!bodyLoc || !bodyLoc.startTag) errors.push(`${rel}: page content before the <body> tag`);

  const all = elements(doc);
  const canonicals = all.filter(({ node }) =>
    node.tagName === "link" && (attr(node, "rel") || "").toLowerCase().split(/\s+/).includes("canonical"));
  const noindex = rel === "404.html" || all.some(({ node, parent }) =>
    node.tagName === "meta" && parent === head &&
    (attr(node, "name") || "").toLowerCase() === "robots" &&
    /\bnoindex\b/i.test(attr(node, "content") || ""));

  if (noindex) {
    if (canonicals.length) errors.push(`${rel}: noindex page should not carry a canonical tag`);
    return errors;
  }
  if (canonicals.length !== 1) {
    errors.push(`${rel}: expected exactly 1 canonical tag, found ${canonicals.length}`);
    return errors;
  }
  const { node, parent } = canonicals[0];
  if (parent !== head) errors.push(`${rel}: canonical tag is not directly inside <head>`);
  const href = attr(node, "href");
  if (href !== pageUrl(rel)) errors.push(`${rel}: canonical is ${href}, expected ${pageUrl(rel)}`);
  return errors;
}
