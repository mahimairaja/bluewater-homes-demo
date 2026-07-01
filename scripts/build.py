#!/usr/bin/env python3
"""Generate the Bluewater Homes sample site (professional static realtor site).

A SYNTHETIC realtor site anyone can paste into RealtyRecall to watch one URL fan out into every
listing plus an inferred realtor profile. Server-rendered HTML with schema.org JSON-LD,
OpenGraph, and a sitemap so onboarding extracts everything deterministically (no LLM key needed
for the listings). Real photography comes from Pexels, resolved at build time and cached.

Usage:
    PEXELS_API_KEY=... python3 scripts/build.py [BASE_URL] [--refresh-photos]

BASE_URL (default https://bluewater-homes-demo.vercel.app) is baked into canonical links and the
sitemap. Photo CDN URLs are absolute (Pexels), so images are independent of BASE_URL. The key is
only needed to (re)build assets/photos.json; it is never written into any output file.
"""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FLAGS = {a for a in sys.argv[1:] if a.startswith("--")}
BASE_URL = (ARGS[0] if ARGS else "https://bluewater-homes-demo.vercel.app").rstrip("/")
PHOTOS_CACHE = ROOT / "assets" / "photos.json"

REALTOR = {
    "name": "Morgan Bell",
    "agency": "Bluewater Homes",
    "area": "Sarnia & Bright's Grove, Ontario",
    "tagline": "Homes with heart on the shores of Lake Huron.",
    "tone": "warm, local, and no-pressure",
    "phone": "519-555-0148",
    "email": "morgan@bluewaterhomes.example",
    "since": 2012,
    "sold": "260+",
}

# The first six match RealtyRecall/demo/seed-listings.csv (so a CSV upload and a URL crawl
# agree); RR-107..RR-109 add range. `query` picks the Pexels photography per listing.
LISTINGS = [
    {
        "code": "RR-101", "slug": "rr-101", "street": "14 Zephyrwood Crescent",
        "area": "Sarnia", "postal": "N7T 4R2", "price": 389000, "beds": 2, "baths": 1,
        "sqft": 980, "query": "modern condo interior",
        "desc": "Bright, move-in-ready starter condo two blocks from the water, with an updated kitchen and in-suite laundry.",
        "features": ["Updated kitchen", "In-suite laundry", "Two blocks to the waterfront", "Low condo fees"],
    },
    {
        "code": "RR-102", "slug": "rr-102", "street": "88 Maple Ridge Drive",
        "area": "Sarnia", "postal": "N7S 2K1", "price": 459000, "beds": 3, "baths": 2,
        "sqft": 1520, "query": "brick bungalow house",
        "desc": "Classic three-bed brick bungalow on a quiet family street, with a finished basement and a big fenced yard.",
        "features": ["Finished basement", "Fenced backyard", "Attached garage", "Quiet family street"],
    },
    {
        "code": "RR-103", "slug": "rr-103", "street": "7 Lakeshore Road",
        "area": "Bright's Grove", "postal": "N0N 1C0", "price": 749000, "beds": 4, "baths": 3,
        "sqft": 2680, "query": "waterfront house lake",
        "desc": "Waterfront four-bed with lake views from the primary suite, a chef's kitchen, and a walkout deck.",
        "features": ["Lake views", "Chef's kitchen", "Walkout deck", "Primary suite with ensuite"],
    },
    {
        "code": "RR-104", "slug": "rr-104", "street": "215 Christina Street North",
        "area": "Sarnia", "postal": "N7T 5V2", "price": 315000, "beds": 1, "baths": 1,
        "sqft": 720, "query": "loft apartment exposed brick",
        "desc": "Downtown loft in a restored heritage building, with exposed brick and a walk to cafes and the marina.",
        "features": ["Exposed brick", "Heritage building", "Walk to the marina", "Open-concept living"],
    },
    {
        "code": "RR-105", "slug": "rr-105", "street": "42 Blackwell Sideroad",
        "area": "Sarnia", "postal": "N7V 3B4", "price": 529000, "beds": 4, "baths": 2,
        "sqft": 1990, "query": "suburban family house exterior",
        "desc": "Spacious four-bed on a deep lot with room for a shop; needs cosmetic updates but priced to move.",
        "features": ["Deep lot", "Room for a shop", "Four bedrooms", "Priced to move"],
    },
    {
        "code": "RR-106", "slug": "rr-106", "street": "19 Errol Village Lane",
        "area": "Bright's Grove", "postal": "N0N 1C0", "price": 635000, "beds": 3, "baths": 3,
        "sqft": 2210, "query": "modern house exterior dusk",
        "desc": "Newer three-bed in a family neighbourhood near the golf course, with an open main floor and a double garage.",
        "features": ["Double garage", "Open main floor", "Near the golf course", "Newer build"],
    },
    {
        "code": "RR-107", "slug": "rr-107", "street": "5 Harbourfront Mews",
        "area": "Sarnia", "postal": "N7T 8B9", "price": 412000, "beds": 3, "baths": 2,
        "sqft": 1340, "query": "modern townhouse exterior",
        "desc": "Low-maintenance three-bed townhouse steps from the harbour, with a private patio and a single garage.",
        "features": ["Steps to the harbour", "Private patio", "Single garage", "Low-maintenance living"],
    },
    {
        "code": "RR-108", "slug": "rr-108", "street": "3110 London Line",
        "area": "Sarnia", "postal": "N7W 1A2", "price": 689000, "beds": 4, "baths": 3,
        "sqft": 2450, "query": "country house countryside",
        "desc": "Four-bed country property on nearly an acre, with mature trees, a wraparound porch, and a heated shop.",
        "features": ["Just under an acre", "Wraparound porch", "Heated shop", "Mature trees"],
    },
    {
        "code": "RR-109", "slug": "rr-109", "street": "22 Old Lakeshore Road",
        "area": "Bright's Grove", "postal": "N0N 1C0", "price": 915000, "beds": 4, "baths": 4,
        "sqft": 3120, "query": "luxury modern living room interior",
        "desc": "Custom-built four-bed on a premium lot, with vaulted ceilings, a spa ensuite, and a landscaped backyard oasis.",
        "features": ["Vaulted ceilings", "Spa ensuite", "Backyard oasis", "Custom build"],
    },
]

