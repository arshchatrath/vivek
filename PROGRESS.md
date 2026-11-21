# Vivek progress

Updated: 21 November 2026

## Decisions

- Name: Vivek; green and warm neutral visual theme.
- Groq is the text model provider for this MVP, per the user's correction to the original xAI Grok specification. Gemini handles opt-in packaging images.
- Four Mosaic brands are included. The Fellowship story still needs the user's actual interview notes and a clearly described interview cohort; do not invent those findings.
- Zero-budget architecture: static Next.js export, FastAPI, PostgreSQL with pgvector, Redis quotas, MiniLM embeddings, and free developer API accounts.
- Health-sensitive fields remain unknown unless explicitly sourced and reviewed. Manufacturer descriptions are not independent clinical evidence.

## Completed locally

- Read the master specification and the earlier harness repository at `C:\Users\arshc\dev\agent-harness`; used its web-design and AI-agent profiles to shape the build and verification.
- Crawled official product sitemaps and Product JSON-LD with robots checks. Captured **323 unique product listings**: Man Matters 81, Be Bodywise 104, Little Joys 131, Root Labs 7. One discovered URL redirects to a duplicate product. All 323 have source links and per-field provenance.
- Saved private Crawl4AI Markdown for all 323 products in Git-ignored `data/artifacts/`. One print-encoding error was recorded after its Markdown was saved; there are 323 files.
- Started local Docker PostgreSQL/pgvector and Redis. Loaded 323 products and 323 source passages with 384-dimensional local embeddings. API uses PostgreSQL when `DATABASE_URL` is set, with local-seed fallback for development.
- Built source-linked catalog search, brand filters, product detail, pagination, comparison, a Groq text route with citation validation, pgvector and full-text retrieval, and a Gemini package-label route with consent and metadata stripping. Added daily provider call caps and source-only fallbacks.
- Built responsive desktop and mobile UI. Production Next.js static export passes. Six API tests pass. Real browser screenshots at 1440 and 390 widths show no overlapping sections.
- Added repeatable refresh script and setup guide.
- Added **Describe your concern** as the primary entry. It retrieves focused guidance with citations, supports an opt-in Groq passage search for follow-up questions, and displays checked ingredient or product-form examples. Urgent and care-first results suppress product matching. The twelve guides cover scalp flakes, acne, hair thinning, dry skin, rough bumps, sun protection, damaged hair, body odor, sleep, cavity prevention, dark spots, and constipation.
- Indexed 30 guidance passages in PostgreSQL. Scanned all 323 listings, including their captured page details, and recorded review candidates in `data/artifacts/catalog-concern-audit.json`. The audit found candidate mentions in 299 listings across 29 topic groups. The remaining listings are recorded for manual review.
- Moved the working concern form onto the first screen. Added quick examples, clearer navigation, and a mobile layout that keeps the primary action visible. Grouped product questions and label reading together, gave all four brands a place in the initial catalog results, and made the product and comparison dialogs keyboard-accessible.
- Created `Vivek - Mosaic Fellowship.pptx`, a five-slide deck with speaker notes, live MVP screenshots, and direct links to the health guidance and brand listings in the demo. The company slide shows the current catalog coverage and proposes two pilot measures.
- Refined the concern hero with clearer copy, a more compact form, and all twelve sample prompts available through the examples menu. Added a branded 3.2-second opening screen with a skip button, Escape dismissal, and reduced-motion support.
- Added microphone input using the configured Gnani key. Short audio clips are transcribed in Indian English and populate the editable concern field. The API checks consent, WAV format, and its Redis quota before sending audio to Gnani.
- Normalized storefront and comparison prices to rupees. The seven US Root Labs records show dated estimates using the 20 November 2026 FBIL rate. The original USD value remains visible in the product detail and in the source record.
- Audited the repository with Ponytail. Removed the duplicate catalog and its sync script, three unused direct development dependencies, and unused Next.js starter files. The static app reads the canonical catalog and sends display fields only. The uncompressed home export fell from 1,080,102 bytes to about 254,000 bytes.

## Verification and limits

