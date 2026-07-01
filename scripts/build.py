#!/usr/bin/env python3
"""Generate the Bluewater Homes sample site (pure static HTML + JSON-LD).

This is a SYNTHETIC realtor site: a friendly, well-structured page tree that anyone can paste
into RealtyRecall to watch one URL fan out into every listing plus an inferred realtor profile.

It is deliberately server-rendered with schema.org JSON-LD, OpenGraph, and a sitemap so the
onboarding engine extracts everything deterministically (no LLM key required for the listings).

Usage:
    python3 scripts/build.py [BASE_URL]

BASE_URL (default https://bluewater-homes-demo.vercel.app) is baked into canonical links, the
sitemap, and absolute image URLs. Re-run with the real production URL after the first deploy.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "https://bluewater-homes-demo.vercel.app").rstrip("/")

REALTOR = {
    "name": "Morgan Bell",
    "agency": "Bluewater Homes",
    "area": "Sarnia & Bright's Grove, Ontario",
    "tagline": "Homes with heart on the shores of Lake Huron.",
    "tone": "warm, local, and no-pressure",
    "phone": "519-555-0148",
    "email": "morgan@bluewaterhomes.example",
}

# The same six homes as demo/seed-listings.csv, so uploading the CSV and crawling this site
# yield an identical set. `hue` only tints the placeholder image.
LISTINGS = [
    {
        "code": "RR-101", "slug": "rr-101", "street": "14 Zephyrwood Crescent",
        "area": "Sarnia", "postal": "N7T 4R2", "price": 389000, "beds": 2, "baths": 1,
        "sqft": 980, "hue": 198,
        "desc": "Bright move-in-ready starter condo two blocks from the water, with an updated kitchen and in-suite laundry.",
    },
    {
        "code": "RR-102", "slug": "rr-102", "street": "88 Maple Ridge Drive",
        "area": "Sarnia", "postal": "N7S 2K1", "price": 459000, "beds": 3, "baths": 2,
        "sqft": 1520, "hue": 152,
        "desc": "Classic three-bed brick bungalow on a quiet family street, with a finished basement and a big fenced yard.",
    },
    {
        "code": "RR-103", "slug": "rr-103", "street": "7 Lakeshore Road",
        "area": "Bright's Grove", "postal": "N0N 1C0", "price": 749000, "beds": 4, "baths": 3,
        "sqft": 2680, "hue": 210,
        "desc": "Waterfront four-bed with lake views from the primary suite, a chef's kitchen, and a walkout deck.",
    },
    {
        "code": "RR-104", "slug": "rr-104", "street": "215 Christina Street North",
        "area": "Sarnia", "postal": "N7T 5V2", "price": 315000, "beds": 1, "baths": 1,
        "sqft": 720, "hue": 32,
        "desc": "Downtown loft in a restored heritage building, with exposed brick and a walk to cafes and the marina.",
    },
    {
        "code": "RR-105", "slug": "rr-105", "street": "42 Blackwell Sideroad",
        "area": "Sarnia", "postal": "N7V 3B4", "price": 529000, "beds": 4, "baths": 2,
        "sqft": 1990, "hue": 268,
        "desc": "Spacious four-bed on a deep lot with room for a shop; needs cosmetic updates but priced to move.",
    },
    {
        "code": "RR-106", "slug": "rr-106", "street": "19 Errol Village Lane",
        "area": "Bright's Grove", "postal": "N0N 1C0", "price": 635000, "beds": 3, "baths": 3,
        "sqft": 2210, "hue": 8,
        "desc": "Newer three-bed in a family neighbourhood near the golf course, with an open main floor and a double garage.",
    },
]


def money(v: int) -> str:
    return "${:,}".format(v)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def img_url(listing: dict) -> str:
    return f"{BASE_URL}/assets/{listing['slug']}.svg"


def head(title: str, description: str, path: str, og_type: str, image: str, jsonld: dict | list | None) -> str:
    canonical = f"{BASE_URL}{path}"
    blocks = ""
    if jsonld is not None:
        payload = json.dumps(jsonld, ensure_ascii=False, indent=2)
        blocks = f'\n    <script type="application/ld+json">\n{payload}\n    </script>'
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="stylesheet" href="/assets/styles.css" />
    <meta property="og:site_name" content="{esc(REALTOR['agency'])}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:title" content="{esc(title)}" />
    <meta property="og:description" content="{esc(description)}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{image}" />{blocks}
  </head>
  <body>
    <header class="site">
      <a class="brand" href="/">{esc(REALTOR['agency'])}</a>
      <nav>
        <a href="/">Home</a>
        <a href="/listings/">Listings</a>
        <a href="/about.html">About</a>
      </nav>
    </header>
    <main>
"""


