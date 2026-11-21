# WELLWISE — Master Product Requirements & Engineering Build Specification

**Working name:** WellWise — Understand Before You Buy  
**Version:** 1.1 | **Prepared:** 20 November 2026  
**Purpose:** Full-scope build brief for Codex or another coding agent  
**Status:** Product proposal, not a launched or medically certified service  
**Primary market:** India, multilingual-first; architect for international expansion

> **Executive direction for the coding agent:** Build the complete, production-minded consumer platform described in this document. Do not silently cut features or replace real integrations with fake data. Deliver in phases, with an executable end-to-end application after each phase. Implement the broad, multi-brand vision, with a specifically configurable Mosaic Fellowship demonstration focused on **one brand and one validated customer problem**. Treat all medical/wellness claims as evidence-sensitive. Do not fabricate professional review, government approval, product facts, review verification, or live integrations.

---

## 0. Decisions already made

1. **Keep full product scope.** The platform spans Mosaic Wellness brands and relevant competing products, with patient/customer education, product discovery, reviews, progress tracking, and verified evidence.
2. **Use RAG (retrieval-augmented generation)** to answer against curated, cited source material instead of inventing answers from a model's general knowledge.
3. **Grok/xAI is the primary text model** for routine questions, conversation, structured synthesis and natural-language explanations.
4. **Gemini is the primary vision model** for user-submitted images. An image pipeline first extracts *observable information* and passes structured, sanitized observations to the text/RAG pipeline; Gemini does not independently issue final health advice.
5. **Avoid unnecessary Gemini calls** because its available credits/budget may be limited. Use low-cost deterministic image handling and caching before invoking Gemini. Grok does not need to see the full image to explain retrieved information.
6. **No product-only bias.** Compare Mosaic and competitor products fairly, disclose commercial relationships, distinguish paid placement, and do not recommend a purchase when evidence or safety does not support it.
7. **The user wants the complete platform, not a stripped-down MVP.** Phase delivery is an engineering organization strategy, not permission to omit the later modules.
8. **Formal government verification is an aspiration, not an existing endorsement.** Provide provenance, applicable regulatory-record lookups and expert reviews; only describe an agency as an approver if actual verification is documented.
9. **Safety first for users and children.** The app provides education and decision support; it must not act as a diagnostic service or prescribe treatment without a separately compliant, clinician-led pathway.
10. **Pre-populated database first:** Ingest, normalize, verify and index available product/evidence information **before public launch**. Answer user requests primarily from this database; never crawl the whole web on every question.
11. **Crawler choice:** Use self-hosted **Crawl4AI** as the preferred permitted website crawler, falling back to sitemap parsing, JSON-LD, HTML parsing, and Playwright where appropriate. Self-hosting avoids hosted crawler page-credit costs but not compute/API costs.
12. **Keep source detail:** Preserve raw authorized page snapshots or lawful references, page-level Markdown, field-level provenance and structured records; do **not** reduce an entire site to one lossy summary before extraction.
13. **Fellowship compliance:** Research/interview at least five genuine customers of a *single* Mosaic brand; identify a single defensible problem after interviews; demonstrate the app solving that specific issue. A multi-brand architecture does not negate this requirement.

---

## 1. Vision, thesis, and success criteria

### 1.1 Vision

Create a trusted **consumer wellness information and product-decision platform** for Indian users. A customer can describe a skin/hair/wellness or family-product concern in ordinary language; upload photos of product packaging, labels, ingredients or, where safe, a concern; receive a careful layperson explanation rooted in credible evidence; compare Mosaic and other brands; inspect review evidence; choose what to do next; and optionally monitor their experience over time.

### 1.2 Core user problem hypotheses (validate, never declare proven)

- Customers struggle to translate technical medical/product terminology into clear actionable understanding.
- Advice across ads, influencers, e-commerce listings and search engines may be inconsistent or poorly sourced.
- Customers may not know which ingredients matter, how two products differ, or how to interpret claims.
- They may struggle to judge the reliability of ratings and reviews.
- Customers using longer-term routines may lack an organized way to log use and experience.
- Parents may have questions about children's product labels, ages, allergens and safety information.
- Ordering, wallet/discount, refund and consultation experiences may create additional friction for some brands; don't assume those problems exist for all customers.

### 1.3 Desired outcomes

**User:** greater comprehension, visible source quality, informed comparison, fewer misunderstandings, easier tracking, appropriate referrals.  
**Business:** test improvements in qualified engagement, confident product consideration, reduced product confusion and support burden.  
**Research:** discover and quantify actual problem frequency and severity from interviews and usability sessions.

### 1.4 Non-goals / prohibited shortcuts

- No confident diagnosis from a photograph or symptom text; no disease classification output passed off as certainty.
- No emergency triage replacement; show urgent-care advice for red flags.
- No prescription, medication changes, dosage instructions tailored to an individual, or individualized child treatment recommendations.
- No unsupported efficacy claims, fake review authenticity labels, fake scientific studies or fabricated regulatory approvals.
- No silent capture or indefinite storage of sensitive photos or medical information.
- No use of scraped copyrighted, personal or paywalled material without permission or suitable lawful basis.
- No assumption that an existing Grok or Gemini consumer subscription provides API credits: **API billing, availability and rate limits must be checked in the actual developer accounts**.

---

## 2. Brands and catalog scope

### 2.1 Brand universe

- **Man Matters:** men's hair, grooming and wellness.
- **Be Bodywise:** women's hair, body, skin and wellness.
- **Little Joys:** children's wellness and nutrition; parent-facing access and more conservative safeguards.
- **Root Labs:** Mosaic's unisex/Ayurvedic wellness brand, primarily available in the US at the time of research; handle country/currency/availability correctly.
- **Competitor brands:** extensible across Indian and international product catalogs. Include them objectively with accurate source attribution.

Brands and current catalogs must be discovered from official approved sources, not hardcoded assumptions. Start with seed records only where independently verified.

### 2.2 Product categories

Hair loss and hair care; scalp care; skin and acne-related cosmetics; body care; personal hygiene; nutrition and supplements; general wellness; children's nutrition and parent educational resources; ingredient libraries; devices/tools where appropriate; professional consultation pathways. Categories have distinct allowed-claims and safety policies.

### 2.3 Catalog model

Each product may include brand, title, category, variant, size, country, current status, official listing URL, label photographs, INCI/ingredient list, concentration if disclosed, directions from official packaging, warnings, age limits, allergens, claims, evidence links, regulatory references, price with timestamp and currency, stock/status if licensed API is available, review sources, and last verified date. **Unknown fields must remain unknown.**

---

## 3. User personas and jobs-to-be-done

| Persona | Job to be done | Important limits |
|---|---|---|
| First-time skincare shopper | Understand ingredients, compare products, avoid unsuitable claims | No clinical diagnosis |
| Hair-care customer | Understand a routine and documented limitations; compare products | No self-prescribing hair-loss medicines |
| Parent/guardian | Read label, age guidance, allergens and claims for a child's product | Guardian-gated; no child image diagnosis |
| Existing Mosaic customer | Understand purchased products, log adherence, review experiences | Don't infer clinical results |
| Product researcher | Review citations, compare competitors and price/claims | Source provenance and neutral ranking |
| Clinician/content expert | Review evidence, corrections and safety alerts | Authenticated credentialed workflow |
| Content administrator | Maintain catalog, evidence, review moderation and audit trail | No rewriting of immutable history |

---

## 4. Full feature inventory (deliver all modules)

### 4.1 Public website / onboarding

- Responsive landing page with clear trust statement and service limitations.
- Guest search and information exploration without forced login; opt-in account for saved history.
- English, Hindi and Hinglish; language detection and explicit language switch. Architecture for more Indian languages.
- Persona/category discovery and brand-neutral entry points.
- Accessibility: WCAG 2.2 AA target, keyboard navigation, readable mobile design, proper alt text, screen-reader labels.
- Introductory consent, privacy choices, image/health data disclosure and age/guardian controls.

### 4.2 Conversational wellbeing assistant (Grok primary)