TESTIMONIALS = [
    ("Morgan sold our bungalow in a week and found us a bigger place two streets over. Calm, honest, and always a step ahead.", "The Whitfords", "Sarnia"),
    ("First-time buyers and totally overwhelmed, until Morgan walked us through every step. We closed on our condo stress-free.", "Priya & Sam", "Bright's Grove"),
    ("Knows the shoreline better than anyone. We got lake views and a fair price, and never once felt pushed.", "Dana R.", "Bright's Grove"),
]

# ---------------------------------------------------------------------------- photos (Pexels)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")


def _pexels_search(query: str, n: int, orientation: str) -> list[dict]:
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": n, "orientation": orientation}
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": PEXELS_KEY,
            "User-Agent": "Mozilla/5.0 (BluewaterHomesDemo build)",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (trusted host)
        data = json.load(resp)
    photos = []
    for ph in data.get("photos", []):
        src = ph.get("src", {})
        photos.append(
            {
                "id": ph.get("id"),
                "large2x": src.get("large2x") or src.get("large"),
                "large": src.get("large"),
                "medium": src.get("medium"),
                "photographer": ph.get("photographer", "Pexels"),
                "photographer_url": ph.get("photographer_url", "https://www.pexels.com"),
                "alt": ph.get("alt") or query,
            }
        )
    return photos


def _fetch_photos() -> dict:
    print("  fetching photography from Pexels...")
    photos: dict = {"hero": None, "agent": None, "listings": {}}
    hero = _pexels_search("luxury lakefront home exterior", 3, "landscape")
    photos["hero"] = hero[0] if hero else None
    agent = _pexels_search("real estate agent portrait professional", 2, "portrait")
    photos["agent"] = agent[0] if agent else None
    for listing in LISTINGS:
        got = _pexels_search(listing["query"], 4, "landscape")
        if not got:
            got = _pexels_search("house home", 3, "landscape")
        photos["listings"][listing["code"]] = got[:3]
        print(f"    {listing['code']}: {len(got[:3])} photo(s) for '{listing['query']}'")
    return photos


def load_photos() -> dict:
    if PHOTOS_CACHE.exists() and "--refresh-photos" not in FLAGS:
        print(f"  using cached photos ({PHOTOS_CACHE.name})")
        return json.loads(PHOTOS_CACHE.read_text())
    if not PEXELS_KEY:
        raise SystemExit(
            "No cached photos and PEXELS_API_KEY is not set. Run once with the key:\n"
            "    PEXELS_API_KEY=... python3 scripts/build.py"
        )
    photos = _fetch_photos()
    PHOTOS_CACHE.write_text(json.dumps(photos, indent=2))
    print(f"  cached photos -> {PHOTOS_CACHE.name}")
    return photos


