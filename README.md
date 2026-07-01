# Bluewater Homes (sample realtor site)

A **synthetic** real-estate site for a fictional agent, *Morgan Bell* of
*Bluewater Homes* (Sarnia & Bright's Grove, Ontario). Every listing is made up.

It exists so anyone can try [RealtyRecall](https://realtyrecall.mahimai.ca): paste this site's
URL into the console and watch one link fan out into all 6 listings plus an
inferred realtor profile.

Pure static HTML with schema.org JSON-LD, OpenGraph, and a sitemap, so onboarding extracts the
listings deterministically (no AI key required for the listing data).

Regenerate after changing `scripts/build.py`:

    python3 scripts/build.py https://your-deployed-url.vercel.app
