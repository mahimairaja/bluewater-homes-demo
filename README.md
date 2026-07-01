# Bluewater Homes (sample realtor site)

A **synthetic** real-estate site for a fictional agent, *Morgan Bell* of
*Bluewater Homes* (Sarnia & Bright's Grove, Ontario). Every listing is made up.

It exists so anyone can try [RealtyRecall](https://realtyrecall.mahimai.ca): paste this site's
URL into the console and watch one link fan out into all 6 listings plus an
inferred realtor profile.

Professional static site: schema.org JSON-LD, OpenGraph, and a sitemap, so onboarding extracts
the listings deterministically (no AI key required for the listing data). Photography from
[Pexels](https://www.pexels.com), resolved at build time into `assets/photos.json`.

Rebuild (photos cached; the key is only needed to refresh them, and never lands in output):

    python3 scripts/build.py                          # reuse cached photos
    PEXELS_API_KEY=... python3 scripts/build.py --refresh-photos
