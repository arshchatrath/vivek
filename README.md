# Vivek

Vivek helps people find published wellness guidance, check its sources, and explore official product listings across Man Matters, Be Bodywise, Little Joys, and Root Labs. Built for the Mosaic Fellowship.

[Live demo](https://vivek-fellowship.onrender.com) · [Sourced chat](https://vivek-fellowship.onrender.com/chat) · [Product catalog](https://vivek-fellowship.onrender.com/#catalog)

## Try it

- **Sourced chat** at `/chat`. Ask “My scalp is itchy and has white flakes.” Open the NHS or American Academy of Dermatology source cards before exploring related listings. Optional Groq routing and follow-ups explain what they share.
- **General chat** at `/chat/general`. Ask “What does salicylic acid do?” or “What is the serving size of Biotin Hair Gummies (30N)?” **Send to Groq** shares the submitted question and up to four recent messages. Replies can include related official listings, ingredient notes, and captured ingredient or nutrition details.
- **Product catalog** on the homepage. Filter by brand, compare two to four listings, or open a source link to check current details. **Read a label** reads English text from a package photo on the device. An optional checkbox sends the image to Gemini for a summary.

![Vivek Chat showing a sample question, sourced scalp guidance, and links to original publishers](docs/images/concern-chat.png)

## Coverage

| Data | Count |
| --- | ---: |
| Official listings | 323 |
| Listings with extracted ingredient disclosures | 62 |
| Ingredient background notes | 63 |
| Listings with selected nutrition observations | 3 |
| Guided health topics | 12 |
| Reviewed source passages | 30 |

The catalog stores each listing’s source URL, capture date, displayed price, and field-level provenance. General chat shows ingredient and nutrition observations from the corresponding product captures where available. The catalog and comparison still mark unreviewed fields as unknown. For diagnosis or treatment, speak with a qualified healthcare professional.

## How it works

The homepage and catalog read a checked-in snapshot. FastAPI routes urgent and clinician-first questions locally. The sourced chat uses 12 stored guides and, when configured, local MiniLM embeddings and PostgreSQL word matches to help choose a guide.

General chat uses retrieval-augmented generation (RAG). It finds related listings by title, category, and disclosed ingredient. With PostgreSQL configured, it uses the existing product passage index to rank eligible results. It attaches any matching ingredient disclosures and nutrition observations before sending the requested context to Groq.

```mermaid
flowchart LR
    Question["Question"] --> Safety["Local safety checks"]
    Safety --> Guides["Sourced guides"]
    Safety --> Consent["General chat with opt-in"]
    Catalog["Official product listings"] --> Search["Product retrieval"]
    Index["PostgreSQL product passages and embeddings"] --> Search
    Consent --> Search
    Search --> Context["Listing facts and ingredient notes"]
    Captures["Ingredient disclosures and nutrition observations"] --> Context
    Context --> Groq["Groq"]
```

## Run locally on Windows

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up -d
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps/api/requirements.txt
npm ci --prefix apps/web
```

Seed PostgreSQL and start FastAPI. The first indexing run downloads the MiniLM embedding model.

```powershell
$env:DATABASE_URL = 'postgresql://wellwise:wellwise@127.0.0.1:5432/wellwise'
.\.venv\Scripts\python.exe services/ingestion/load_postgres.py
.\.venv\Scripts\python.exe services/ingestion/index_knowledge.py
.\.venv\Scripts\python.exe services/ingestion/load_concern_guidance.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

Start the web app in another terminal and open [localhost:3000](http://localhost:3000).

```powershell
npm run dev --prefix apps/web
```

### Providers

The catalog and sourced guidance run without provider keys. Place optional keys in the Git-ignored `.env` and restart the API. Redis enforces the daily quotas in [`.env.example`](.env.example).

| Feature | Server environment |
| --- | --- |
| General chat, product questions, guided chat routing and follow-ups | `GROQ_API_KEY`, optional `GROQ_TEXT_MODEL` |
| Package-label reading | `GEMINI_API_KEY` and `ENABLE_IMAGE_ANALYSIS=true`, optional `GEMINI_VISION_MODEL` |
| Microphone input | `GNANI_API_KEY` |

## Refresh and verify

Run [`scripts/refresh-catalog.ps1`](scripts/refresh-catalog.ps1) with a local database and the [ingestion dependencies](services/ingestion/requirements.txt) installed. Add `-IncludeMarkdown` to capture pages with Crawl4AI. Regenerate ingredient disclosures from the captures with `python services/ingestion/extract_ingredients.py` and review the resulting seed before publishing updates.

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests services/ingestion/tests -q
npm run lint --prefix apps/web
npm run build --prefix apps/web
```

[Deployment guide](docs/free-deployment.md)
