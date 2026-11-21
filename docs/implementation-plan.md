# Vivek implementation plan

## Product focus

The first usable journey is official product discovery, readable source-backed facts, comparison, and a cited text answer. The architecture preserves the master specification's later image, review, routine, parent and admin modules. The Fellowship demo will focus on the actual interview brand once the user's research is supplied.

## Data path

Official sitemap → access-policy check → deterministic per-page Product JSON-LD extraction → field provenance → review state → PostgreSQL catalog → full-text and pgvector indexes. Crawl4AI independently captures private Markdown for later review. Crawl jobs run separately from user requests. Recrawls compare hashes and queue changes; they never overwrite approved critical fields.

## Milestones

1. Foundation: Next.js frontend, FastAPI backend, PostgreSQL/pgvector schema, environment validation, CI and local setup.
2. Catalog: crawl the four official brands, audit ten product pages, publish source-backed non-clinical facts, report coverage and missing fields.
3. Answer: hybrid retrieval, Groq synthesis, citation validation, safety and quota rules, feedback and source explorer.
4. Vision and discovery: OCR first, consented Gemini fallback, label reading, product match, comparison and ingredient explorer.
5. Reviews and personal workflows: first-party reviews and moderation, routines, private progress and deletion/export.
6. Governance and release: parent safeguards, regulatory references, admin approvals, monitoring, accessibility, security testing, deployment and Fellowship walkthrough.

## Acceptance rules

- Every published product fact points to a captured source and timestamp. Missing facts display as unknown.
- A product-specific AI claim cites a resolvable passage or is withheld.
- A text-only request never calls Gemini. Budget exhaustion has a usable non-AI path.
- Sensitive uploads require consent and owner-only access.
- Comparison never treats a manufacturer claim or review as independent proof.
- The catalog can be refreshed without silently replacing approved warnings, ingredients or age limits.

## External dependencies

Groq and Gemini API keys; PostgreSQL connection; hosting and private storage accounts; research details; review of health and child-data workflows. Public catalog ingestion proceeds under the user's stated permission, with access controls respected and source policies recorded.