PHOTOS: dict = {}


def listing_photos(listing: dict) -> list[dict]:
    return PHOTOS["listings"].get(listing["code"], [])


def main_photo(listing: dict) -> dict:
    shots = listing_photos(listing)
    return shots[0] if shots else {"large2x": "", "large": "", "medium": "", "alt": listing["street"]}


# --------------------------------------------------------------------------------- helpers


def money(v: int) -> str:
    return "${:,}".format(v)


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


IC_BED = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8V5h12v3"/></svg>'
IC_BATH = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12V5a2 2 0 0 1 2-2h1a2 2 0 0 1 2 2"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M5 12v3a4 4 0 0 0 4 4h6a4 4 0 0 0 4-4v-3"/><line x1="7" y1="19" x2="6" y2="21"/><line x1="17" y1="19" x2="18" y2="21"/></svg>'
IC_AREA = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6"/><path d="M9 21H3v-6"/><path d="M21 3l-7 7"/><path d="M3 21l7-7"/></svg>'
IC_PIN = '<svg class="vic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>'
IC_HAND = '<svg class="vic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.9-3.9a2 2 0 0 0-1.7-.5l-2.1.3a2 2 0 0 1-1.8-.6L7 5.3a1 1 0 0 0-1.4 1.4L8 9"/><path d="m21 3-6 6"/><path d="M3 21l6-6"/></svg>'
IC_KEY = '<svg class="vic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.5 12.5 8-8"/><path d="m16 7 3 3"/></svg>'


def specs_row(listing: dict, cls: str = "specs") -> str:
    return (
        f'<ul class="{cls}">'
        f'<li>{IC_BED}<span><strong>{listing["beds"]}</strong> bed</span></li>'
        f'<li>{IC_BATH}<span><strong>{listing["baths"]}</strong> bath</span></li>'
        f'<li>{IC_AREA}<span><strong>{listing["sqft"]:,}</strong> sqft</span></li>'
        f"</ul>"
    )


def residence_ld(listing: dict) -> dict:
    """schema.org SingleFamilyResidence, embedded on every page that shows this home so all
    extraction paths return the same code-keyed record (clean dedupe)."""
    photo = main_photo(listing)
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
        "image": photo.get("large2x") or photo.get("large"),
        "url": f"{BASE_URL}/listings/{listing['slug']}.html",
        "offers": {
            "@type": "Offer",
            "price": listing["price"],
            "priceCurrency": "CAD",
            "availability": "https://schema.org/InStock",
        },
    }


FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />'
)


def document_head(title: str, description: str, path: str, og_type: str, image: str, jsonld) -> str:
    canonical = f"{BASE_URL}{path}"
    blocks = ""
    if jsonld is not None:
        blocks = f'\n    <script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n    </script>'
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
    {FONTS}
    <link rel="stylesheet" href="/assets/styles.css" />
    <meta property="og:site_name" content="{esc(REALTOR['agency'])}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:title" content="{esc(title)}" />
    <meta property="og:description" content="{esc(description)}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{esc(image)}" />{blocks}
  </head>
  <body>
    <header class="nav">
      <div class="nav-in">
        <a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span>{esc(REALTOR['agency'])}</a>
        <nav class="nav-links">
          <a href="/">Home</a>
          <a href="/listings/">Listings</a>
          <a href="/about.html">About</a>
          <a class="btn btn-sm" href="/about.html#contact">Book a showing</a>
        </nav>
      </div>
    </header>
"""


def site_footer() -> str:
    links = "".join(
        f'<li><a href="/listings/{x["slug"]}.html">{esc(x["street"])}</a></li>' for x in LISTINGS[:4]
    )
    return f"""    <section class="cta">
      <div class="wrap cta-in">
        <div>
          <h2>Thinking of buying or selling on the shoreline?</h2>
          <p>Let's talk. No pressure, just honest local advice.</p>
        </div>
        <a class="btn btn-lg" href="tel:{esc(REALTOR['phone'])}">Call {esc(REALTOR['phone'])}</a>
      </div>
    </section>
    <footer class="foot">
      <div class="wrap foot-in">
        <div class="foot-brand">
          <div class="brand"><span class="brand-mark" aria-hidden="true"></span>{esc(REALTOR['agency'])}</div>
          <p>{esc(REALTOR['tagline'])}</p>
          <p class="muted">{esc(REALTOR['name'])} &middot; {esc(REALTOR['phone'])}<br />{esc(REALTOR['email'])}</p>
        </div>
        <div>
          <h4>Listings</h4>
          <ul>{links}</ul>
        </div>
        <div>
          <h4>Areas served</h4>
          <ul><li>Sarnia</li><li>Bright's Grove</li><li>Point Edward</li><li>Corunna</li></ul>
        </div>
      </div>
      <div class="wrap fineprint">
        <p>Sample site with synthetic listings, built to demo <a href="https://realtyrecall.mahimai.ca">RealtyRecall</a>. Not a real brokerage. Photography via <a href="https://www.pexels.com">Pexels</a>.</p>
      </div>
    </footer>
  </body>
