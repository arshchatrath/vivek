# Vivek

Vivek is a wellness guidance and product explorer for the Mosaic Fellowship. Type or dictate a concern to find published guidance, when to seek care, and product listings that name the relevant ingredient or product type. The catalog covers Man Matters, Be Bodywise, Little Joys, and Root Labs. Vivek also offers search, comparisons, product questions, and opt-in package-label reading.

## Repository layout

| Path | Purpose |
| --- | --- |
| `apps/web` | Next.js static site, concern form, catalog, and comparison |
| `apps/api` | FastAPI, retrieval, provider routes, and API tests |
| `data/seeds` | Canonical catalog and guidance snapshots shared by the API and static build |
| `services/ingestion` | Brand crawling, audit, and PostgreSQL indexing |
| `infra/schema.sql` and `compose.yaml` | Local PostgreSQL, pgvector, and Redis |

## What is populated

- 323 unique official product listings, with original URLs, capture dates, names, images, displayed prices, and source provenance.
- The catalog and comparison display rupees. The seven Root Labs listings from the US storefront use approximate rupee conversions from the 20 November 2026 FBIL reference rate. Listing details show the captured US price and link to the rate archive. Refresh the dated reference in `apps/web/src/app/vivek-app.tsx` when updating the conversion.
- PostgreSQL product and source tables, full-text indexes, and 323 local pgvector embeddings.
- Twelve concern guides and 30 source passages in a separate PostgreSQL retrieval index. Initial guidance is read locally. For an opt-in follow-up, Groq selects passages from the chosen topic and Vivek displays the stored guidance with its original links.
- A full catalog audit scanned all 323 listing names, categories, descriptions, and captured product details. It found terms for 29 topic groups across 299 listings. These are leads for review. Ingredient matches require a checked brand listing and the expected ingredient or product form.
- Crawl4AI Markdown page captures in `data/artifacts/` for review. This folder is ignored by Git; its text is not automatically treated as verified health evidence.
- Ingredients, warnings, and age guidance remain unknown where an official listing has not been reviewed field by field.

## Local setup on Windows

1. Install Python 3.13, Node 22+, and Docker Desktop. Start Docker Desktop.
2. From this folder, run `docker compose up -d db redis`.
3. Copy `.env.example` to `.env`. Keep `.env` local; it is ignored by Git. Set `DATABASE_URL` and `REDIS_URL` as shown for local Docker.
4. Install backend dependencies: `python -m pip install -r apps/api/requirements.txt -r services/ingestion/requirements.txt`.
5. Load the current source catalog and vector index:

   ```powershell
   $env:DATABASE_URL='postgresql://wellwise:wellwise@localhost:5432/wellwise'
   python services/ingestion/load_postgres.py
   python services/ingestion/index_knowledge.py
   python services/ingestion/load_concern_guidance.py
   ```

   The first vector-index run downloads a free local MiniLM model. No paid embedding service is needed.

6. The API reads `.env` automatically. Run `python -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000`.
7. In another PowerShell window, run `cd apps/web`, `npm install`, and `npm run dev`. Open `http://localhost:3000`.

Product search and comparison work from the static catalog. The concern guide also accepts typed input with no model key. The API returns source cards when Groq is unavailable and an unavailable state for unconfigured label or voice input.

## Free developer keys

- Create a Groq API key and set `GROQ_API_KEY`. Vivek uses `openai/gpt-oss-20b` for text by default. Set `GROQ_TEXT_MODEL` only to choose another model. [Groq Console](https://console.groq.com/) · [Model list](https://console.groq.com/docs/models)
- Create a Gemini API key and set `GEMINI_API_KEY`. Vivek uses `gemini-3.1-flash-lite` for label reading by default. Set `GEMINI_VISION_MODEL` only to choose another model. Set `ENABLE_IMAGE_ANALYSIS=true` to enable label reading. The upload endpoint sends cleaned images only after explicit user consent. [Google AI Studio](https://aistudio.google.com/app/apikey) · [Gemini pricing and data terms](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite)
- Set `GNANI_API_KEY` server-side for microphone input. The browser records up to 20 seconds on HTTPS or localhost and sends a WAV clip to the API. Gnani transcribes it in Indian English. The user can edit the text before submitting, and Vivek does not retain the recording. [Gnani REST transcription](https://docs.gnani.ai/api/STT/speech-to-text)
- **Never** put keys in `NEXT_PUBLIC_*`, commit them, or send them in chat. Configure them as server-side secrets in the host dashboard when deploying.

`REDIS_URL` enables daily provider caps. Defaults are 30 text calls, 3 label reads, and 20 short voice clips. Configure them with `DAILY_TEXT_CALL_LIMIT`, `DAILY_VISION_CALL_LIMIT`, and `DAILY_SPEECH_CALL_LIMIT`. The API pauses provider calls if Redis is unavailable.

## Refreshing product information

Run `scripts/refresh-catalog.ps1` from PowerShell with `DATABASE_URL` set. It checks robots rules, reads official product sitemaps and JSON-LD, stores source artifacts, updates PostgreSQL, rebuilds both retrieval indexes, scans for concern mentions, and exports a fresh frontend. Add `-IncludeMarkdown` to continue private Crawl4AI page captures. Review `data/artifacts/pending-changes.jsonl`, `data/artifacts/catalog-concern-audit.json`, and `catalog_change_events` after a refresh. Schedule the script with Windows Task Scheduler on a machine that can run Docker and reach the brand sites. A hosted scheduler can use the same commands with hosted database credentials.

## Deployment shape

`apps/web` builds a static export in `apps/web/out`, suitable for a free static host. `apps/api` needs a Python host plus PostgreSQL with pgvector and Redis. Set `NEXT_PUBLIC_API_URL` to the public API origin **before** building the web export, and set `API_CORS_ORIGIN` to the exact web origin. Use HTTPS and host-managed secrets. No hosted deployment is configured in this repository yet.

## Checks

```powershell
python -m pytest apps/api/tests -q
cd apps/web
npm run build
```

See [the free deployment guide](docs/free-deployment.md) for exact account setup, [PROGRESS.md](PROGRESS.md) for delivery state and open decisions, and [WELLWISE_MASTER_BUILD_SPEC.md](WELLWISE_MASTER_BUILD_SPEC.md) for the full long-term vision.