- Natural-language chat: short or detailed answers, technical explanation then simple-language translation, inline definitions, follow-ups.
- Clarification questions for incomplete context; distinguish user-reported symptoms from confirmed conditions.
- RAG-grounded answers with in-text citations, excerpt previews, dates, and evidence quality.
- Show **What we know / What we don't know / When to seek professional help / Sources** when warranted.
- Ability to request independent product comparisons, review summaries, more detail or simpler language.
- User-selectable answer modes: Simple, Detailed, Ingredients, Evidence, Product Compare.
- Streaming responses, regenerate, feedback, report answer, save conversation, export data, delete history.
- No attempt to manufacture citations: unsupported responses should say the corpus does not establish the answer.

### 4.3 Image understanding (Gemini primary)

Supported input intents:

1. Photograph of product package or ingredient list: transcribe and identify **visible** label information; compare to catalog.
2. Product photo: possible catalog matches with uncertainty and user confirmation.
3. Photo of a cosmetic/skin/hair concern: describe observable characteristics only, explicitly non-diagnostic; ask relevant context and return educational resources / recommend professional care where warranted.
4. Progress photo (adult opt-in): dated private photo diary, standardized framing guidance and side-by-side comparison; **never claim photographic improvement equals clinical response**.
5. Screenshot of checkout/review/marketing claims: extract visible claims and explain their meaning, without inferring legitimacy from appearance.
6. Documents (product insert or reports): only after explicit consent; extract the requested content and explain jargon, subject to strict medical safety restrictions.

Processing contract: MIME sniffing, size limits, malware scanning, EXIF/location stripping, file type validation, moderation, optional crop/orientation correction, deduplication hash, transparent provider-call count and consent. Prefer deterministic QR/barcode/OCR/library lookups when sufficient, otherwise Gemini. Log errors without logging raw sensitive inputs. Never publicly expose user uploads.

### 4.4 Trusted evidence and source explorer

- Knowledge base segmented by ingredients, products, education, professional guidance, regulatory records, clinical evidence, manufacturer claims, and review experiences.
- Source cards: title, publisher, jurisdiction, content type, publication date, retrieval date, URL/license, applicability and limitations, review status, version.
- Exact passage-level citations for medical or product claims.
- Retrieval with query rewriting, hybrid keyword + vector search, metadata filters, reranking, passage deduplication, freshness rules and citation validation.
- Evidence hierarchy visible to the user, with nuance (e.g. a regulator listing ≠ proven efficacy; study quality varies).
- Editorial workflow for expert review with credential checks, approval scope, expiration/re-review and public correction history.
- Source challenge / flag incorrect citation / user report workflow.
- Government-agency data adapters for lawful, published records, preserving the agency's exact terms; **never equate a public registry hit with agency endorsement of WellWise**.

### 4.5 Product discovery and recommendations

- Find by problem **topic** (education first), ingredient, category, brand, intended use, budget, formulation preference, allergen constraints and country.
- Separate **neutral comparator** from sponsored placements; never rank a medical product using affiliate revenue.
- Eligibility & safety filters (age restrictions, contraindication warnings, known allergies, regulated product flags, missing data).
- Side-by-side product tables for price/size per unit, ingredients, product claims, label warnings, evidence, sources, review themes, retailer links.
- Relevance rationale: why shown, evidence behind match, data missing, comparable alternatives.
- Neutral "no product recommended" option, and pathway to professional advice.
- Ingredient interaction explanations only where supported by authoritative sources; never suggest unsafe combinations.
- Save products and lists; alerts when a product's facts or claims are corrected.

### 4.6 Reviews and review intelligence

- Collect first-party user reviews with consent, optional verified purchase only when backed by a real verified order source, reporting/moderation and anti-spam controls.
- Ingest third-party reviews **only via permitted sources/APIs or with explicit rights**, with provenance and timestamp.
- Review analysis: common themes, negatives/positives, ease-of-use, packaging, support, long-term experience, disclosed side effects; distinguish experience from proven effect.
- AI-generated summary **must hyperlink supporting reviews**, display sample count, date range and selection method.
- Filter by verified-purchase status (only if genuinely verifiable), time, product variant, usage duration and score.
- Prevent brigading, duplicate reviews, fake testimonials, ungrounded review statistics and personally identifying disclosures.
- Review dispute and removal process; no removal solely because a review is unfavorable.

### 4.7 Routine and experience tracker

- User-created routines with product names, label directions, check-ins, reminders, notes and optional symptom diary.
- Import recommended routine **only as user-confirmed product usage**, not a medical prescription.
- Photo journal for adults with explicit consent; make uploads private by default and deletable.
- Graphs for subjective self-reported observations and adherence (clearly labeled), not automated medical efficacy claims.
- Export PDF/CSV for discussion with a professional; optional reminder and refill planning.
- Consent-based multi-device sync and data export/deletion.

### 4.8 Cost, checkout and order-information companion

- Transparent effective-price comparison including pack size, discounts, wallet restrictions, shipping and taxes when source data is supplied.
- Explainers for coupons, wallet balances, refunds and support policies; show official source and last-checked date.
- Manual order-support timeline and support ticket notes; **do not show live orders/refunds without authorized partner API access**.
- Clear separation between sourced policy information and unverified user accounts.

### 4.9 Parent / child safety experience

- Guardian role, child-related product educational pages, label reading, age bands, ingredients, allergens and referral guidance.
- No personalized pediatric diagnosis, no independent child account or child-generated profile, no child-face analytics; require review by legal/privacy counsel before processing any child data.
- Strong privacy defaults, separate authorization and stricter moderation for uploads.
- Visible escalation to pediatricians/qualified professionals for medical concerns.

### 4.10 Admin and content operations

- Admin dashboard: brands, products, ingredients, knowledge sources, document ingest runs, chunk/citation inspector, search performance, flagged answers, review moderation, expert verification, regulatory references and publication control.
- Role-based access: superadmin, catalog editor, evidence reviewer, clinical reviewer, moderator, analyst, support.
- Source approval and content rollback; immutable audit log of changes to safety-critical product claims.
- Data freshness scheduler and human review queues.
- User reports, risk events, moderation and account deletion work queue.
- Read-only analytics with permissioned aggregate data; no individual health records in marketing dashboards.

### 4.11 Professional referral and escalation

- Rule-based warnings for urgent or significant symptoms: provide appropriate seek-care message, not a product offer.
- Professional directory or official consultation link only from validated sources; avoid inventing availability or credentials.
- Optional clinician-review workflow, **not** a fake live consultation service.

### 4.12 Future-grade extensions that remain in project scope

- Voice input/output with consent; regional-language expansion.
- Cross-border catalogs, region-specific claims, currencies and regulations.
- Regulatory record change alerts, evidence refresh jobs and product recall notices sourced to official registries.
- User opt-in public corrections and community Q&A with human moderation.
- Licensed merchant inventory, purchase verification and order status integrations where permission exists.
- Evaluated personalization using non-sensitive preferences; consent-first privacy-preserving cohort insights.

---

## 5. End-to-end UX journeys

### Journey A: Natural-language concern

1. User: "My skin gets oily and I don't understand these two cleansers."
2. Safety classifier checks risk and suitable answer scope; ask concise clarifications if needed.
3. Backend queries ingredient/product/guideline RAG corpus.
4. Grok synthesizes: technical summary → plain-language explanation → tradeoffs → evidence limitations → product comparisons → source links.
5. User opens a source excerpt, requests reviews, selects two products, compares and saves.
6. Optionally creates a personal routine and records experience.

### Journey B: Photo of packaging

1. User uploads photo and explicitly selects "Read a label".
2. Virus/type validation → strip EXIF → detect barcode/OCR where possible → catalog match.
3. If confidence insufficient, send to Gemini with task-specific, constrained prompt.
4. Return JSON of visible text/possible ingredients/missing or unreadable regions/confidence; ask user to confirm uncertain text.
5. Retrieve source-backed ingredient explainers via RAG.
6. Grok provides layperson summary and product comparisons; show original vs extracted text for correction.

### Journey C: Concern photo (adult)

1. Present privacy disclosure and "information only, not a diagnosis" statement; seek explicit consent.
2. Validate/scan/moderate photo and reject sensitive/unsupported contexts as needed.
3. Gemini returns *observable visual features* and cannot label a medical condition as certain.
4. Grok asks for contextual information; retrieve educational references.
5. Safety rules decide if product comparison is appropriate or should be suppressed for medical follow-up.
6. Show cited educational possibilities with uncertainty, self-care basics if supported and professional escalation instructions.

