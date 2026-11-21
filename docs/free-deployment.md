# Vivek Fellowship deployment

The Fellowship demo uses Render's free tier in Singapore. It is publicly accessible over HTTPS and requests `noindex,nofollow`. Share the URL only with the intended reviewers.

| Resource | Address or name |
| --- | --- |
| Static frontend | [vivek-fellowship.onrender.com](https://vivek-fellowship.onrender.com) |
| FastAPI service | [vivek-fellowship-api.onrender.com](https://vivek-fellowship-api.onrender.com) |
| PostgreSQL 17 and pgvector | `vivek-fellowship-db` |
| Redis-compatible Key Value | `vivek-fellowship-quota` |
| Private source repository | [arshchatrath/vivek](https://github.com/arshchatrath/vivek) |

The database expires **21 December 2026 at 18:25 IST**. Move or replace it before then if the demo needs to stay online. The API can take about one minute to wake up after 15 minutes of inactivity. [Render free-tier documentation](https://render.com/docs/free)

## Service settings

The static site builds from the repository root with `npm ci --prefix apps/web && npm run build --prefix apps/web` and serves `apps/web/out`. Set `NEXT_PUBLIC_API_URL` to the API origin at build time.

The API builds from the repository root with `pip install -r apps/api/requirements.txt`, then downloads the MiniLM embedding model into the build using `FASTEMBED_CACHE_PATH=.render-embeddings`. It starts with `uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port $PORT` and uses `/api/v1/health` as its health check.

- Set `API_CORS_ORIGIN` and `PUBLIC_BASE_URL` to the exact frontend origin. Set `DATABASE_URL` and `REDIS_URL` to the internal connection strings from Render. Keep both datastores closed to external traffic.
- Store `GROQ_API_KEY`, `GEMINI_API_KEY`, and `GNANI_API_KEY` in the API service's environment. Set `ENABLE_IMAGE_ANALYSIS=true` when label reading is enabled. Leave model overrides empty to use the application defaults.
- The optional `DAILY_TEXT_CALL_LIMIT`, `DAILY_VISION_CALL_LIMIT`, and `DAILY_SPEECH_CALL_LIMIT` control calls to the providers. If the API cannot reach Redis, these calls are unavailable and the catalog and saved guidance remain accessible.

## Initial data and updates

Run `services/ingestion/load_postgres.py`, `services/ingestion/index_knowledge.py`, and `services/ingestion/load_concern_guidance.py` in that order from a trusted connection to the target database. The Render deployment used a temporary API startup command to do this across the private network. The seed contains 323 catalog listings, 323 product embeddings, and 30 guidance passages.

Run `scripts/refresh-catalog.ps1` with a local database to refresh the source captures and rebuild the catalog. Review source changes and the newly captured fields before running the same three load and index scripts against the hosted database. The preview has no scheduled production crawl.

Check the [API health endpoint](https://vivek-fellowship-api.onrender.com/api/v1/health) and open the frontend. Use a sample concern to verify guidance and source links, search for a known product, and test optional voice and label reading with synthetic inputs.
