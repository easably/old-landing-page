#!/usr/bin/env python3
"""Convert blog-articles/*.docx to static HTML under blog/<slug>/index.html (pandoc + media)."""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCX_DIR = ROOT / "blog-articles"
BLOG_DIR = ROOT / "blog"

# Public site origin (update if the site is deployed elsewhere)
SITE_ORIGIN = "https://easylang.app"

SITE_KEYWORDS = (
    "learn languages with YouTube, learn languages with Netflix, "
    "language learning, YouTube language learning, Netflix language learning, "
    "language learning app, subtitles, vocabulary, EasyLang"
)


def sort_key(p: Path) -> tuple[int, str]:
    m = re.match(r"^(\d+)", p.name)
    n = int(m.group(1)) if m else 999
    return (n, p.name)


def slugify(name: str, used: dict[str, int]) -> str:
    base = Path(name).stem.strip().lower()
    base = re.sub(r"[\s_]+", "-", base)
    base = "".join(
        c if (c.isalnum() or c == "-" or "\u4e00" <= c <= "\u9fff") else "-"
        for c in base
    )
    base = re.sub(r"-+", "-", base).strip("-") or "article"
    if base not in used:
        used[base] = 0
        return base
    used[base] += 1
    return f"{base}-{used[base]}"


def display_title(filename: str) -> str:
    base = Path(filename).stem.strip()
    return re.sub(r"^\d+\s*", "", base).strip() or base


