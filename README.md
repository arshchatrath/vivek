# Vivek

Vivek is my Mosaic Wellness Fellowship project. I started with Be Bodywise to explore how shoppers make sense of ingredients and product claims. Vivek helps them check published wellness guidance, read package labels, and compare official listings from Be Bodywise, Man Matters, Little Joys, and Root Labs.

[Open the live demo](https://vivek-fellowship.onrender.com/)

## Try the live demo

- **Check a source.** Ask “My scalp is itchy and has white flakes.” The reply pairs related product listings with guidance that links to the NHS and the American Academy of Dermatology. [Sourced Chat](https://vivek-fellowship.onrender.com/chat)
- **Ask about a product.** Try “What is the serving size of Biotin Hair Gummies (30N)?” Select **Send to Groq** to share the question and up to four recent messages. [General Chat](https://vivek-fellowship.onrender.com/chat/general)
- **Compare listings.** Filter by Be Bodywise and select two to four products. Open the original listings to check current details and look for fields marked **Not yet verified**. [Product catalog](https://vivek-fellowship.onrender.com/#catalog)
- **Read a label.** Upload a package photo to extract English text on your device. You can also choose to send the image to Gemini for a summary. [Label reader](https://vivek-fellowship.onrender.com/#label)

The hosted API may take a moment to wake when you send the first question.

![Sourced Chat response about an itchy scalp, with related product listings and links to NHS and American Academy of Dermatology guidance](docs/images/concern-chat.png)

## What the data covers

| Data | Count |
| --- | ---: |
| Official listings | 323 |
| Listings with extracted ingredient disclosures | 62 |
| Ingredient background notes | 63 |
| Listings with selected nutrition observations | 3 |
| Guided health topics | 12 |
| Reviewed source passages | 30 |

The catalog records each listing’s source URL, capture date, displayed price, and where individual fields came from. Open the brand’s listing for current prices, ingredients, and warnings. For diagnosis or treatment, speak with a qualified healthcare professional.

## How Vivek works

The Next.js frontend displays a catalog snapshot stored in this repository. The FastAPI backend checks for questions that need urgent or clinician-first guidance before calling a model provider. Sourced Chat matches a question to stored guides and can use local MiniLM embeddings and PostgreSQL keyword matches to pick a guide.

General Chat uses retrieval-augmented generation (RAG). It retrieves related listings by title, category, and disclosed ingredient, then sends relevant listing facts, ingredient notes, and captured nutrition details to Groq to generate a reply. When PostgreSQL is available, it uses the product passage index to rank eligible results.

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

Install Node.js 20.9 or later, Python 3.13, and Docker Compose. Run these commands from the repository root.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --wait
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

Start the web app in another terminal. Once it starts, open [localhost:3000](http://localhost:3000).

```powershell
npm run dev --prefix apps/web
```

### Providers

The catalog and sourced guidance run without provider keys. Place optional keys in the Git-ignored `.env` and restart the API. Redis enforces the daily quotas in [`.env.example`](.env.example).

| Feature | Server environment |
| --- | --- |
| General chat, product questions, guided chat routing and follow-ups | `GROQ_API_KEY`, optional `GROQ_TEXT_MODEL` |
| Optional package-label summary | `GEMINI_API_KEY` and `ENABLE_IMAGE_ANALYSIS=true`, optional `GEMINI_VISION_MODEL` |
| Microphone input | `GNANI_API_KEY` |

## Refresh the data and run checks

Run [`scripts/refresh-catalog.ps1`](scripts/refresh-catalog.ps1) with a local database and the [ingestion dependencies](services/ingestion/requirements.txt) installed. Add `-IncludeMarkdown` to capture pages with Crawl4AI. Regenerate ingredient disclosures from the captures with `python services/ingestion/extract_ingredients.py` and review the resulting seed before publishing updates.

Run these checks after setting up and seeding the local database.

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests services/ingestion/tests -q
npm run lint --prefix apps/web
npm run build --prefix apps/web
```

[Render deployment guide](docs/free-deployment.md)