### Journey D: Parent checking a product

1. Parent chooses packaging/ingredient scan, not image-based child diagnosis.
2. Show age/allergen/label directions and source status with explicit unknowns.
3. Highlight any age-specific restrictions and recommend qualified professional consultation for individualized concerns.
4. Allow product comparison based on objective label data, not personalized medical claims.

### Journey E: Reviews

1. User selects product and requests "what do people dislike?"
2. Review engine retrieves permitted source reviews with citations.
3. Structured aggregation by theme and denominator, with data quality note and no unsupported percentage.
4. Grok summarizes competing themes and discloses anecdotal nature.
5. Show original excerpts within applicable usage rights.

---

## 6. AI architecture: Grok + Gemini routing

### 6.1 Mandatory division of responsibilities

**Grok (primary text / normal questions):** chat, clarify intents, explain technical text in easy English/Hindi/Hinglish, tool orchestration, RAG answer composition, ingredient explanation, review synthesis, grounded product-comparison narratives, summaries, structured outputs. It must work only with verified retrieved facts for medical or product-specific assertions.

**Gemini (primary image understanding):** analyze user-supplied image pixels, read packaging, extract legible labels, identify visible product features and summarize observations under strict vision-specific schemas. Call it **only when required**; image output is untrusted evidence until matched with independent sources or confirmed by user.

**Deterministic code, not LLM:** safety rules for explicit red flags, authentication, access control, ranking math, prices, discount calculations, review counts, source provenance, consent enforcement, retention/deletion, image hash/cache checks, and citation integrity validation.

**Fallbacks:** if Grok fails, return retrieved source snippets with a helpful explanation rather than hallucinating; if Gemini is unavailable or quota exhausted, allow text description, label transcription and barcode/catalog lookup, and show retry-unavailable state. Optional secondary provider must be explicitly configured and approved, not secretly substituted.

### 6.2 Routing decision table

| Input/request | Primary processing | Calls Gemini? |
|---|---|---|
| Text-only question | Intent → retrieve → Grok → cite | No |
| Plain-language explanation | Grok over citations | No |
| Product comparison | Structured DB + rules + Grok narrative | No |
| Review question | Review DB + aggregation + Grok summary | No |
| Image of package label | OCR/catalog → Gemini if necessary → RAG → Grok | Sometimes |
| Unknown product photo | Barcode/catalog matching → Gemini if needed → confirm | Sometimes |
| Adult concern photo | Explicit consent → Gemini visual observations → rules/RAG/Grok | Yes, when accepted |
| Progress photo upload | Secure storage and comparison UI; optional Gemini if user explicitly requests visual description | Not by default |
| Checkout screenshot | OCR first, Gemini if visual context essential | Sometimes |
| Unsafe or emergency content | Rules-based escalation + safe template | No necessary call |

### 6.3 Proposed orchestrator pseudo-code

```python
async def answer(request, user):
    enforce_consent_and_permissions(request, user)
    risk = safety_screen(request.text, request.image_metadata)
    if risk.requires_immediate_escalation:
        return safe_escalation_response(risk)

    observation = None
    if request.image is not None:
        observation = await image_pipeline(
            image=request.image,
            task=request.image_intent,
            prefer_local_ocr=True,
            use_gemini_only_if_needed=True,
        )
        if observation.is_unsupported:
            return ask_for_text_or_professional_assessment()

    retrieval_query = build_safe_query(request.text, observation)
    evidence = await hybrid_retrieve_and_rerank(retrieval_query, user.region)
    checked = validate_evidence(evidence)
    if not checked.sufficient_for_claim:
        return transparent_insufficient_evidence_response(checked)

    structured_options = rules_based_product_candidates(checked, user.safe_preferences)
    draft = await grok_generate_json(
        text=request.text,
        observations=observation,
        evidence=checked,
        product_options=structured_options,
        safety_policy=current_safety_policy(),
    )
    return validate_citations_claims_and_safety(draft, checked, structured_options)
```

### 6.4 Model/provider abstraction

Implement `TextModel`, `VisionModel`, `EmbeddingModel` interfaces with adapters, provider health checks, versioned model IDs and test mocks. Use environment-configured `XAI_TEXT_MODEL` and `GEMINI_VISION_MODEL`; **verify current accepted IDs in developer consoles rather than hardcoding a guessed free model**. Store the model ID/version on every generated artifact and review event. Pin versions in staging; use controlled upgrades.

### 6.5 Cost discipline and quotas

- Per-user, per-day and global quotas; monthly billing caps and alert thresholds; circuit breaker on budget exhaustion.
- Input token limits, retrieval passage limits, response length caps and server-side idempotency keys.
- Cache public product explanations and approved evidence queries with source/version fingerprint; cache image analyses **only within the user's authorized account** or for public non-personal product labels with appropriate consent/rights.
- Perform cheap barcode/OCR/metadata extraction before Gemini and ask for retake rather than repeatedly calling a vision API on blurry images.
- Batch ingestion/embeddings; keep chats concise; apply cost dashboards per workflow.
- Distinguish **user's subscription/credits** from server-side API usage. Current public pricing and availability can change; consult official docs during setup.
- Never send a sensitive image to any AI provider without explicit disclosure and lawful handling review of the provider's privacy/data-retention terms.

### 6.6 Required structured output objects

`VisionObservation`: `{intent, observed_text[], visible_features[], potential_product_matches[], unreadable_regions[], uncertainty[], safety_flags[], provider, model_id, created_at}`.

`Answer`: `{answer_simple, answer_technical, evidence_summary, uncertainty, follow_up_questions[], citations[], product_candidates[], red_flags[], seek_care_guidance, model_metadata}`.

`Citation`: `{source_id, document_id, chunk_id, excerpt_start, excerpt_end, title, url, published_at, retrieved_at, jurisdiction, source_type}`.

`ProductRecommendation`: `{product_id, eligible, rationale[], limitations[], evidence_ids[], sponsored, contraindication_flags[], missing_facts[]}`.

All JSON must be validated at API boundaries with typed schemas. **A model must never invent IDs**; all citations and products must resolve to backend records.

---

## 7. RAG knowledge and evidence ingestion

### 7.1 Authorized source classes

1. Government agencies and official public regulatory registries, product recalls, advisories and applicable rules.
2. Professional bodies, established hospital/clinical education pages and reputable guidelines.
3. Peer-reviewed papers/reviews, subject to quality evaluation and correct interpretation.
4. Official product labels, packaging, manufacturers' published specifications and warnings.
5. Licensed/authorized reviews, clearly marked anecdotal.
6. User-provided documents, accessible only within that user's tenancy/consent scope.

Candidate Indian sources and authorities to investigate: FSSAI for foods/nutraceuticals; CDSCO and applicable state authorities for medicines, cosmetics and medical-device regulatory aspects; relevant health ministry advisories; official laws and policies. Scope varies by product type. Confirm applicable classification before building a registry adapter.

### 7.2 Content pipeline

Discover source → rights/robots/access check → fetch with provenance → extract → sanitize → classify jurisdiction/category → metadata enrichment → document fingerprint → chunk at semantic boundaries → embedding → keyword index → editorial review → publish → monitor changes → re-review/retire.

Keep raw licensed snapshot or a legally appropriate reference, source URL, fetch timestamp, content hash, version, source-specific rights policy, quoted excerpt boundaries and ingestion errors.

### 7.3 Retrieval algorithm

- Query classification (medical education, ingredients, product, regulatory, review, logistics).
- Hybrid BM25/trigram keyword + semantic vector search across appropriate collections, with explicit filters for geography, source type, date, brand, product, user ownership and safety class.
- Rerank and deduplicate; ensure the answer doesn't collapse a manufacturer claim into scientific consensus.
- Cite specific passages, not just a generic source homepage.
- When evidence conflicts, show both positions and the evidentiary reasons for uncertainty.
- Do not use user reviews as the sole support for efficacy claims.
- No authoritative answer if the current evidence base cannot support it.

### 7.4 Evaluation and regression