FOOT = f"""    </main>
    <footer class="site">
      <p><strong>{esc(REALTOR['agency'])}</strong> &middot; {esc(REALTOR['area'])}</p>
      <p>{esc(REALTOR['name'])} &middot; {esc(REALTOR['phone'])} &middot; {esc(REALTOR['email'])}</p>
      <p class="fineprint">Sample site with synthetic listings, built to demo RealtyRecall. Not a real brokerage.</p>
    </footer>
  </body>
</html>
"""


def listing_card(listing: dict) -> str:
    return f"""      <a class="card" href="/listings/{listing['slug']}.html">
        <img class="card-img" src="/assets/{listing['slug']}.svg" alt="{esc(listing['street'])}" />
        <div class="card-body">
          <div class="card-price">{money(listing['price'])}</div>
          <div class="card-street">{esc(listing['street'])}, {esc(listing['area'])}</div>
          <div class="card-specs">{listing['beds']} bed &middot; {listing['baths']} bath &middot; {listing['sqft']:,} sqft</div>
        </div>
      </a>
"""


def residence_ld(listing: dict) -> dict:
    """schema.org SingleFamilyResidence for one home. Reused on the detail page AND embedded on
    the home/listings pages so every path extracts the same code-keyed record (clean dedupe).
    """
    return {
        "@context": "https://schema.org",
        "@type": "SingleFamilyResidence",
        "name": listing["street"],
        "sku": listing["code"],
        "numberOfBedrooms": listing["beds"],
        "numberOfBathroomsTotal": listing["baths"],
        "floorSize": {"@type": "QuantitativeValue", "value": listing["sqft"], "unitCode": "FTK"},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": listing["street"],
            "addressLocality": listing["area"],
            "addressRegion": "ON",
            "postalCode": listing["postal"],
            "addressCountry": "CA",
        },
        "description": listing["desc"],
        "image": img_url(listing),
        "url": f"{BASE_URL}/listings/{listing['slug']}.html",
        "offers": {
            "@type": "Offer",
            "price": listing["price"],
            "priceCurrency": "CAD",
            "availability": "https://schema.org/InStock",
        },
    }


def render_home() -> str:
    org_jsonld = {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": REALTOR["agency"],
        "description": REALTOR["tagline"],
        "areaServed": REALTOR["area"],
        "url": f"{BASE_URL}/",
        "telephone": REALTOR["phone"],
        "email": REALTOR["email"],
        "employee": {"@type": "Person", "name": REALTOR["name"], "jobTitle": "Realtor"},
    }
    # Org profile + the featured homes' structured data, so the homepage alone already yields
    # code-keyed listings (no LLM needed, and no address-only duplicates).
    home_ld = [org_jsonld] + [residence_ld(x) for x in LISTINGS[:3]]
    featured = "".join(listing_card(x) for x in LISTINGS[:3])
    body = f"""      <section class="hero">
        <h1>{esc(REALTOR['agency'])}</h1>
        <p class="lede">{esc(REALTOR['tagline'])}</p>
        <p>Working with buyers and sellers across {esc(REALTOR['area'])}. Browse every current
        home below, or <a href="/listings/">see all listings</a>.</p>
      </section>
      <section>
        <h2>Featured homes</h2>
        <div class="grid">
{featured}        </div>
        <p><a class="more" href="/listings/">View all {len(LISTINGS)} listings &rarr;</a></p>
      </section>
"""
    return head(
        f"{REALTOR['agency']} | Homes in {REALTOR['area']}",
        REALTOR["tagline"] + " Current homes for sale across " + REALTOR["area"] + ".",
        "/", "website", f"{BASE_URL}/assets/hero.svg", home_ld,
    ) + body + FOOT


