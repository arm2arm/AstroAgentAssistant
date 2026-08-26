# DRP Hub live site notes

Grounded from live inspection of `https://drphub-p4n.aip.de` during a paper/slides revision session.

## Confirmed homepage metadata
- HTML `<title>`: `DRP Hub - Research Infrastructure for Particle Physics & Astrophysics`
- Meta description mentions:
  - `PUNCH4NFDI`
  - `reproducible workflows`
  - FAIR principles (`Findable, Accessible, Interoperable, Reusable` wording on site; some older skill text used `Repeatable`)
- Open Graph title/description also frame the site as PUNCH4NFDI research infrastructure.
- The homepage exposes an alternate link for OAI-PMH:
  - `/oai?verb=Identify`

## Frontend bundle signals
Inspection of the deployed JS bundle exposed strings and code paths indicating:
- registry-oriented pages/components
- bookmarking features
- sharing / shared-with-me flows
- active REANA configuration handling
- auth / sign-in flows

These signals justify wording such as:
- "DRP Hub acts as a registry, collaboration layer, and execution gateway for Digital Research Products."
- "The site appears designed for discovery, provenance inspection, bookmarking, sharing, and REANA-aware workflow context."

## Caution on claims
Use careful wording:
- Distinguish **confirmed public-site/UI concepts** from **backend behaviour that was not fully exercised in session**.
- Good: "frontend and site metadata indicate bookmark/share/registry/REANA-aware concepts"
- Avoid: claiming a specific backend execution feature definitely works unless directly verified in the session.

## Useful paper/slides wording
Short form:
> DRP Hub is more than a passive catalogue: it is a registry and collaboration layer for Digital Research Products, with public FAIR-oriented metadata and signals of REANA-aware workflow integration.

Longer form:
> DRP Hub presents Digital Research Products as executable, inspectable, and shareable research objects rather than static repository links. Public site metadata and frontend structure support describing it as a combined registry, collaboration layer, and REANA-aware gateway for reproducible workflows.