Create a human-curated benchmark of at least 100 questions across labels, ingredients, brand comparisons, children, adverse reactions, missing evidence and malicious prompt injection. Measure citation precision, groundedness, unsupported claim rate, safety escalation recall, factual product match, language readability and latency. Store model/prompt/corpus version with each run.

---

## 7A. REQUIRED: Pre-launch product catalog, automated crawling and database-readiness architecture

**Architectural decision (mandatory):** WellWise uses a **pre-populated, continually maintained product catalog and evidence corpus**, not ad-hoc site crawling in the critical path of every user conversation. Before launch, ingest all *lawfully accessible and sufficiently verified* records possible from Mosaic brands and permitted competitor sources. “All products” is a coverage goal, **not a claim of complete access**: inaccessible, outdated, discontinued, or unverified items must be tracked transparently.

### 7A.1 Source inventory and priority

| Source | Example entry point | Data collected | Authority/limitations |
|---|---|---|---|
| Man Matters | https://manmatters.com/ | Official catalog, variants, ingredients, descriptions, directions, warnings, FAQs, product images | Manufacturer-authored; confirm label versions |
| Be Bodywise | https://bebodywise.com/ | Hair, skin and body product pages, ingredient lists, usage information, published claims | Manufacturer claims are not independently proven evidence |
| Little Joys | https://ourlittlejoys.com/ | Children's nutrition/wellness products, age and allergen information, nutrition labels | Apply child-specific safety and stricter validation |
| Root Labs | https://rootlabshealth.com/ | Published supplement facts, descriptions and label information | Verify current brand ownership, regional catalog and availability |
| Other Mosaic-affiliated catalogs | Discover and confirm official sites during source onboarding | Cross-linked products, variants, SKUs | Check official ownership and permission; avoid false affiliations |
| Tata 1mg / Nykaa / Amazon / other retailers | Their authorized feeds, APIs or permitted public listings | Cross-check pricing, packaging, SKU, availability; review metadata only where permitted | Not authoritative for formulation; honor terms and licensing |
| FSSAI / CDSCO / relevant official registries | https://fssai.gov.in/ ; https://cdsco.gov.in/ | Relevant regulations, alerts, official public records | Regulatory reference **does not** imply certification of WellWise or product efficacy |
| Peer-reviewed and reputable clinical sources | https://pubmed.ncbi.nlm.nih.gov/ and publisher-permitted abstracts/pages | Ingredient and product-category evidence, limitations, citations | Appraise evidence quality and context; don't infer branded efficacy |
| First-party reviews, licensed review feeds | Submitted with consent or under an explicit license | Review text/ratings, timestamps, product/variant link | Reviews are anecdotes; do not scrape/repost unlicensed material |

**Onboarding rule:** Verify current domains and brands, site terms, `robots.txt`, licenses, allowed request rates, terms of caching/retention and data-use permissions before each source connector is enabled. Do not bypass CAPTCHAs, paywalls, access controls, anti-bot defenses or login restrictions. No data source is assumed to grant unlimited crawling or republication merely because it is publicly visible.

### 7A.2 Crawler and extraction technology