def render_about() -> str:
    person_jsonld = {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": REALTOR["name"],
        "worksFor": {"@type": "Organization", "name": REALTOR["agency"]},
        "areaServed": REALTOR["area"],
        "description": REALTOR["tagline"],
        "url": f"{BASE_URL}/about.html",
        "telephone": REALTOR["phone"],
        "email": REALTOR["email"],
        "knowsAbout": ["residential real estate", "waterfront homes", "first-time buyers"],
    }
    body = f"""      <section class="prose">
        <h1>About {esc(REALTOR['name'])}</h1>
        <p>I'm {esc(REALTOR['name'])}, the realtor behind {esc(REALTOR['agency'])}. For over a
        decade I've helped families buy and sell across {esc(REALTOR['area'])}, from first
        condos near the water to waterfront homes in Bright's Grove.</p>
        <p>My style is {esc(REALTOR['tone'])}. I'd rather you find the right home than the fast
        one, and I know these streets, schools, and shorelines like my own backyard.</p>
        <p><em>&ldquo;{esc(REALTOR['tagline'])}&rdquo;</em></p>
        <p>Reach me at {esc(REALTOR['phone'])} or {esc(REALTOR['email'])}.</p>
      </section>
"""
    return head(
        f"About {REALTOR['name']} | {REALTOR['agency']}",
        f"{REALTOR['name']} of {REALTOR['agency']}, serving {REALTOR['area']}. {REALTOR['tagline']}",
        "/about.html", "profile", f"{BASE_URL}/assets/hero.svg", person_jsonld,
    ) + body + FOOT


def render_listings_index() -> str:
    cards = "".join(listing_card(x) for x in LISTINGS)
    all_ld = [residence_ld(x) for x in LISTINGS]
    body = f"""      <section>
        <h1>All listings</h1>
        <p>{len(LISTINGS)} homes currently for sale across {esc(REALTOR['area'])}.</p>
        <div class="grid">
{cards}        </div>
      </section>
"""
    return head(
        f"All listings | {REALTOR['agency']}",
        f"Every current home for sale with {REALTOR['agency']} across {REALTOR['area']}.",
        "/listings/", "website", f"{BASE_URL}/assets/hero.svg", all_ld,
    ) + body + FOOT


def render_listing(listing: dict) -> str:
    jsonld = residence_ld(listing)
    body = f"""      <article class="detail">
        <a class="back" href="/listings/">&larr; All listings</a>
        <img class="detail-img" src="/assets/{listing['slug']}.svg" alt="{esc(listing['street'])}" />
        <h1>{esc(listing['street'])}</h1>
        <p class="detail-area">{esc(listing['area'])}, ON &middot; {esc(listing['postal'])}</p>
        <p class="detail-price">{money(listing['price'])}</p>
        <ul class="specs">
          <li><strong>{listing['beds']}</strong> bedrooms</li>
          <li><strong>{listing['baths']}</strong> bathrooms</li>
          <li><strong>{listing['sqft']:,}</strong> sqft</li>
          <li>MLS <strong>{esc(listing['code'])}</strong></li>
        </ul>
        <p class="detail-desc">{esc(listing['desc'])}</p>
        <p>Interested? Call {esc(REALTOR['name'])} at {esc(REALTOR['phone'])} to book a showing.</p>
      </article>
"""
    return head(
        f"{listing['street']}, {listing['area']} | {money(listing['price'])}",
        listing["desc"],
        f"/listings/{listing['slug']}.html", "product", img_url(listing), jsonld,
    ) + body + FOOT


