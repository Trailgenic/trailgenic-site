// Builds the TrailGenic site into public/.
// src/pages   one HTML file per page; <!--@partial name--> pulls in src/partials/name.html
// src/static  files copied as they are (robots.txt, llms.txt, sitemap.xml)
// assets      self-hosted images, stylesheets, scripts and downloads (served under /cdn/)
// The build fails, leaving the live site untouched, if a page uses a missing
// partial, links a /cdn/ file that does not exist, or carries a stale integrity hash.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const OUT = path.join(ROOT, "public");
const errors = [];

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]);
}

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
fs.cpSync(path.join(ROOT, "assets"), OUT, { recursive: true });
fs.cpSync(path.join(ROOT, "src", "static"), OUT, { recursive: true });

const partials = {};
for (const f of fs.readdirSync(path.join(ROOT, "src", "partials"))) {
  partials[f.replace(/\.html$/, "")] = fs.readFileSync(path.join(ROOT, "src", "partials", f), "utf8");
}

const pagesDir = path.join(ROOT, "src", "pages");
let count = 0;
for (const file of walk(pagesDir)) {
  if (!file.endsWith(".html")) continue;
  const rel = path.relative(pagesDir, file);
  const html = fs.readFileSync(file, "utf8").replace(/<!--@partial ([\w-]+)-->/g, (m, name) => {
    if (!(name in partials)) { errors.push(`${rel}: unknown partial "${name}"`); return m; }
    return partials[name];
  });
  for (const m of html.matchAll(/(?:https:\/\/www\.trailgenic\.com)?(\/cdn\/[A-Za-z0-9._\/-]+)/g)) {
    if (!fs.existsSync(path.join(OUT, m[1]))) errors.push(`${rel}: missing file ${m[1]}`);
  }
  for (const m of html.matchAll(/<(?:script|link)\b[^>]*?(?:src|href)="(\/cdn\/[^"?]+)[^"]*"[^>]*?integrity="(sha\d+)-([^"]+)"/g)) {
    const fp = path.join(OUT, m[1]);
    if (!fs.existsSync(fp)) continue;
    const digest = crypto.createHash(m[2]).update(fs.readFileSync(fp)).digest("base64");
    if (digest !== m[3]) errors.push(`${rel}: integrity hash out of date for ${m[1]}`);
  }
  const dest = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, html);
  count++;
}

if (errors.length) {
  console.error(`Build failed with ${errors.length} problem(s):\n` + errors.slice(0, 50).join("\n"));
  process.exit(1);
}
console.log(`Built ${count} pages into public/`);