</html>
"""


def listing_card(listing: dict) -> str:
    photo = main_photo(listing)
    return f"""        <a class="card" href="/listings/{listing['slug']}.html">
          <div class="card-media">
            <img loading="lazy" src="{esc(photo.get('large'))}" alt="{esc(photo.get('alt') or listing['street'])}" />
            <span class="tag">For sale</span>
            <span class="price-pill">{money(listing['price'])}</span>
          </div>
          <div class="card-body">
            <h3 class="card-street">{esc(listing['street'])}</h3>
            <p class="card-area">{esc(listing['area'])}, ON</p>
            {specs_row(listing, "specs mini")}
          </div>
        </a>
"""


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
    home_ld = [org_jsonld] + [residence_ld(x) for x in LISTINGS[:3]]
    hero = PHOTOS.get("hero") or {}
    hero_img = hero.get("large2x") or hero.get("large") or ""
    agent = PHOTOS.get("agent") or {}
    featured = "".join(listing_card(x) for x in LISTINGS[:3])
    values = f"""
        <div class="value"><span class="vico">{IC_PIN}</span><h3>Rooted in the shoreline</h3><p>I live and work here. I know the streets, schools, and which docks catch the sunset.</p></div>
        <div class="value"><span class="vico">{IC_HAND}</span><h3>Honest, no pressure</h3><p>My job is the right home, not the fast one. You'll always know exactly where you stand.</p></div>
        <div class="value"><span class="vico">{IC_KEY}</span><h3>From first condo to forever home</h3><p>First-time buyers and downsizers alike get the same patient, hands-on guidance.</p></div>
"""
    quotes = "".join(
        f'<figure class="quote"><blockquote>&ldquo;{esc(q)}&rdquo;</blockquote><figcaption>&mdash; {esc(who)}, {esc(where)}</figcaption></figure>'
        for q, who, where in TESTIMONIALS
    )
    body = f"""    <section class="hero" style="background-image: linear-gradient(180deg, rgba(10,26,45,.42), rgba(10,26,45,.72)), url('{esc(hero_img)}')">
      <div class="wrap hero-in">
        <p class="eyebrow">{esc(REALTOR['area'])}</p>
        <h1>Find your place on Lake Huron.</h1>
        <p class="hero-sub">{esc(REALTOR['tagline'])} Browse every current listing, or reach out for a no-pressure conversation.</p>
        <div class="hero-cta">
          <a class="btn btn-lg" href="/listings/">Browse listings</a>
          <a class="btn btn-ghost btn-lg" href="/about.html">Meet {esc(REALTOR['name'].split()[0])}</a>
        </div>
        <div class="hero-stats">
          <div><strong>{len(LISTINGS)}</strong><span>homes for sale</span></div>
          <div><strong>{REALTOR['sold']}</strong><span>homes sold</span></div>
          <div><strong>Since {REALTOR['since']}</strong><span>serving Sarnia</span></div>
        </div>
      </div>
    </section>
    <main class="wrap">
      <section class="section">
        <div class="section-head">
          <h2>Featured homes</h2>
          <a class="more" href="/listings/">View all {len(LISTINGS)} &rarr;</a>
        </div>
        <div class="grid">
{featured}        </div>
      </section>

      <section class="section agent">
        <div class="agent-photo"><img src="{esc(agent.get('large') or agent.get('medium') or '')}" alt="{esc(REALTOR['name'])}" /></div>
        <div class="agent-copy">
          <p class="eyebrow">Meet your agent</p>
          <h2>{esc(REALTOR['name'])}</h2>
          <p>For over a decade I've helped families buy and sell across {esc(REALTOR['area'])}, from first condos near the water to waterfront homes in Bright's Grove. My style is {esc(REALTOR['tone'])}.</p>
          <div class="chips"><span>Local since {REALTOR['since']}</span><span>{REALTOR['sold']} homes sold</span><span>5-star service</span></div>
          <a class="btn" href="/about.html">More about me</a>
        </div>
      </section>

      <section class="section">
        <div class="values">{values}</div>
      </section>

      <section class="section">
        <h2 class="center">What clients say</h2>
        <div class="quotes">{quotes}</div>
      </section>
    </main>