- **Preferred free/self-hosted crawler: Crawl4AI** (https://docs.crawl4ai.com/). Support sitemap-driven URL discovery and extraction of LLM-ready Markdown, raw HTML where lawful, links and metadata.
- **Complementary deterministic tools:** sitemap XML parsing; `schema.org/Product` JSON-LD parsing; BeautifulSoup/Cheerio; Playwright only for necessary JavaScript-rendered pages; URL and canonical normalization.
- **Alternative tools if circumstances warrant:** SiteOne Crawler (desktop/offline exports), Firecrawl (hosted quota/paid credits), Apify (hosted budget). Do not rely on any advertised free-credit figure without checking current provider terms.
- **Grok**: per-page structured extraction, classification, normalization, conflict explanation, and text responses. Use typed JSON-schema-constrained output; do not make up missing fields.
- **Gemini**: interpret *permitted* product-label/packaging images when standard OCR or structured extraction cannot recover essential text. Invoke only after a quota check. Do not use Gemini for routine web text conversion or summarization.
- **OCR/barcode first**: use local OCR and barcode libraries as available; confirm label transcription and preserve uncertainty. Image processing may be subject to data rights and model costs.
- **Infrastructure**: Python ingestion workers, PostgreSQL for canonical records and job tracking, pgvector for retrieval, object storage only for permitted snapshots, Redis/queue for resumable tasks.

### 7A.3 Two separate data paths

**Offline / pre-launch ingestion (not user request):**

1. Register each authorized website and its crawl policy (allowed paths, robots, terms, rights, rate caps, owner).
2. Discover product URLs from sitemaps, official category indexes, canonical links and permitted navigation; deduplicate URL variants.
3. Queue crawl jobs using per-domain concurrency, request delay, retry with exponential backoff, timeout, checkpoints and resume support. Record pages blocked or inaccessible as `unavailable` rather than forcing access.
4. Fetch and preserve raw HTML, cleaned **per-page** Markdown, JSON-LD, title, canonical URL, fetch time, content hash, source rights policy, language, region and parse status where storing such material is allowed. If retention is not permitted, store a link and minimal lawful metadata only.
5. **Deterministic extraction first**: product ID/SKU, manufacturer, brand, name, variant, price/currency/time, size, ingredients/INCI, nutrition facts, concentration, manufacturer claims, directions, warnings, intended age range, allergens, FAQ, packaging images, source URLs.
6. Send ambiguous *individual pages* or targeted source snippets to Grok for structured extraction only when needed. Require strict schema validation, evidence span/URL per important field, and `null` for unknown data. Do not feed one mega-summary of the entire website to Grok for product records.
7. Apply normalization: ingredient vocabulary, units and percentages, alias mapping, brand and SKU canonicalization, product/variant grouping, country-specific versions, duplicate detection and discontinued-item handling.
8. Compare conflicting manufacturer vs retailer vs label fields. Preserve each version and provenance, assign `needs_review` to conflict/high-risk fields, and route for editorial or qualified expert review as appropriate.
9. Publish approved structured catalog records and evidence documents to their separate read models; chunk semantically and embed only permitted text into pgvector (with keyword/FTS indexes).
10. Generate **derived** per-product summaries and optional category/website overviews for browsing; summaries are never the sole retained source of ingredients, claims or warnings.
11. Run coverage and quality checks, record missing-field rates, expose source links, and establish launch readiness before enabling catalog answers to users.

**Online / user request path:**

1. User asks a text question, describes a concern, scans a label, or uploads an eligible image.
2. Run consent/safety and intent routing. Text goes to the Grok-oriented pipeline; image requires OCR/metadata checks and optional budgeted Gemini vision.
3. Retrieve matching structured products, ingredient facts, relevant evidence passages and permitted review data from the **already populated** database; apply category, region, recency and safety filters.
4. Grok produces a concise sourced explanation, explains uncertainties and differences among claims, and optionally enables neutral product comparison. Medical escalation rules may prevent product recommendations.
5. Cite field-level source URLs / evidence passages; show stale or unknown data. Do not pretend an absent product or attribute was found.
6. When information is missing, optionally perform an allowed **background-on-demand source discovery job** with explicit rate and policy checks; never insert unverified crawl output directly as an authoritative answer. Queue review and ingest first; meanwhile respond that information is currently unavailable.

**Performance principle:** Chat requests read the prebuilt catalog/RAG index. Crawling is an asynchronous maintenance/ingestion process with separate failure modes and budgets. Never block all user Q&A on a website being online.

### 7A.4 Storage domains and exact schemas

The following are **logical domains**, which may live in one secured PostgreSQL instance and optionally separate schemas. They are not necessarily three different database servers:

1. **Product catalog:** brands, products, regional variants/SKUs, ingredients, label snapshots, concentrations, directions, contraindications/warnings, manufacturer claims, prices, public links, change history, field verification.
2. **Evidence and RAG corpus:** official policies, scientific abstracts/articles as licensed, clinical/professional guidance, ingredient explanations, regulator records, embeddings, citation spans, editorial decisions.
3. **Reviews and user experience:** user-submitted/authorized external reviews, moderation, provenance, user preferences, saved product comparisons, routines and progress history. User-private data **must not leak into shared RAG embeddings or other users' retrieval**.

Minimum normalized product JSON representation (illustrative only; use relational entities plus typed API schemas):

```json
{
  "product_id": "uuid",
  "brand": "Be Bodywise",
  "name": "Example product name — placeholder",
  "category": "body_care",
  "product_type": "cosmetic",
  "region": "IN",
  "variants": [],
  "ingredients": [],
  "active_ingredients": [],
  "ingredient_concentrations": [],
  "manufacturer_claims": [],
  "independently_supported_claims": [],
  "usage_instructions": [],
  "warnings": [],
  "age_restrictions": null,
  "contraindications": [],
  "allergens": [],
  "nutrition_facts": null,
  "packaging_details": {},
  "regulatory_records": [],
  "product_images": [],
  "source_urls": [],
  "source_last_fetched_at": null,
  "last_verified_at": null,
  "publication_status": "needs_review"
}
```

**Field-level provenance** is mandatory. For each extracted attribute (especially ingredients, strengths, warnings, age limits, regulatory claims) store `source_id`, `source_url`, `captured_at`, `source_type`, `content_hash`, optional evidence span/offset, `extraction_method`, `verification_status`, reviewer identity where applicable, and `verified_at`. These should not be hidden in one loosely formatted description blob. `confidence` can guide review but is not independent verification.

Additional suggested tables: `crawl_sources`, `crawl_policies`, `crawl_jobs`, `crawl_pages`, `crawl_failures`, `crawl_checkpoints`, `extraction_runs`, `product_source_fields`, `product_conflicts`, `product_dedup_matches`, `catalog_coverage`, `publication_decisions`, `catalog_change_events`, `refresh_schedules`. Hash/version page and product snapshots separately. Enforce canonical product IDs and unique product-variant mappings.

### 7A.5 Refresh, change detection, and publication

- **Before launch:** Full permitted seed crawl, extraction, human review of critical fields, normalized catalog, evidence index, and quality report. Never claim complete coverage of inaccessible pages.
- **After launch baseline:** Weekly permitted product-page refresh; more frequent (e.g., daily) *lightweight change checks* for high-priority products if allowed, and less frequent stable-document reviews. These are configurable starting policies, not guaranteed provider commitments.
- Compute canonical page/content hashes to skip unchanged pages and avoid repeated Grok and embedding costs; compare snapshots and retain source history.
- When content changes, identify affected products/fields, invalidate only impacted derived summaries/embeddings/caches, and queue verification. Don't overwrite a verified ingredient/warning with unreviewed text.
- Track product launch, variant changes, reformulations, out-of-stock status only where lawful/current, removals, redirects, and broken source links. Mark stale records clearly.
- **Regulatory/recall alerts:** Separate high-priority checks where public feeds exist; never assert a product is recalled without precise official evidence and matching SKU/region.
- Monitor provider usage separately: crawl compute, xAI tokens, Gemini vision calls, embeddings, storage, bandwidth. Implement budget thresholds, request dedup, optional human approvals and failure alerts.
- If a crawler, source site, or AI provider is unavailable, retain last **approved** version with a visible `last_verified_at` and freshness status, or suppress unsupported high-risk guidance.

### 7A.6 Admin data operations and metrics

Build a dedicated admin interface showing: brand/domain intake, site policy/rights status, discovered/crawled/product URL counts, extraction successes and failures, unique products vs variants, catalog completeness, missing ingredient/warning fields, duplicate/conflict queue, pending editorial approval, freshness/stale rate, last crawl time, next refresh, data-source provenance, per-provider cost, and export to CSV/JSONL (only for permitted data). Support re-crawl single page/brand, rerun extraction, approve/reject fields, rollback publication, source deletion/takedown and repeatable audit logs.

**Launch acceptance checks:**

- A seeded, audited Mosaic catalog exists in PostgreSQL *before* the public chat is enabled, with actual fetched/approved records and an explicit product coverage report.
- An automated sitemap-to-catalog test reliably captures at least 10 permitted product pages in a pilot, then expands to all reachable authorized product pages; no invented 100%-coverage claim.
- Product detail pages show source URL, timestamp, ingredient list where disclosed, missing-field treatment, region and variant identity.
- Grok answers a product-specific question **from retrieved stored content**, citing the product page/field; it must not silently fetch live web content or hallucinate absent facts.
- Gemini is never called for text-only queries or ordinary page conversion; packaging-image use is gated by OCR, budget and user consent.
- Re-crawling unchanged pages triggers zero unnecessary Grok extraction and embedding calls; a changed ingredient or warning creates a reviewable difference without silently overwriting the approved record.
- A missing/unavailable product returns a clear knowledge-gap message and optionally queues lawful discovery instead of offering an invented recommendation.
- Health claims and restricted product categories are reviewed under the existing safety policy, and privacy/tenant isolation tests pass.

### 7A.7 Practical Codex implementation order for ingestion

1. Create the source registry and page-rights policy model.
2. Implement sitemap/URL discovery and Crawl4AI adapter with domain-scoped limits, resume, retries and crawl log.
3. Persist authorized raw per-page artifacts and structured `crawl_pages` metadata.
4. Parse Product JSON-LD/HTML deterministically; define Pydantic schemas, ingredient normalization and variant dedup.
5. Add Grok fallback extraction for ambiguity and Gemini label-image extraction only where justified.
6. Create field provenance, conflict detection, publication approval, normalized PostgreSQL catalog and admin dashboard.
7. Index approved permitted passages in pgvector + keyword retrieval, then build cited Grok product Q&A.
8. Implement delta refresh jobs, snapshot diffing, stale indicators, metrics and CSV/JSONL exports.
9. Pilot on one brand with 10 items; review extraction quality; expand to other brands and authorized competitor sources.
10. Maintain a documented product-coverage report, ingestion runbook and cost dashboard. Continue delivery of **all other features** in this specification; ingestion priority does not narrow product scope.

---

## 8. Product recommendation and trust engine

### 8.1 Ranking factors

Hard safety/eligibility checks first → user intent/category match → source completeness → objective product fit → availability/location → transparent price/quantity → user preferences. User reviews are supplementary context, not independent efficacy evidence.

Avoid medical outcome likelihood estimates and opaque "98% match" claims. Explain missing constraints and uncertainty. Paid placements are separately labeled and cannot override safety.

### 8.2 Compare view

Top summary, price per standardized unit, ingredients, concentrations if confirmed, product purposes as represented by labels, cautions, strength of independent evidence for relevant ingredients (not implied product-level efficacy), review themes/count/source, citations and last verified date.

### 8.3 Trust and verification statuses

Use precise labels such as: `Official manufacturer label`, `Public regulatory record found`, `Independently reviewed evidence`, `Clinician-reviewed explanation`, `Customer-reported experience`, `Unverified claim`, `Information outdated`. Never use `Government approved` unless the specific exact approval scope, issuing authority and reference are verified.

---

## 9. Suggested full-stack architecture

### 9.1 Stack

- **Web:** Next.js + TypeScript + App Router, Tailwind CSS, accessible component library, PWA capabilities.
- **API:** Python FastAPI for ingestion, AI orchestration, health-content safety, structured services; optionally Next.js BFF for session-specific endpoints.
- **Database:** PostgreSQL, `pgvector`, PostgreSQL full-text indexing; Redis for queues/rate limits/cache.
- **Background jobs:** Celery/RQ/Arq with Redis or an equivalent durable queue; ingestion, embeddings, monitoring and reminders.
- **Objects:** S3-compatible private storage for user images, public assets and protected source snapshots; signed URLs.
- **AI:** xAI/Grok text adapter; Google Gemini image adapter; independent versioned embedding adapter; OCR/barcode service.
- **Auth:** passwordless/email/OAuth with secure sessions, RBAC and guardian constraints.
- **Observability:** OpenTelemetry, structured metrics/tracing, alerting and error tracker; redact sensitive values.
- **Hosting:** Dockerized services with a repeatable staging/production deployment and automated backups; prefer managed DB for reliability.

### 9.2 Monorepo layout

```text
wellwise/
  apps/
    web/                     # Next.js public product, user account and admin
    api/                     # FastAPI routes
  packages/
    ui/                      # Reusable design system
    schemas/                 # API contracts and generated types
    config/                  # Lint/types/build settings
  services/
    rag/                     # Search, ingestion, embeddings, citation resolver
    orchestration/           # Grok router, Gemini vision, safety decision engine
    catalog/                 # Products, brands, ingredients, comparisons
    reviews/                 # Ingest, moderation, thematic summaries
    tracking/                # Routine and progress records
    jobs/                    # Scheduled work and retries
  infra/
    docker/ terraform/ migrations/ observability/
  data/
    seeds/ fixtures/ allowed-sources/
  evals/
    qa/ safety/ groundedness/ image/ cost/
  docs/
    architecture/ decisions/ regulatory/ research/ api/
  .env.example
  README.md
  AGENTS.md
```

### 9.3 Security boundaries

Public catalog and published evidence | private user health-related records/images | admin content editing | professional review | third-party AI providers must be distinct trust domains. Enforce authorization on every record rather than only hiding UI routes.

---

## 10. Database blueprint (initial entities)

Use UUID primary keys, timestamps, optimistic versioning and audit triggers for critical content.

| Domain | Entities / key relationships |
|---|---|
| Identity | `users`, `profiles`, `roles`, `user_roles`, `sessions`, `consents`, `guardian_attestations` |
| Catalog | `brands`, `categories`, `products`, `product_variants`, `product_ingredients`, `ingredients`, `product_labels`, `product_claims`, `prices`, `product_links`, `catalog_versions` |
| Evidence | `sources`, `documents`, `document_versions`, `chunks`, `embeddings`, `citations`, `evidence_reviews`, `source_checks`, `regulatory_records`, `correction_events` |
| Conversations | `conversations`, `messages`, `message_citations`, `ai_runs`, `user_feedback`, `safety_events` |
| Images | `uploads`, `vision_observations`, `upload_consents`, `file_deletion_jobs` |
| Reviews | `reviews`, `review_sources`, `review_flags`, `review_verifications`, `review_summaries`, `moderation_actions` |
| Recommendation | `recommendation_sessions`, `recommended_products`, `saved_products`, `comparison_lists` |
| Tracking | `routines`, `routine_items`, `routine_checkins`, `progress_notes`, `progress_photos`, `reminders` |
| Support/commerce | `saved_offers`, `price_observations`, `support_cases`, `support_updates` |
| Governance | `audit_logs`, `admin_approvals`, `expert_credentials`, `provider_usage`, `quota_limits`, `data_requests` |
| Crawling and catalog QA | `crawl_sources`, `crawl_policies`, `crawl_jobs`, `crawl_pages`, `crawl_failures`, `crawl_checkpoints`, `extraction_runs`, `product_source_fields`, `product_conflicts`, `product_dedup_matches`, `catalog_coverage`, `publication_decisions`, `catalog_change_events`, `refresh_schedules` |

**Minimum fields examples:**

- `sources`: title, URL, publisher, source_kind, jurisdiction, license, published_at, last_fetched_at, status, reliability_notes.
- `documents`: source_id, content_hash, version, ingestion_state, visibility, rights_status.
- `chunks`: document_id, passage text, offsets, lexical index, embedding vector, safety tags, approved_at.
- `products`: brand_id, canonical_name, country, category, status, source_ids, verification_timestamp.
- `reviews`: product_variant_id, rating, text, created_at, source_url, authenticity_status, consent, moderation_status.
- `ai_runs`: provider, model, workflow, prompt_version, evidence_ids, tokens, latency, cost_estimate, outcome; **no raw confidential prompt logs by default**.
- `uploads`: owner_id, intent, encrypted storage key, content_hash, MIME, consent_id, retention_until, deletion_status.

Index products on brand/category; chunks with pgvector and FTS; reviews on product/date; restrict user-owned records via backend row-level access rules and optionally PostgreSQL RLS.

---

## 11. API contract map

All endpoints versioned under `/api/v1`, documented in OpenAPI and validated with Pydantic/Zod.

| Method + endpoint | Purpose |
|---|---|
| `POST /chat/sessions` | Start anonymous/authenticated session |
| `POST /chat/{id}/messages` | Grounded chat response, optional streaming |
| `POST /uploads/init` | Authorize upload with intent and consent |
| `POST /uploads/{id}/analyze` | Run OCR/Gemini and store observations |
| `DELETE /uploads/{id}` | User deletion, cascade jobs |
| `GET /products` | Search/filter products |
| `GET /products/{id}` | Evidence-backed product detail |
| `POST /products/compare` | Deterministic compare table |
| `GET /ingredients/{slug}` | Ingredient explainer + sources |
| `GET /sources/{id}` | Full source metadata and permitted excerpt |
| `GET /reviews` | Filter and paginate sourced reviews |
| `POST /reviews` | New review with moderation |
| `GET /review-summaries/{product_id}` | Cited aggregate summary |
| `POST /routines` | Save routine |
| `POST /routines/{id}/checkins` | Record user-reported usage |
| `GET /progress` | User-owned history and private photo metadata |
| `GET /me/data-export` | Export request/status |
| `DELETE /me` | Account deletion and audit confirmation |
| `POST /feedback` | Report quality/safety issue |
| `GET /admin/ingestion` | Ingestion jobs/status |
| `POST /admin/sources` | Add candidate source |
| `POST /admin/sources/{id}/approve` | Human gate for publishing |
| `GET /admin/ai-runs` | Redacted provider usage and quality metrics |
| `GET /health` / `GET /ready` | Deployment probes |

Pagination, status codes, idempotency, rate limits and validation errors are mandatory. Generate an OpenAPI client and checked-in example requests.

---

## 12. UI/UX pages and design principles

**Pages:** home, onboarding/consent, Explore, AI chat, image upload wizard, analysis result, product search, brand page, product detail, ingredient wiki, evidence source detail, product compare, review explorer, routine builder, calendar/check-ins, progress journal, saved items, support/checkout explainer, account/privacy, professional help, admin login, content admin, reviews moderation, evidence verifier, analytics dashboard, user-reported corrections.

**Visual direction:** calm, premium, scientific but accessible, distinctly Indian-localized without overstating authority. Spacious cards, mobile-first sticky search/chat composer, clear sourcing panels, high-contrast typography, restrained colors for safety alerts. Never disguise advertising as medical guidance.

**Interaction requirements:**

- Chat composer accepts text, camera/photo upload and optional speech; shows which AI capability will be used and why.
- Toggle "Explain simply" and "Show technical detail"; no loss of factual nuance.
- Sources open in a side panel with quoted passage, source date, jurisdiction and limitations.
- Product comparison supports 2–4 items, sortable objective columns, missing data markers.
- Review summary displays citations, total sample and known selection bias.
- Mobile image workflow supports retake/crop and opt-in upload status.
- Save and account actions show clear privacy choices.
- Admin pages visually distinguish draft vs approved source content.

---

## 13. Safety, privacy and compliance gates

1. **Scope classification:** educational/product informational vs possible medical advice. Route possible diagnosis or individualized treatment to safe guidance and professional consultation.
2. **Urgent health concerns:** provide generic urgent-care instructions when red flags are detected; do not suggest products alongside emergencies.
3. **Child data:** guardianship, minimization, no personalized pediatric photo diagnosis, conservative age-related warnings, legal review before live processing.
4. **Privacy:** India's DPDP Act and DPDP Rules, including phased applicability, require jurisdiction-specific legal review. Provide purpose-based notices, informed consent where required, withdrawal/deletion, retention limits, breach-handling processes and vendor governance. Do not claim compliance based on a checklist alone.
5. **Vendor contracts:** evaluate xAI and Google API privacy, training, retention and processing geography before sending health-related content; allow opting out of image analysis.
6. **AI transparency:** label AI-generated content, model limitations, date of evidence, and distinction between image observations and diagnosis.
7. **Regulatory status:** never assert that WellWise, its AI, any individual response, or all catalog products are certified by FSSAI/CDSCO or a government agency. Show precise verifiable record numbers only where applicable.
8. **Adverse event handling:** if users report serious side effects, don't run them through normal recommendation flow; provide seek-care messaging and appropriate official reporting links as verified.
9. **No prompt injection:** treat retrieved pages, uploaded images/OCR and reviews as untrusted data. They may never override system safety rules or reveal keys or hidden prompts.
10. **Abuse prevention:** WAF, CAPTCHA on abuse spikes, per-IP/user quotas, audit logs, CSRF protection, XSS sanitation, signed uploads, dependency scanning, secrets management and routine backups.
11. **Medical device / telemedicine classification:** obtain qualified legal and clinical review before expanding to diagnosis, triage, treatment or prescription functions; evaluate any applicable CDSCO medical-device software guidance.
12. **Security testing:** IDOR/access control, document injection, malicious file uploads, secret leakage, review manipulation, OAuth/session handling, database backup recovery.

Ship health-sensitive features only after relevant safeguards and review gates pass, even though the full features remain in scope.

---

## 14. Data sourcing strategy (real data, no fabrications)

### Phase of source acquisition

1. Official Mosaic brand sites and official product listings; manually curate baseline facts.
2. Confirm packaging, directions, ingredients, availability and category-specific warnings.
3. Competitor official product labels, legally accessible catalogs and manufacturer documentation.
4. Public regulator records, guidance and research sources; check licensing/usage conditions.
5. Reviews only from lawful API/licensed feeds or consenting first-party submissions; store source, author attribution where allowed, publication date and rights conditions.
6. Expert review of high-stakes educational content and content correction workflow.

**Important:** web content may be stale, incomplete or misleading. Build scheduled verification, source conflict workflows, provenance displays and graceful missing-data UI. Do not auto-publish a new health claim simply because one web page mentions it.

---

## 15. Testing plan and quality bars

### 15.1 Automated testing

- Type checking, formatting, linting, unit tests and DB migration tests.
- AI provider adapter mocked tests; integration smoke tests with explicit opt-in actual API calls.
- RAG regression tests for citation integrity, no support → no authoritative claim, source freshness and adversarial prompt injection.
- Vision quality tests: blurry packaging, mirrored text, cropped labels, bad lighting, mismatched brands, skin-image uncertainty, child-image rejection paths.
- Security: authorization, upload validation, consent, deletion cascade, excessive usage limits.
- E2E: Playwright desktop/mobile flows from landing → ask → source → compare → review → save.
- Accessibility automated checks plus manual keyboard/screen-reader tests.

### 15.2 Suggested release gates (targets, calibrate with real evaluation)

- Zero known critical or high-severity authorization/secret-exposure issues.
- Zero fabricated citation IDs in a curated 100+ answer benchmark.
- 100% of displayed review-verified badges backed by a verifiable source.
- 100% of source-backed medical/product claims either cite resolvable evidence or explicitly disclose that support is unavailable.
- 100% of sensitive-image uploads require an applicable consent path and deletion support.
- Document and review child-safety and emergency-escalation adversarial cases before production release.
- Set and monitor latency/error/cost SLOs based on measured staging performance rather than inventing performance figures.

---

## 16. Observability, analytics and business evaluation

**Product funnel:** visit → educational search → useful answer → source opened → product compared → product saved → informed outbound click (optional) → follow-up satisfaction.  
**User quality:** perceived clarity, confidence, reported understanding, harmful/incorrect-answer reports, product preference change, sourced-answer satisfaction.  
**RAG quality:** groundedness, citation accuracy, retrieval coverage, unanswered queries, expert correction backlog, source freshness.  
**Model economics:** Grok token cost / request, Gemini image analysis calls / user, cache hit rates, budget alerts, rate-limit incidents.  
**Reviews:** ingestion source count, review provenance coverage, sample size, moderation backlog.  
**Privacy:** retention jobs completed, user export/deletion turnaround, unauthorized access alerts.

Prefer consented, aggregated analytics; avoid logging individual symptoms, uploaded images or identifiable child data into third-party analytics products.

---

## 17. Development roadmap — full scope, incremental delivery

**Milestone 0 — Validation and technical foundations**
- Conduct five+ genuine customer interviews for a chosen Mosaic brand. Record anonymized issues and permissioned identifying details separately.
- Define primary journey/problem and measurable research thesis without changing the product's full multi-brand architecture.
- Bootstrap monorepo, CI, environment management, style system, DB, API schema, auth, telemetry, policy docs and Docker staging.

**Milestone 1 — Catalog and evidence infrastructure**
- **Pre-launch mandatory:** Build the Crawl4AI-based site discovery/crawler, extract official catalog pages one-by-one, validate and publish real product records into PostgreSQL before public chat launch. Pilot on 10 permitted products then expand to all reachable authorized pages; report coverage gaps.
- Build JSON-LD/HTML deterministic extraction before Grok structured extraction; use Gemini only for essential product-label image interpretation when OCR is insufficient.
- Build per-field source provenance, product/variant dedup, conflicts, change detection, admin approval queues and scheduled re-crawls.
- Real brand/category/product/ingredient data model; source registry and document ingest pipeline.
- Hybrid search, embeddings, citation passage links, evidence review admin, source versioning and corpus tests.

**Milestone 2 — Grok-first grounded conversational assistant**
- User text chat, context handling, multilingual explanation, source citation cards, structured safety checks, answer validation, feedback and saved chats.

**Milestone 3 — Gemini vision and multimodal UI**
- Consent-based image upload, OCR/barcode path, Gemini vision fallback, schemas, label inspection, screenshot extraction, adult concern photo safe flow, retake/uncertainty UX and privacy deletion.

**Milestone 4 — Product explorer and comparison**
- Mosaic and competitor products, neutral filters/ranking, ingredient wiki, full comparison, prices and policy explanation, sponsorship separation, unknown fields.

**Milestone 5 — Review intelligence**
- Lawful review sources, user submissions, moderation, verified-purchase semantics, Grok review synthesis with original-source backlinks, review theme analytics and dispute workflow.

**Milestone 6 — Tracking and personalization**
- Routine editor, check-ins, reminders, adult progress journals, image comparison, export and privacy controls.

**Milestone 7 — Child-focused education, support and verification**
- Parent-safe label exploration, age/allergen info, consultation/referral discovery, logistics/offer explanation, support timeline, agency-record adapters, expert approval queues.

**Milestone 8 — Production hardening and full delivery**
- Security and clinical review, performance, cost caps, scale testing, multilingual polish, accessibility, observability, deployment, backups, documentation and professional demo.

**Each milestone must include:** working tests, actual endpoints/UI, DB migration, usable fixtures clearly labeled as fixtures, relevant documentation, screenshots/video of functional flows, and a punch list of unfinished work. **Do not mark a milestone complete if its core features are placeholders.**

---

## 18. Required environment variables

Create `.env.example` with placeholders; **never hardcode or commit secrets**.

```dotenv
APP_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost:5432/wellwise
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT=
S3_BUCKET=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_REGION=
AUTH_SECRET=
XAI_API_KEY=
XAI_TEXT_MODEL=  # confirm available model ID in xAI console
GEMINI_API_KEY=
GEMINI_VISION_MODEL=  # confirm available model ID in Google AI Studio/API console
EMBEDDING_PROVIDER=
EMBEDDING_MODEL=
MONTHLY_AI_BUDGET_USD=
DAILY_VISION_CALL_LIMIT=
DAILY_TEXT_CALL_LIMIT=
ENABLE_IMAGE_ANALYSIS=false
ENABLE_CHILD_PRODUCT_EDUCATION=true
ENABLE_SENSITIVE_IMAGE_STORAGE=false
ENABLE_EXPERT_REVIEW_REQUIRED=true
```

Document local development, Docker Compose, migrations, seeding, provider configuration, staging, deployment and rollback in `README.md`. Validate required env vars at startup; fail safely for missing provider keys while allowing catalog browsing.

---

## 19. Definition of done and acceptance scenarios

### Scenario 1: Product ingredient photo

User photographs a skincare label → OCR or Gemini extracts visible ingredients → user confirms ambiguous text → app retrieves sourced ingredient information → Grok gives clear explanation and uncertainty → user compares against another real catalog product → citations open correctly. Must be complete without fake products or fabricated evidence.

### Scenario 2: Plain-text concern

User describes a common concern → Grok asks useful clarifications → retrieves appropriate literature → translates technical terms → provides grounded education, not diagnosis → relevant product categories only when safe → user can inspect sources and reviews.

### Scenario 3: Image safety

Adult uploads a possible medical concern → consent gate → vision returns observations, not certain diagnosis → model clearly distinguishes uncertainty and follows escalation rules. Parent attempting to submit a child's medical image receives safe boundaries and guidance, not diagnostic analysis.

### Scenario 4: Review credibility

User compares two products and requests negative reviews → same-product/variant reviews found from permitted sources → summary includes count, window, provenance and source links → no invented verified-purchase badge or efficacy conclusion.

### Scenario 5: Progress tracking

Account holder configures routine, checks in, stores optional private image, views dated self-report comparisons, exports/deletes records; unrelated account cannot access them.

### Scenario 6: Provider quota exhausted

Gemini budget cap hit → no accidental repeat charges; text/manual input path remains functional; Grok still answers text-only questions with sources. If Grok is also unavailable, show evidence excerpts and friendly error, never uncited invented output.

### Scenario 7: Government-source interpretation

An official public record is linked to a product → show issuing agency, exact reference, scope and date → do **not** label the entire platform as government-certified or treat registry existence as clinical validation.

### Scenario 8: Fellowship demonstration

From the customer research, choose one validated issue for one Mosaic brand → demonstrate interview-based rationale → complete flow resolving the selected issue → show user test feedback and how product decisions changed. Wider platform remains available in the repository but does not muddle submission narrative.

---

## 20. Fellowship research and submission plan

**Required discipline:** Five or more real customers of the *same* Mosaic brand and a connected working app solving the validated customer problem. Follow current official submission instructions for documents and deployed links.

Ask participants about actual recent experiences, not hypothetical willingness to use WellWise:

1. Which product(s) have you actually used, and when?
2. Walk me through your last purchase and first use.
3. What information did you search for before purchasing?
4. Which information was confusing or contradictory? Give a specific example.
5. How did you judge whether an ingredient, claim or review was trustworthy?
6. Have you ever compared this with another brand? Show what you checked if willing.
7. What did you do when unsure? How much time/effort did it take?
8. Were you confused about how to use the product or track your experience?
9. What was the most frustrating unresolved moment?
10. If this information problem disappeared, what would change about your buying decision?

After the interviews: transcribe only with permission; cluster problems by frequency, severity, recoverable evidence and feasible benefit; write a concise problem statement supported by exact anonymized quotes; test a clickable flow; run task-based usability tests and record results. Never manufacture interview data or claim fictional observations.

Suggested challenge narrative: **"Customers of [validated brand] struggle to assess conflicting product/ingredient information and compare options. Our evidence-backed, transparent assistant turns technical product information into understandable decisions."** Use this only if actual interviews support it.

---

## 21. Codex execution instructions

> Paste the following into Codex after placing this Markdown file at the repository root.

```text
You are the technical lead building WellWise. Read WELLWISE_MASTER_BUILD_SPEC.md completely and treat it as the product and engineering source of truth. Build the full platform incrementally; do not shrink the scope or arbitrarily delete modules.

Start by:
1. Inspecting the repository and writing docs/implementation-plan.md with dependencies, milestones, acceptance tests and any missing external credentials/data rights.
2. Creating the monorepo structure, environment validation, Docker Compose, PostgreSQL/pgvector + Redis, DB migrations, Next.js web and FastAPI API.
3. Designing the relational schema, typed API contracts, server-side authorization, source registry and safe upload lifecycle.
4. Building the complete **pre-population pipeline first**: source-rights registry -> sitemap discovery -> Crawl4AI permitted per-page crawl -> deterministic JSON-LD/HTML extraction -> schema-validated Grok extraction when needed -> field-level provenance/validation -> approved PostgreSQL catalog -> pgvector/FTS indexing. Pilot 10 real products, audit accuracy, then expand; keep raw page-level Markdown where legally permitted (do not collapse the entire site into one summary).
5. Building a functioning vertical slice using that populated catalog: indexed source passage -> hybrid retrieval -> Grok grounded text answer -> public UI with field-level citation links.
6. Adding catalog ops: refresh scheduler (weekly starting policy), content hashing, version diffs, stale states, dedup, manual approval dashboard, crawl coverage/export, and error/cost monitoring.
7. Adding Gemini vision as a separate, cost-capped adapter; OCR/barcode first; never route text-only requests to Gemini.
8. Progressing through ALL milestones described in the spec with automated tests, seed provenance, screenshots, run instructions and visible pending work.

Use real integrations when keys and rights are available. If not, implement testable provider interfaces and clearly labeled local fixtures, never pretend to have real live data, genuine reviews, government certifications or medical approvals. Prioritize user privacy, evidence integrity, safety and transparent limitations. Never implement diagnostic/prescription claims without professional/legal review. Do not commit keys. Keep docs/decisions.md and a running CHANGELOG.md. After each milestone, report the actual routes, tests, verified outputs and what remains to be built. Ask only for truly blocked credentials, licenses or policy decisions; otherwise proceed with the next safe implementation step.
```

### Deliverables the agent must produce

- Functional source code and repeatable local/production setup.
- Database schema, migrations, API documentation and data dictionary.
- Grok and Gemini provider integrations with cost/fallback tests.
- Cited evidence ingest/approval/retrieval engine and transparent **pre-seeded** catalog; Crawl4AI pipeline, per-page source artifacts, field-level provenance, audit/coverage reports, scheduled refreshes and admin QA dashboard.
- Full user journeys, user dashboard and admin workspace.
- Security, evaluation and accessibility test suites.
- Real-content sourcing and rights log, regulator/status interpretation guide.
- Fellowship interview analysis template and demo walkthrough.
- Production deployment plan, operations runbook, incident response and backup recovery guide.

---

## 22. Open dependencies and required decisions before production

The coding agent should track these explicitly, not invent answers:

- Production domain, brand identity, logo and final product name.
- xAI/Grok developer account/API key, eligible model and budget; rate limits in the actual account.
- Gemini developer account/API key, vision model and budget/credits; media processing and retention terms.
- Embedding model/provider and permitted document storage policies.
- S3-compatible storage, database, email and optional SMS/push provider credentials.
- Permission to ingest/store third-party catalog data, page snapshots, images, review data and official source documents; current crawl robots/terms and allowed rate policies.
- Any Mosaic partnership/API data access (otherwise build from public lawful sources only).
- Qualified clinician reviewers and legal review for content, child data, consent and regulated-feature boundaries.
- Genuine user interviews for Fellowship and written permissions for research information.
- Localizations beyond English/Hindi/Hinglish, jurisdiction rollout order and supported product categories by geography.

---

## 23. Official references and maintenance links

The following sites should be checked during development because plans, APIs, policies and product catalogs may change:

- Mosaic Wellness company and brands: https://mosaicwellness.in/
- Crawl4AI docs: https://docs.crawl4ai.com/
- Man Matters official: https://manmatters.com/
- Be Bodywise official: https://bebodywise.com/
- Little Joys official: https://ourlittlejoys.com/
- Root Labs candidate official: https://rootlabshealth.com/ (reconfirm current ownership/domain)
- Schema.org Product structured data: https://schema.org/Product
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Mosaic Fellowship challenge: https://mosaicfellowship.in/challenge
- Mosaic Fellowship submission: https://mosaicfellowship.in/submit
- xAI developer docs: https://docs.x.ai/overview
- xAI pricing and rate limits: https://docs.x.ai/developers/pricing and https://docs.x.ai/developers/rate-limits
- Google Gemini API getting started: https://ai.google.dev/gemini-api/docs/get-started
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Government of India DPDP Rules announcement: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190655
- CDSCO official website and applicable medical-device software guidance: https://cdsco.gov.in/
- FSSAI official website: https://fssai.gov.in/

**Final principle:** Populate and verify the database before serving answers; run crawling separately from live chat; preserve source-level facts rather than relying on site-wide summaries. Build a robust explanation, evidence, review and product-decision platform — not a black-box diagnosis or undisclosed sales funnel. Grok is the economical text/RAG assistant; Gemini handles image interpretation only when needed; traceable evidence and deterministic rules govern what the user may safely rely on.
