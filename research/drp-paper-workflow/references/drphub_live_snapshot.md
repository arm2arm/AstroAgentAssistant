# DRP-Hub Live API Snapshot as Paper Evidence (2026-08-23)

Reusable pattern for producing "system in operation" evidence in a
paper that describes a live registry. Capture a timestamped read-only
snapshot from the production API and embed verbatim API responses as
exhibits — never hand-paraphrase system state.

## API access
- Base: `https://drp-term.kube.aip.de/api/v1` (health: `GET /health`, no auth).
- Endpoints are `/products`-based — `GET /cards` 404s (old skill
  wording is wrong). OpenAPI at `/docs`.
- Token: read `~/.hermes/secrets/drphub_token.txt` at runtime, never
  inline in tool args (drphub-cards token-truncation pitfall).
- Use the helper pattern from the `drphub-cards` skill
  (urllib, Idempotency-Key on mutations — not needed for read-only).

## Snapshot recipe (read-only, ~5 calls)
1. Sweep `GET /products?limit=100&fields=...` following
   `next_cursor` until exhausted. Fields worth projecting:
   `id,title,product_status,visibility,maturity_level,source_type,has_reana,run_count`.
2. Aggregate (Python Counter): totals by status, visibility,
   maturity, source_type; `sum(has_reana)`; `sum(run_count)`.
3. Flagship (published) product: full `GET /products/{id}`,
   `GET /products/{id}/maturity`, `GET /products/{id}/audit?limit=N`.
4. Optionally `GET /config` for declared capabilities (idempotency
   TTL, auth modes, page size) — good one-liner in the architecture
   section.
5. Dump to a JSON file (e.g. `/tmp/drphub_snapshot.json`) so the
   paper's numbers are reproducible from one artifact.

## What to embed in the paper
- One stats paragraph (timestamped: "captured 2026-08-23").
- One flagship-product table (abridged record extract).
- One verbatim `/maturity` JSON response (the core exhibit).
- One short audit-log excerpt.
- Appendix: fuller verbatim records + API examples.

## Claim-verification rules (learned the hard way this session)
- **DOI/URL verification:** before asserting any DOI or URL in the
  paper, probe it: `curl -s -o /dev/null -w "%{http_code}" -I <url>`.
  The flagship's `doi` field was `10.5281/zenodo.9999999` — a
  placeholder that 404s. Phrase as "DOI field set, pending minting"
  and let the computed-maturity `missing` list carry the real claim
  ("one field and one human act from publication-grade").
- **Stored vs computed maturity:** the flagship stored
  `maturity_level=0` while `/maturity` computed L2. Present this gap
  as the diagnostic exhibit, not a data error.
- **Counts are a point-in-time:** always timestamp the snapshot;
  re-capture if the paper sits for weeks before submission.

## Baseline snapshot 2026-08-23 (for drift detection)
69 products (24 public / 21 internal / 24 private); 55 repo / 12
clone / 2 manual sources; 41 REANA-capable; 260 total runs; 1
published = `9c7f3bef-ae97-4044-9910-8724b294c3ff` ("Plot Linear
Functions with pandas and matplotlib", run_count=6, validation
passed, oai_published=true, computed maturity L2, missing L3:
validation_scope, missing L4: human_reviewed).