"""
    return (
        document_head(
            f"{REALTOR['agency']} | Homes in {REALTOR['area']}",
            REALTOR["tagline"] + " Current homes for sale across " + REALTOR["area"] + ".",
            "/", "website", hero_img, home_ld,
        )
        + body
        + site_footer()
    )


def render_about() -> str:
    agent = PHOTOS.get("agent") or {}
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
        "image": agent.get("large"),
        "knowsAbout": ["residential real estate", "waterfront homes", "first-time buyers"],
    }
    body = f"""    <main class="wrap">
      <section class="section about">
        <div class="about-photo"><img src="{esc(agent.get('large2x') or agent.get('large') or '')}" alt="{esc(REALTOR['name'])}" /></div>
        <div class="about-copy prose">
          <p class="eyebrow">About</p>
          <h1>{esc(REALTOR['name'])}</h1>
          <p>I'm {esc(REALTOR['name'])}, the realtor behind {esc(REALTOR['agency'])}. For over a decade I've helped families buy and sell across {esc(REALTOR['area'])}, from first condos near the water to waterfront homes in Bright's Grove.</p>
          <p>My style is {esc(REALTOR['tone'])}. I'd rather you find the right home than the fast one, and I know these streets, schools, and shorelines like my own backyard.</p>
          <p class="pull"><em>&ldquo;{esc(REALTOR['tagline'])}&rdquo;</em></p>
          <div class="chips"><span>Local since {REALTOR['since']}</span><span>{REALTOR['sold']} homes sold</span><span>5-star service</span></div>
          <div id="contact" class="contact-card">
            <h3>Book a showing</h3>
            <p>Call or email and we'll find a time that works.</p>
            <p class="contact-lines"><a href="tel:{esc(REALTOR['phone'])}">{esc(REALTOR['phone'])}</a><br /><a href="mailto:{esc(REALTOR['email'])}">{esc(REALTOR['email'])}</a></p>
          </div>
        </div>
      </section>
    </main>
"""
    return (
        document_head(
            f"About {REALTOR['name']} | {REALTOR['agency']}",
            f"{REALTOR['name']} of {REALTOR['agency']}, serving {REALTOR['area']}. {REALTOR['tagline']}",
            "/about.html", "profile", agent.get("large") or "", person_jsonld,
        )
        + body
        + site_footer()
    )


def render_listings_index() -> str:
    cards = "".join(listing_card(x) for x in LISTINGS)
    all_ld = [residence_ld(x) for x in LISTINGS]
    body = f"""    <main class="wrap">
      <section class="section">
        <p class="eyebrow">For sale</p>
        <h1>All listings</h1>
        <p class="lede">{len(LISTINGS)} homes currently for sale across {esc(REALTOR['area'])}.</p>
        <div class="grid">
{cards}        </div>
      </section>
    </main>
