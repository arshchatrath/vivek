param([switch]$IncludeMarkdown)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
if (-not $env:DATABASE_URL) { throw 'Set DATABASE_URL in this PowerShell session before refreshing.' }

python services/ingestion/catalog.py --limit 0 --delay 0.7
if ($LASTEXITCODE -ne 0) { throw 'Catalog crawl failed.' }
python services/ingestion/load_postgres.py
if ($LASTEXITCODE -ne 0) { throw 'Database load failed.' }
python services/ingestion/index_knowledge.py
if ($LASTEXITCODE -ne 0) { throw 'Knowledge index failed.' }
python services/ingestion/load_concern_guidance.py
if ($LASTEXITCODE -ne 0) { throw 'Concern guidance index failed.' }
if ($IncludeMarkdown) {
  python services/ingestion/crawl4ai_enrich.py --limit 0 --delay 0.7
  if ($LASTEXITCODE -ne 0) { throw 'Crawl4AI capture failed.' }
}
python services/ingestion/audit_concerns.py
if ($LASTEXITCODE -ne 0) { throw 'Catalog concern audit failed.' }
Push-Location apps/web
try {
  npm run build
  if ($LASTEXITCODE -ne 0) { throw 'Web build failed.' }
} finally { Pop-Location }
Write-Host 'Catalog refresh completed. Review data/artifacts/pending-changes.jsonl and database catalog_change_events.'