def run_plain(docx: Path) -> str:
    r = subprocess.run(
        ["pandoc", str(docx.resolve()), "-t", "plain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise RuntimeError(f"pandoc plain failed for {docx.name}")
    return r.stdout


def meta_description(plain: str, fallback: str, max_len: int = 155) -> str:
    t = re.sub(r"\s+", " ", plain).strip() or fallback
    if len(t) <= max_len:
        return t
    cut = t[: max_len - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"


def build_article_html(
    docx: Path,
    out_dir: Path,
    title: str,
    desc: str,
    docx_href: str,
    slug: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            "pandoc",
            str(docx.resolve()),
            "-o",
            "index.html",
            "--extract-media=.",
        ],
        cwd=str(out_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise RuntimeError(f"pandoc html failed for {docx.name}")
    body = (out_dir / "index.html").read_text(encoding="utf-8")
    title_esc = html.escape(title, quote=True)
    desc_esc = html.escape(desc, quote=True)
    kw_esc = html.escape(SITE_KEYWORDS, quote=True)
    canon = f"{SITE_ORIGIN}/blog/{quote(slug, safe='-')}/"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{desc_esc}">
  <meta name="keywords" content="{kw_esc}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{html.escape(canon, quote=True)}">
  <title>{title_esc} — EasyLang blog</title>
  <meta property="og:type" content="article">
  <meta property="og:url" content="{html.escape(canon, quote=True)}">
  <meta property="og:title" content="{title_esc} — EasyLang blog">
  <meta property="og:description" content="{desc_esc}">
  <link rel="shortcut icon" href="../../img/logo/icon128.png" type="image/png">
  <link rel="stylesheet" href="../article.css">
</head>
<body>
  <nav class="top-nav" aria-label="Blog navigation">
    <a href="../../index.html">EasyLang home</a> ·
    <a href="../index.html">Blog</a> ·
    <a href="{docx_href}" download>Download .docx</a>
  </nav>
  <article class="post">
{body}
  </article>
</body>
</html>
"""
    (out_dir / "index.html").write_text(page, encoding="utf-8")


def write_sitemap_and_robots(manifest: list[tuple[str, str, str]]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    urls = [f"{SITE_ORIGIN}/", f"{SITE_ORIGIN}/blog/"]
    for _, slug, _ in manifest:
        urls.append(f"{SITE_ORIGIN}/blog/{quote(slug, safe='-')}/")
    for loc in urls:
        safe_loc = loc.replace("&", "&amp;")
        lines.append(f"  <url><loc>{safe_loc}</loc></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    robots = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_ORIGIN}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print("Wrote sitemap.xml and robots.txt")


def main() -> None:
    if not DOCX_DIR.is_dir():
        print("Missing blog-articles/", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Install pandoc: https://pandoc.org/", file=sys.stderr)
        sys.exit(1)

    docx_files = sorted(
        [
            p
            for p in DOCX_DIR.iterdir()
            if p.suffix.lower() == ".docx" and not p.name.startswith("~$")
        ],
        key=sort_key,
    )
    used_slugs: dict[str, int] = {}
    manifest: list[tuple[str, str, str]] = []

    for docx in docx_files:
        slug = slugify(docx.name, used_slugs)
        title = display_title(docx.name)
        plain = run_plain(docx)
        desc = meta_description(plain, title)
        docx_rel_href = "../blog-articles/" + quote(docx.name)
        out_dir = BLOG_DIR / slug
        build_article_html(docx, out_dir, title, desc, docx_rel_href, slug)
        manifest.append((title, slug, docx.name))
        print(f"OK  {slug}  ←  {docx.name}")

    ol = []
    for title, slug, fname in manifest:
        docx_href = "../blog-articles/" + quote(fname)
        title_esc = html.escape(title)
        ol.append(
            f'    <li><a href="{html.escape(slug)}/">{title_esc}</a>'
            f' <span class="fmt">(<a href="{docx_href}" download>.docx</a>)</span></li>'
        )

    blog_desc_esc = html.escape(
        "EasyLang blog — learn languages with YouTube, Netflix, and more. "
        "Guides and articles for language learning with video and context.",
        quote=True,
    )
    blog_kw_esc = html.escape(
        SITE_KEYWORDS + ", blog, guides, how to learn English",
        quote=True,
    )
    canon_blog_esc = html.escape(f"{SITE_ORIGIN}/blog/", quote=True)

    index_intro = f"""<!DOCTYPE html>
<html lang="en">

<head>
\t<meta charset="UTF-8">
\t<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
\t<meta name="description" content="{blog_desc_esc}">
\t<meta name="keywords" content="{blog_kw_esc}">
\t<meta name="robots" content="index,follow">
\t<link rel="canonical" href="{canon_blog_esc}">
\t<meta property="og:type" content="website">
\t<meta property="og:url" content="{canon_blog_esc}">
\t<meta property="og:title" content="Blog — EasyLang (YouTube &amp; Netflix language learning)">
\t<meta property="og:description" content="{blog_desc_esc}">
\t<link rel="shortcut icon" href="../img/logo/icon128.png" type="image/png">
\t<link rel="stylesheet" href="../fonts/Kodchasan/kodchasan.css">
\t<link rel="stylesheet" href="../fonts/Comfortaa/comfortaa.css">
\t<title>Blog — EasyLang | Learn languages with YouTube &amp; Netflix</title>
\t<style>
\t\tbody {{ font-family: Comfortaa, sans-serif; margin: 0; padding: 2rem 1.5rem 4rem; color: rgba(0, 0, 0, .85); line-height: 1.5; max-width: 46rem; margin-left: auto; margin-right: auto; }}
\t\th1 {{ font-family: Kodchasan, sans-serif; color: #215599; font-size: 1.75rem; }}
\t\th2 {{ font-family: Kodchasan, sans-serif; color: #215599; font-size: 1.2rem; margin-top: 2rem; }}
\t\ta {{ color: #45B8FF; font-weight: bold; word-break: break-word; }}
\t\ta:hover {{ color: #215599; }}
\t\t.note {{ margin-top: 1.5rem; padding: 1rem; background: #f4fafc; border-radius: 8px; font-size: .95rem; }}
\t\t.articles {{ margin: 0; padding-left: 1.25rem; }}
\t\t.articles li {{ margin: 0.65rem 0; }}
\t\t.fmt {{ font-weight: normal; font-size: .9rem; }}
\t\t.fmt a {{ font-weight: 600; }}
\t</style>
</head>

<body>
\t<p><a href="../index.html">← EasyLang home</a></p>
\t<h1>Blog</h1>
\t<p>Read articles as normal web pages (google-friendly text and headings). Topics cover language skills, subtitles, video learning—great companions to <strong>learning languages with YouTube</strong> or <strong>Netflix</strong>. Each post is built from the Word draft in <code>blog-articles/</code>; use the <code>.docx</code> link if you need the original file.</p>
\t<p class="note">After editing a <code>.docx</code>, rebuild HTML from the repo root: <code>python3 scripts/build_blog_html.py</code> (requires <a href="https://pandoc.org/" target="_blank" rel="noopener">pandoc</a>).</p>

\t<h2>Articles</h2>
\t<ol class="articles">
{chr(10).join(ol)}
\t</ol>
</body>

</html>
"""
    (BLOG_DIR / "index.html").write_text(index_intro, encoding="utf-8")
    print(f"Wrote blog/index.html ({len(manifest)} articles)")
    write_sitemap_and_robots(manifest)


if __name__ == "__main__":
    main()