def render_svg(listing: dict) -> str:
    h = listing["hue"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img" aria-label="{esc(listing['street'])}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="hsl({h} 62% 52%)" />
      <stop offset="1" stop-color="hsl({(h + 28) % 360} 58% 34%)" />
    </linearGradient>
  </defs>
  <rect width="1200" height="800" fill="url(#g)" />
  <g fill="none" stroke="#ffffff" stroke-width="14" stroke-linejoin="round" stroke-linecap="round" opacity="0.92">
    <path d="M330 470 L600 270 L870 470" />
    <path d="M390 440 L390 640 L810 640 L810 440" />
    <rect x="540" y="520" width="120" height="120" />
  </g>
  <text x="600" y="726" fill="#ffffff" font-family="Georgia, serif" font-size="46" font-weight="700" text-anchor="middle">{money(listing['price'])} &#183; {listing['beds']} bed &#183; {listing['baths']} bath</text>
  <text x="600" y="770" fill="#ffffff" opacity="0.85" font-family="Georgia, serif" font-size="30" text-anchor="middle">{esc(listing['street'])}, {esc(listing['area'])}</text>
</svg>
"""


def render_hero_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600" role="img" aria-label="Bluewater Homes">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="hsl(202 70% 58%)" />
      <stop offset="1" stop-color="hsl(198 64% 40%)" />
    </linearGradient>
  </defs>
  <rect width="1200" height="600" fill="url(#sky)" />
  <rect y="430" width="1200" height="170" fill="hsl(202 55% 30%)" opacity="0.6" />
  <g fill="none" stroke="#ffffff" stroke-width="10" opacity="0.9" stroke-linejoin="round">
    <path d="M470 340 L600 240 L730 340" />
    <path d="M510 320 L510 430 L690 430 L690 320" />
  </g>
  <text x="600" y="530" fill="#ffffff" font-family="Georgia, serif" font-size="54" font-weight="700" text-anchor="middle">Bluewater Homes</text>
</svg>
"""


def render_sitemap() -> str:
    paths = ["/", "/about.html", "/listings/"] + [f"/listings/{x['slug']}.html" for x in LISTINGS]
    urls = "\n".join(f"  <url><loc>{BASE_URL}{p}</loc></url>" for p in paths)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""


CSS = """:root {
  --ink: #16223a; --muted: #5b6b86; --line: #e4e9f2; --brand: #0e6ba8; --bg: #f7f9fc;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color: var(--ink); background: var(--bg); line-height: 1.55; }
a { color: var(--brand); text-decoration: none; }
a:hover { text-decoration: underline; }
main { max-width: 1040px; margin: 0 auto; padding: 28px 20px 8px; }
header.site, footer.site { max-width: 1040px; margin: 0 auto; padding: 18px 20px; }
header.site { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); }
.brand { font-weight: 800; font-size: 20px; color: var(--ink); }
header nav a { margin-left: 18px; color: var(--muted); font-weight: 600; }
.hero h1 { font-size: 40px; margin: 8px 0 6px; }
.lede { font-size: 20px; color: var(--muted); margin: 0 0 10px; }
h2 { font-size: 24px; margin-top: 34px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 14px; }
.card { display: block; background: #fff; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; color: inherit; transition: box-shadow .15s, transform .15s; }
.card:hover { text-decoration: none; box-shadow: 0 10px 28px rgba(20,40,80,.10); transform: translateY(-2px); }
.card-img, .detail-img { width: 100%; display: block; aspect-ratio: 3 / 2; object-fit: cover; }
.card-body { padding: 14px 16px 18px; }
.card-price { font-weight: 800; font-size: 20px; color: var(--brand); }
.card-street { margin-top: 2px; font-weight: 600; }
.card-specs { color: var(--muted); font-size: 14px; margin-top: 4px; }
.more { font-weight: 700; }
.detail { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 20px; }
.detail-img { border-radius: 12px; margin-bottom: 16px; }
.detail h1 { margin: 6px 0 2px; }
.detail-area { color: var(--muted); margin: 0 0 8px; }
.detail-price { font-size: 30px; font-weight: 800; color: var(--brand); margin: 0 0 14px; }
.specs { list-style: none; padding: 0; margin: 0 0 16px; display: flex; flex-wrap: wrap; gap: 10px 22px; }
.specs li { color: var(--muted); }
.specs strong { color: var(--ink); }
.back, .detail-desc { display: block; }
.back { margin-bottom: 14px; font-weight: 600; }
.prose { max-width: 680px; }
.prose h1 { font-size: 32px; }
footer.site { border-top: 1px solid var(--line); margin-top: 40px; color: var(--muted); font-size: 14px; }
.fineprint { color: #9aa8bf; }
"""

ROBOTS = f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n"

README = f"""# Bluewater Homes (sample realtor site)

A **synthetic** real-estate site for a fictional agent, *{REALTOR['name']}* of
*{REALTOR['agency']}* ({REALTOR['area']}). Every listing is made up.

It exists so anyone can try [RealtyRecall](https://realtyrecall.mahimai.ca): paste this site's
URL into the console and watch one link fan out into all {len(LISTINGS)} listings plus an
inferred realtor profile.

Pure static HTML with schema.org JSON-LD, OpenGraph, and a sitemap, so onboarding extracts the
listings deterministically (no AI key required for the listing data).

Regenerate after changing `scripts/build.py`:

    python3 scripts/build.py https://your-deployed-url.vercel.app
"""


def write(path: str, content: str) -> None:
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


def main() -> None:
    print(f"Building Bluewater Homes with BASE_URL={BASE_URL}")
    write("index.html", render_home())
    write("about.html", render_about())
    write("listings/index.html", render_listings_index())
    for listing in LISTINGS:
        write(f"listings/{listing['slug']}.html", render_listing(listing))
        write(f"assets/{listing['slug']}.svg", render_svg(listing))
    write("assets/hero.svg", render_hero_svg())
    write("assets/styles.css", CSS)
    write("sitemap.xml", render_sitemap())
    write("robots.txt", ROBOTS)
    write("README.md", README)
    write(".vercelignore", "scripts/\nREADME.md\n")
    print(f"Done: {len(LISTINGS)} listings + home/about/index.")


if __name__ == "__main__":
    main()
