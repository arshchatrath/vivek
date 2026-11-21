# Vivek

Vivek helps people turn a wellness question into guidance they can check. Ask in plain language, open the original health sources, and compare products whose brand listings name a relevant ingredient or product type. Built for the Mosaic Fellowship.

[Live demo](https://vivek-fellowship.onrender.com) · [Open chat](https://vivek-fellowship.onrender.com/chat) · [Browse the catalog](https://vivek-fellowship.onrender.com/#catalog)

## Try it

1. Open [Vivek Chat](https://vivek-fellowship.onrender.com/chat). Type **“My scalp is itchy and has white flakes.”** or use the microphone and review the transcript.
2. Send the question. Open a source link such as **NHS**, then see which ingredients or product types appear on the official listings.
3. Ask **“When should I see a doctor about dandruff?”** in the same thread. The **ⓘ** icon next to **Ask with Groq** explains what the follow-up shares.
4. In the [catalog](https://vivek-fellowship.onrender.com/#catalog), filter by brand and select two to four products to compare. Open any product to see its capture date and original listing. **Read a label** lets you upload a packaging photo and review the visible ingredients and warnings.

![Vivek Chat showing a sample question, sourced scalp guidance, and links to original publishers](docs/images/concern-chat.png)

## What the demo covers

The catalog contains **323 official listings**. The concern library contains **12 topics** and **30 source passages**. Each catalog record stores its original URL, capture date, displayed price, and field-level source details.

| Brand | Listings |
| --- | ---: |
| Man Matters | 81 |
| Be Bodywise | 104 |
| Little Joys | 131 |
| Root Labs | 7 |

Catalog and comparison prices display in rupees. The seven US Root Labs listings use an estimate based on the 20 November 2026 FBIL reference rate. Product details show the captured USD price alongside the estimate.

Vivek is for educational guidance. For diagnosis or treatment, speak with a qualified clinician. Product details link to the brand listing, and label reads show what was visible in the uploaded photo. Ingredients, warnings, and age guidance stay marked as unverified where field-level review is pending. Chat history clears on refresh.

## How it works

The Next.js catalog reads a checked-in snapshot. For concern questions, FastAPI checks for care signals, recognizes common misspellings, and looks for a known topic. For unfamiliar wording, it combines local MiniLM embeddings and PostgreSQL word matches across the 12 guides. A clear match returns saved passages with source links. Competing matches prompt a question before any product examples appear.

```mermaid
flowchart LR
    Brands["Official brand sites"] --> Ingest["Sitemaps, product metadata, and optional Crawl4AI capture"]
    Ingest --> Catalog["Versioned catalog snapshot"]
    Catalog --> Web["Next.js chat and catalog"]
    Catalog --> DB["PostgreSQL + pgvector"]
    Guidance["Sourced concern summaries"] --> DB
    Web --> API["FastAPI"]
    API --> DB
    API --> Redis["Redis quotas"]
    API --> Providers["Groq text · Gemini labels · Gnani voice"]
```

Initial concern answers use zero Groq credits. Groq selects relevant excerpts for opt-in follow-ups within the same topic. For product questions, the API retrieves listing facts with full-text search and pgvector embeddings, then Groq writes a cited answer. Gnani transcribes clips of up to 20 seconds. After you consent to label reading, the API strips photo metadata and sends the image to Gemini.

## Run locally on Windows

Install **Python 3.13**, **Node.js 22 or later**, and **Docker Desktop**. Start Docker Desktop, then run the following from the repo root in PowerShell.

```powershell
docker compose up -d --wait db redis
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps/api/requirements.txt
npm ci --prefix apps/web
```

Seed the local PostgreSQL database and start the API. The first indexing run downloads the MiniLM embedding model. The concern loader builds searchable topic profiles and the source passage index.

```powershell
$env:DATABASE_URL = 'postgresql://wellwise:wellwise@127.0.0.1:5432/wellwise'
.\.venv\Scripts\python.exe services/ingestion/load_postgres.py
.\.venv\Scripts\python.exe services/ingestion/index_knowledge.py
.\.venv\Scripts\python.exe services/ingestion/load_concern_guidance.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app `
  --app-dir apps/api --host 127.0.0.1 --port 8000
```

In a second PowerShell window at the repo root, start the frontend and open [localhost:3000](http://localhost:3000). The local [API health endpoint](http://localhost:8000/api/v1/health) should report `"catalog_products": 323`.

```powershell
npm run dev --prefix apps/web
```

### Add optional provider keys

The catalog, comparisons, and typed concern guidance work without provider keys. Add the keys you need to the Git-ignored `.env` and restart the API. Use the host’s secret store in production and reserve `NEXT_PUBLIC_*` for browser-visible settings.

| Feature | Server environment | Where to get access |
| --- | --- | --- |
| Product questions and follow-ups | `GROQ_API_KEY`. Defaults to `openai/gpt-oss-20b`. Override with `GROQ_TEXT_MODEL`. | [Groq Console](https://console.groq.com/) |
| Package-label reading | `GEMINI_API_KEY` and `ENABLE_IMAGE_ANALYSIS=true`. Defaults to `gemini-3.1-flash-lite`. Override with `GEMINI_VISION_MODEL`. | [Gemini API key setup](https://ai.google.dev/gemini-api/docs/api-key) |
| Microphone input | `GNANI_API_KEY`. Transcribes in Indian English on HTTPS or localhost. | [Gnani setup](https://docs.gnani.ai/api/STT/speech-to-text) |

Redis enforces daily caps of **30 Groq calls**, **3 label reads**, and **20 voice clips** by default. Set the limits in [`.env.example`](.env.example). If Redis is unavailable, the API pauses provider calls and continues serving the catalog and stored guidance.

## Refresh the catalog

From PowerShell with your Python environment active, install the [ingestion dependencies](services/ingestion/requirements.txt) and point `DATABASE_URL` at your local development database. Run the [refresh script](scripts/refresh-catalog.ps1) to crawl brand sites, update the catalog and indexes, and build a new frontend export.

```powershell
python -m pip install -r services/ingestion/requirements.txt
$env:DATABASE_URL = 'postgresql://wellwise:wellwise@127.0.0.1:5432/wellwise'
.\scripts\refresh-catalog.ps1
```

Add `-IncludeMarkdown` to capture pages with Crawl4AI. Review the private reports in `data/artifacts/` and the `catalog_change_events` table before publishing updates. The live preview uses manual refreshes.

## Test and deploy

Run the API tests, lint the web app, and build the static site from the repo root.

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests -q
npm run lint --prefix apps/web
npm run build --prefix apps/web
```

Render serves the static export from `apps/web/out` and runs FastAPI separately. Set `NEXT_PUBLIC_API_URL` before building the frontend. Set `API_CORS_ORIGIN` to the exact frontend origin on the API.

The preview uses Render’s free tier. The API can take about a minute to wake after inactivity. The current database expires **21 December 2026 at 18:25 IST**. See the [deployment guide](docs/free-deployment.md) and [Render’s free-tier limits](https://render.com/docs/free).

## Find the code

| Path | What to find there |
| --- | --- |
| [`apps/web`](apps/web) | Chat, catalog, comparison, and label reader |
| [`apps/api`](apps/api) | FastAPI routes, retrieval, provider integrations, and tests |
| [`data/seeds`](data/seeds) | Catalog and concern snapshots |
| [`services/ingestion`](services/ingestion) | Brand crawlers, catalog audit, and index loaders |
| [`infra/schema.sql`](infra/schema.sql) and [`compose.yaml`](compose.yaml) | Database schema and local services |

[Progress and open work](PROGRESS.md) · [Full WellWise specification](WELLWISE_MASTER_BUILD_SPEC.md)
