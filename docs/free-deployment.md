# Free-tier deployment plan

Recommended first public demo stack: **Cloudflare Pages** for the static web export, **Render Free web service** for FastAPI, **Supabase Free Postgres** with the vector extension, and **Upstash Free Redis** for provider-call caps. These services currently list free tiers, but quotas and acceptable-use terms can change. Render's free web service sleeps after 15 minutes idle, and Supabase Free projects pause after a week of inactivity. That is acceptable for a Fellowship preview, but the first assistant request may be slow. Avoid Render Free Postgres for this catalog because its free database expires after 30 days.

Official references: [Cloudflare static Next.js](https://developers.cloudflare.com/pages/framework-guides/nextjs/deploy-a-static-nextjs-site/), [Render Free](https://render.com/docs/free), [Supabase Free](https://supabase.com/pricing), [Supabase vector extension](https://supabase.com/docs/guides/ai/vector-columns), [Upstash Free](https://upstash.com/pricing/redis), [Upstash with Render](https://upstash.com/docs/redis/quickstarts/render).

## Account setup

1. Create a private GitHub repository for this workspace. Keep `.env`, `data/artifacts/`, `apps/web/out/`, and `shots/` out of Git as configured in `.gitignore`.
2. Create a Supabase Free project. In **Database → Extensions**, enable `vector` and `pg_trgm`. In **Connect**, copy the direct Postgres connection string and keep it in a password manager. Set it as `DATABASE_URL` only in the local environment and Render secrets. Run `python services/ingestion/load_postgres.py`, `python services/ingestion/index_knowledge.py`, and `python services/ingestion/load_concern_guidance.py` locally against that database. The initial catalog and product index should have 323 records each. The separate `concern_passages` table should have 30.
3. Create an Upstash Free Redis database in a region near the API. In its connection tab, copy the **TLS/TCP** `rediss://` connection string, not the REST URL. Set it as `REDIS_URL` in Render. The API refuses paid-provider calls if quota storage is unavailable.
4. Create a Render Free **Web Service** connected to the private repository. Use the repository root and build with `pip install -r apps/api/requirements.txt`. Start with `uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port $PORT`. Set `DATABASE_URL`, `REDIS_URL`, `API_CORS_ORIGIN`, and `GROQ_API_KEY` in the service environment. Set `GEMINI_API_KEY` and `ENABLE_IMAGE_ANALYSIS=true` if enabling label reading. Set `GNANI_API_KEY` if enabling microphone input. Keep the daily call limits within your account quotas and use `/api/v1/health` as the health check.
5. Create a Cloudflare Pages site connected to the same repository. Root directory: `apps/web`; build command: `npm run build`; output directory: `out`. Set `NEXT_PUBLIC_API_URL` to the exact HTTPS Render origin before building. Once Cloudflare gives the Pages origin, set that exact value as Render's `API_CORS_ORIGIN` and redeploy the API.
6. Open the Pages URL on desktop and mobile. Verify catalog images, search, comparison, the source-only fallback, and `/api/v1/health`. Then add keys one at a time and test one Groq request and one consented Gemini label scan. Watch the provider dashboards and Redis counters.

The Pages site requests `noindex,nofollow` because the user intends to share its public link with officials. This does not provide access control; anyone with the URL can open it. Add authentication before storing personal health information or private user material.

## Updates

Run `scripts/refresh-catalog.ps1` locally with the hosted `DATABASE_URL` set when the catalog needs refreshing, review observed changes, and push the resulting seed/build source to the repository. Cloudflare will rebuild the static catalog. Avoid placing crawlers on the sleeping API service.