"""
    return (
        document_head(
            f"All listings | {REALTOR['agency']}",
            f"Every current home for sale with {REALTOR['agency']} across {REALTOR['area']}.",
            "/listings/", "website", (PHOTOS.get("hero") or {}).get("large") or "", all_ld,
        )
        + body
        + site_footer()
    )


def render_listing(listing: dict) -> str:
    photos = listing_photos(listing)
    main = photos[0] if photos else {"large2x": "", "large": "", "alt": listing["street"]}
    thumbs = "".join(
        f'<img loading="lazy" src="{esc(p.get("medium") or p.get("large"))}" alt="{esc(p.get("alt") or listing["street"])}" />'
        for p in photos[1:3]
    )
    gallery = f'<div class="gallery-thumbs">{thumbs}</div>' if thumbs else ""
    features = "".join(f"<li>{esc(f)}</li>" for f in listing["features"])
    agent = PHOTOS.get("agent") or {}
    body = f"""    <main class="wrap detail">
      <nav class="crumbs"><a href="/">Home</a> / <a href="/listings/">Listings</a> / <span>{esc(listing['street'])}</span></nav>
      <div class="gallery">
        <img class="gallery-main" src="{esc(main.get('large2x') or main.get('large'))}" alt="{esc(main.get('alt') or listing['street'])}" />
        {gallery}
      </div>
      <div class="detail-grid">
        <article class="detail-main">
          <span class="tag">For sale</span>
          <h1>{esc(listing['street'])}</h1>
          <p class="detail-area">{esc(listing['area'])}, ON &middot; {esc(listing['postal'])}</p>
          <p class="detail-price">{money(listing['price'])}</p>
          {specs_row(listing)}
          <p class="detail-desc">{esc(listing['desc'])}</p>
          <h3>Highlights</h3>
          <ul class="features">{features}</ul>
          <p class="mls">MLS&reg; {esc(listing['code'])}</p>
        </article>
        <aside class="agent-card">
          <img src="{esc(agent.get('large') or agent.get('medium') or '')}" alt="{esc(REALTOR['name'])}" />
          <h3>{esc(REALTOR['name'])}</h3>
          <p class="muted">{esc(REALTOR['agency'])}</p>
          <a class="btn btn-block" href="tel:{esc(REALTOR['phone'])}">Book a showing</a>
          <p class="agent-phone">{esc(REALTOR['phone'])}</p>
        </aside>
      </div>
    </main>