- API health with the local database reports 323 products. The no-key chat route returns source cards. Using the locally configured keys, Groq's default `openai/gpt-oss-20b` returned the exact catalog price and a matching citation both with a selected product and with catalog retrieval. Gemini's default `gemini-3.1-flash-lite` read both ingredients from a synthetic package label. Image analysis was enabled for the local test process. Both model variables are optional overrides.
- The design gate ended its third round at `GATE: OPEN 48`. The reported hero wrapping, fold, and one-sided tab overflow findings cleared. The latest report includes section sizing, alignment, visuals, keyboard focus, and a small language selector. The final export enlarges that selector to 44 pixels and adjusts scroll behavior when controls receive focus. No waivers were applied. See `shots/gate-round-3.log` for the complete local report.
- The harness's code scan passes across eight frontend files. ESLint reported no errors and warned about unoptimized images and manually linked styles and fonts used by the static export.
- The local PostgreSQL and Redis ports now bind to `127.0.0.1`. Both services restarted successfully, and the database retained all 323 products and embeddings.
- The concern flow passed 25 API tests in total, including topic routing, source links, safety routing, and ingredient/form checks. A live scalp query used the PostgreSQL guidance index and returned matched listings. A live Groq follow-up selected the saved passage for when to seek care.
- The concern release build and frontend code scan passed. The design gate ended at `GATE: OPEN 38`, with the tablet navigation wrapping resolved. Visual and layout checks remain open. See `shots/gate-concern-final.log` for the details. No waivers were used.
- The redesigned static export and frontend scan pass. Browser checks on the local PostgreSQL-backed MVP covered the concern form and source links, keyboard focus, catalog search, two-brand comparison, label upload consent, and mobile navigation. All 25 API tests pass. PowerPoint rendered the five slides, and the deck passed package validation and design lint.
- The redesign's visual harness ended at `GATE: OPEN 24` after three rounds. The missing stylesheet, body-text contrast, outer container margins, and split alignment findings cleared. The remaining findings cover viewport-sized sections, page structure, repeated catalog cards, hero actions, and decorative visuals. The app uses sections that grow with results, uniform cards for comparison, and quick examples in the concern form. No waivers were applied. See `shots/gate-redesign-final.log` for the full report.
- The hero update passes the static build and frontend scan. Browser checks at 320, 390, 768, and 1440 pixels confirmed that the primary action fits in the opening viewport. The intro timer measured 3.2 seconds, both dismissal methods worked, and the scalp-flakes example still returned sourced guidance.
- A live browser test passed synthetic microphone audio through Gnani and returned the sourced scalp-flakes guide. It verified a rupee-only price comparison and the original US price in the detail view. The API suite now passes 29 tests.
- The final hero, voice, and pricing build ended its visual harness rounds at `GATE: OPEN 24`. The heading and shared column alignment findings cleared. The remaining report covers full-screen section sizing and structure, visuals, repeated cards, and multiple actions in the hero. No waivers were applied. Full output is in `shots/gate-hero-polish-final.log`.
- Fixed those 24 blocking layout findings. The fixed header, standalone product tools, and combined sources footer put the initial desktop sections on the viewport grid. The catalog now uses a product photo shelf and compact listing rows, with a native brand filter on mobile. Confirmed `GATE: PASS` with 19 advisory warnings and zero waivers in `shots/gate-findings-verified.log`. The production build, frontend scan, all 29 API tests, and desktop and mobile browser regression checks passed. The browser also verified live Gnani transcription, concern sources, label-upload consent, and product comparison.
- Product prices and images are observations from brand pages and may change. Ingredients, warnings, age guidance, independent evidence, reviews, and clinical claims are not yet verified or published as facts.
## Production preview

- [Vivek](https://vivek-fellowship.onrender.com) and the [FastAPI service](https://vivek-fellowship-api.onrender.com/api/v1/health) are on Render. Both services track the private [Vivek GitHub repository](https://github.com/arshchatrath/vivek). The initial deployment used application commit `0a561de`.
- Render PostgreSQL 17 and Key Value are private to the Singapore services. Initial deployment verified 323 catalog listings, 323 product embeddings, and 30 guidance passages from 12 topics in the hosted database.
- The user selected the free Render database, which expires on **21 December 2026 at 18:25 IST**. The API may take about a minute to wake after idle time. Provider credentials are configured in Render's API environment. [Deployment guide](docs/free-deployment.md)
- Production checks passed for site HTTPS, the mobile browser flow, exact CORS, four-brand catalog coverage, rupee pricing, PostgreSQL concern guidance and follow-ups, pgvector retrieval with Groq citations, and Gnani transcription. Gemini read a synthetic label. When a repeat call returned HTTP 503, Vivek displayed the label-reader fallback.
- The final API rollout starts directly from the seeded database. The 29 API unit tests passed.
- Added a dedicated chat at `/chat` with in-page conversation history, voice input, cited guidance, and follow-ups. An information icon explains Groq data sharing beside the follow-up action. The checkbox was removed from the homepage follow-up form too.
- Added GSAP photo motion for pointer users and transitions for the navigation, dialogs, results, and composer. Motion respects the system preference. Checked the static export at seven viewport sizes from 320px to 1440px, including landscape.
- Fixed catalog results overlapping the following section on short desktop screens. Search prioritizes product titles, empty results offer a filter reset, and the comparison bar stays within the catalog. Product cards and details display a brand fallback when an image fails to load.
- Added `hairloss` as a hair-shedding alias and normalized whitespace before matching concerns. Updated the README with a live screenshot, a diagram, and the distinction between initial concern routing and product retrieval.

## Next work requiring external input

1. Review source coverage and sensitive fields with brand officials. Promote approved ingredient and warning facts only after per-field verification. The change log records later listing differences.
   Expand the concern corpus from the audit in priority order. Have a clinician review guidance and checkout risk before external use. Many child nutrition, supplement, and symptom-related listing claims still need evidence review.
2. Provide actual interview notes and the problem statement for the Fellowship submission.
3. The long-term specification includes accounts, saved routines, journals, reviews, checkout guidance, admin workflows, stronger moderation and privacy controls, and clinical evidence integration.