"""
    return (
        document_head(
            f"{listing['street']}, {listing['area']} | {money(listing['price'])}",
            listing["desc"],
            f"/listings/{listing['slug']}.html", "product",
            main.get("large2x") or main.get("large") or "", residence_ld(listing),
        )
        + body
        + site_footer()
    )


def render_sitemap() -> str:
    paths = ["/", "/about.html", "/listings/"] + [f"/listings/{x['slug']}.html" for x in LISTINGS]
    urls = "\n".join(f"  <url><loc>{BASE_URL}{p}</loc></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


CSS = """:root{
  --navy:#0e2338; --navy2:#16324f; --gold:#c39a4d; --gold-d:#a8823a;
  --ink:#1b2734; --muted:#5f6f80; --line:#e6eaf1; --soft:#f4f7fb; --bg:#ffffff;
  --shadow:0 14px 40px rgba(16,38,66,.12); --radius:16px;
}
*{box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{margin:0;font-family:Inter,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg);line-height:1.6;}
h1,h2,h3,h4{font-family:Fraunces,Georgia,serif;line-height:1.12;color:var(--navy);margin:0 0 .4em;font-weight:600;}
h1{font-size:clamp(30px,5vw,50px);}
h2{font-size:clamp(24px,3.4vw,34px);}
a{color:var(--navy);text-decoration:none;}
a:hover{color:var(--gold-d);}
img{max-width:100%;display:block;}
.wrap{max-width:1140px;margin:0 auto;padding:0 22px;}
.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:700;color:var(--gold-d);margin:0 0 8px;}
.muted{color:var(--muted);}
.center{text-align:center;}
.lede{font-size:19px;color:var(--muted);}
.ic{width:18px;height:18px;flex:0 0 auto;color:var(--gold-d);}
/* buttons */
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--navy);color:#fff;border-radius:999px;padding:11px 20px;font-weight:600;font-size:15px;transition:transform .15s,background .15s,box-shadow .15s;}
.btn:hover{background:var(--navy2);color:#fff;transform:translateY(-1px);box-shadow:var(--shadow);}
.btn-sm{padding:8px 16px;font-size:14px;}
.btn-lg{padding:14px 26px;font-size:16px;}
.btn-ghost{background:transparent;border:1.5px solid rgba(255,255,255,.7);color:#fff;}
.btn-ghost:hover{background:rgba(255,255,255,.14);color:#fff;}
.btn-block{display:flex;justify-content:center;width:100%;}
/* nav */
.nav{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.92);backdrop-filter:saturate(160%) blur(8px);border-bottom:1px solid var(--line);}
.nav-in{max-width:1140px;margin:0 auto;padding:14px 22px;display:flex;align-items:center;justify-content:space-between;}
.brand{display:inline-flex;align-items:center;gap:10px;font-family:Fraunces,serif;font-weight:700;font-size:19px;color:var(--navy);}
.brand-mark{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:9px;background:var(--navy);color:var(--gold);font-size:14px;font-weight:700;letter-spacing:.02em;}
.brand-mark::before{content:"BH";}
.nav-links{display:flex;align-items:center;gap:22px;}
.nav-links a{color:var(--ink);font-weight:600;font-size:15px;}
.nav-links a.btn{color:#fff;}
/* hero */
.hero{background-size:cover;background-position:center;color:#fff;}
.hero-in{padding:96px 22px 84px;max-width:1140px;}
.hero h1{color:#fff;max-width:16ch;}
.hero .eyebrow{color:#f0d9a6;}
.hero-sub{font-size:19px;max-width:56ch;color:rgba(255,255,255,.92);}
.hero-cta{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px;}
.hero-stats{display:flex;gap:40px;margin-top:44px;flex-wrap:wrap;}
.hero-stats strong{font-family:Fraunces,serif;font-size:30px;display:block;color:#fff;}
.hero-stats span{color:rgba(255,255,255,.82);font-size:14px;}
/* sections */
.section{padding:64px 0;border-bottom:1px solid var(--line);}
.section:last-child{border-bottom:0;}
.section-head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:24px;}
.more{font-weight:700;color:var(--gold-d);}
/* grid + cards */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:26px;}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;color:inherit;transition:transform .18s,box-shadow .18s;}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow);color:inherit;}
.card-media{position:relative;aspect-ratio:4/3;overflow:hidden;}
.card-media img{width:100%;height:100%;object-fit:cover;transition:transform .4s;}
.card:hover .card-media img{transform:scale(1.05);}
.tag{position:absolute;top:12px;left:12px;background:var(--gold);color:#241a06;font-size:12px;font-weight:700;padding:5px 11px;border-radius:999px;letter-spacing:.03em;}
.price-pill{position:absolute;bottom:12px;left:12px;background:rgba(14,35,56,.92);color:#fff;font-weight:700;padding:7px 14px;border-radius:999px;font-size:16px;}
.card-body{padding:16px 18px 20px;}
.card-street{font-size:20px;margin:0 0 2px;}
.card-area{color:var(--muted);margin:0 0 12px;font-size:14px;}
.specs{list-style:none;display:flex;gap:18px;padding:0;margin:0;flex-wrap:wrap;}
.specs li{display:flex;align-items:center;gap:7px;color:var(--muted);font-size:15px;}
.specs.mini li{font-size:14px;}
.specs strong{color:var(--ink);}
/* agent block */
.agent{display:grid;grid-template-columns:.9fr 1.1fr;gap:44px;align-items:center;}
.agent-photo img{width:100%;border-radius:var(--radius);box-shadow:var(--shadow);aspect-ratio:4/5;object-fit:cover;}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 22px;}
.chips span{background:var(--soft);border:1px solid var(--line);color:var(--navy);padding:7px 14px;border-radius:999px;font-size:13px;font-weight:600;}
/* values */
.values{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;}
.value{background:var(--soft);border:1px solid var(--line);border-radius:var(--radius);padding:26px;}
.vico{display:inline-grid;place-items:center;width:46px;height:46px;border-radius:12px;background:#fff;border:1px solid var(--line);margin-bottom:14px;}
.vic{width:24px;height:24px;color:var(--gold-d);}
.value h3{font-size:20px;}
.value p{color:var(--muted);margin:0;}
/* quotes */
.quotes{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;}
.quote{margin:0;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:26px;}
.quote blockquote{margin:0 0 14px;font-size:17px;}
.quote figcaption{color:var(--muted);font-weight:600;font-size:14px;}
/* cta */
.cta{background:var(--navy);color:#fff;}
.cta-in{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:52px 22px;flex-wrap:wrap;}
.cta h2{color:#fff;margin:0 0 6px;}
.cta p{color:rgba(255,255,255,.82);margin:0;}
.cta .btn{background:var(--gold);color:#241a06;}
.cta .btn:hover{background:#d4ab5c;}
/* footer */
.foot{background:#0a1a2d;color:#c7d2df;padding:52px 0 10px;}
.foot .brand,.foot h4{color:#fff;}
.foot-in{display:grid;grid-template-columns:2fr 1fr 1fr;gap:32px;}
.foot h4{font-family:Inter,sans-serif;font-size:14px;letter-spacing:.06em;text-transform:uppercase;margin:0 0 12px;}
.foot ul{list-style:none;padding:0;margin:0;display:grid;gap:8px;}
.foot a{color:#c7d2df;}
.foot a:hover{color:#fff;}
.foot .muted{color:#8ea0b4;}
.fineprint{border-top:1px solid rgba(255,255,255,.12);margin-top:34px;padding-top:16px;font-size:13px;color:#8497ab;}
.fineprint a{color:#c7d2df;text-decoration:underline;}
/* about */
.about{display:grid;grid-template-columns:.8fr 1.2fr;gap:44px;align-items:start;}
.about-photo img{width:100%;border-radius:var(--radius);box-shadow:var(--shadow);aspect-ratio:4/5;object-fit:cover;position:sticky;top:96px;}
.prose p{font-size:17px;}
.pull{font-size:20px;color:var(--navy);border-left:3px solid var(--gold);padding-left:16px;}
.contact-card{background:var(--soft);border:1px solid var(--line);border-radius:var(--radius);padding:24px;margin-top:24px;}
.contact-card h3{margin-top:0;}
.contact-lines a{font-weight:600;}
/* detail */
.detail{padding-top:24px;}
.crumbs{color:var(--muted);font-size:14px;margin-bottom:16px;}
.crumbs a{color:var(--muted);}
.gallery{margin-bottom:30px;}
.gallery-main{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:var(--radius);box-shadow:var(--shadow);}
.gallery-thumbs{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px;}
.gallery-thumbs img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:12px;}
.detail-grid{display:grid;grid-template-columns:1.6fr .8fr;gap:40px;align-items:start;padding-bottom:64px;}
.detail-price{font-family:Fraunces,serif;font-size:34px;font-weight:700;color:var(--navy);margin:6px 0 16px;}
.detail-area{color:var(--muted);margin:0;}
.detail .specs{margin:0 0 22px;gap:24px;}
.detail-desc{font-size:17px;}
.features{columns:2;gap:24px;color:var(--muted);padding-left:18px;margin:0 0 22px;}
.features li{margin-bottom:6px;}
.mls{color:var(--muted);font-size:13px;letter-spacing:.04em;}
.agent-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:22px;text-align:center;position:sticky;top:96px;}
.agent-card img{width:96px;height:96px;border-radius:50%;object-fit:cover;margin:0 auto 12px;}
.agent-card h3{margin:0;}
.agent-phone{color:var(--muted);margin:12px 0 0;font-weight:600;}
/* responsive */
@media(max-width:860px){
  .agent,.about,.detail-grid,.foot-in{grid-template-columns:1fr;}
  .values,.quotes{grid-template-columns:1fr;}
  .about-photo img,.agent-card{position:static;}
  .hero-in{padding:72px 22px 60px;}
}
"""

FAVICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="#0e2338"/>'
    '<text x="32" y="44" font-family="Georgia, serif" font-size="30" font-weight="700" '
    'fill="#c39a4d" text-anchor="middle">BH</text></svg>\n'
)

ROBOTS = f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n"

README = f"""# Bluewater Homes (sample realtor site)

A **synthetic** real-estate site for a fictional agent, *{REALTOR['name']}* of
*{REALTOR['agency']}* ({REALTOR['area']}). Every listing is made up.

It exists so anyone can try [RealtyRecall](https://realtyrecall.mahimai.ca): paste this site's
URL into the console and watch one link fan out into all {len(LISTINGS)} listings plus an
inferred realtor profile.

Professional static site: schema.org JSON-LD, OpenGraph, and a sitemap, so onboarding extracts
the listings deterministically (no AI key required for the listing data). Photography from
[Pexels](https://www.pexels.com), resolved at build time into `assets/photos.json`.

Rebuild (photos cached; the key is only needed to refresh them, and never lands in output):

    python3 scripts/build.py                          # reuse cached photos
    PEXELS_API_KEY=... python3 scripts/build.py --refresh-photos
"""


def write(path: str, content: str) -> None:
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


def main() -> None:
    global PHOTOS
    print(f"Building {REALTOR['agency']} with BASE_URL={BASE_URL}")
    PHOTOS = load_photos()
    for old in (ROOT / "assets").glob("*.svg"):  # drop stale art, then rewrite the favicon
        old.unlink()
    write("assets/favicon.svg", FAVICON)
    write("index.html", render_home())
    write("about.html", render_about())
    write("listings/index.html", render_listings_index())
    for listing in LISTINGS:
        write(f"listings/{listing['slug']}.html", render_listing(listing))
    write("assets/styles.css", CSS)
    write("sitemap.xml", render_sitemap())
    write("robots.txt", ROBOTS)
    write("README.md", README)
    write(".vercelignore", "scripts/\nREADME.md\nassets/photos.json\n")
    print(f"Done: {len(LISTINGS)} listings + home/about/index.")


if __name__ == "__main__":
    main()
