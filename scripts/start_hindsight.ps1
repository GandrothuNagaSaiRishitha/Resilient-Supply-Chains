# Starts the self-hosted Hindsight memory engine on Windows (bare-metal, embedded PostgreSQL).
# Usage: powershell -ExecutionPolicy Bypass -File scripts/start_hindsight.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$envText = Get-Content ".env" -Raw
$key = ([regex]::Match($envText, 'GROQ_API_KEY=(.+)')).Groups[1].Value.Trim()
if (-not $key) { throw "GROQ_API_KEY missing from .env" }

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:HINDSIGHT_API_LLM_PROVIDER = "groq"
$env:HINDSIGHT_API_LLM_MODEL = "openai/gpt-oss-120b"
$env:HINDSIGHT_API_LLM_API_KEY = $key
$env:HINDSIGHT_API_LLM_GROQ_SERVICE_TIER = "on_demand"
$env:HINDSIGHT_API_EMBEDDINGS_PROVIDER = "onnx"
$env:HINDSIGHT_API_RERANKER_PROVIDER = "flashrank"
$env:HINDSIGHT_API_LOG_LEVEL = "info"
$env:HINDSIGHT_API_DATABASE_URL = "pg0"
$env:HINDSIGHT_API_RETAIN_MAX_COMPLETION_TOKENS = "32000"
# Store curated business experiences as exact chunks. Retain is a memory write,
# not a generative summary task, so chunk mode avoids burning the free Groq token
# budget on fact-extraction calls and keeps every retained sentence exact.
$env:HINDSIGHT_API_RETAIN_EXTRACTION_MODE = "chunks"
# Observations/consolidation require a large consolidation prompt (~8k tokens)
# that exceeds the free Groq TPM budget even for a single fact. Reflect's agentic
# loop can answer from retained facts through its recall tool, so consolidation is
# disabled to keep the memory engine reliable on the free tier.
$env:HINDSIGHT_API_ENABLE_OBSERVATIONS = "false"
$env:HINDSIGHT_API_ENABLE_AUTO_CONSOLIDATION = "false"
# Free-tier Groq keys allow 8k tokens/minute per model. Reflect and consolidation use a
# separate, lighter model with fewer iterations so the whole loop fits the budget.
$env:HINDSIGHT_API_REFLECT_LLM_MODEL = "openai/gpt-oss-20b"
$env:HINDSIGHT_API_REFLECT_MAX_ITERATIONS = "2"
$env:HINDSIGHT_API_REFLECT_MAX_COMPLETION_TOKENS = "400"
$env:HINDSIGHT_API_REFLECT_MAX_CONTEXT_TOKENS = "900"
$env:HINDSIGHT_API_REFLECT_LLM_MAX_RETRIES = "3"
$env:HINDSIGHT_API_REFLECT_LLM_INITIAL_BACKOFF = "5"
$env:HINDSIGHT_API_REFLECT_LLM_MAX_BACKOFF = "30"
$env:HINDSIGHT_API_REFLECT_WALL_TIMEOUT = "180"
# Consolidation turns raw facts into observations. On an 8k TPM free key, one
# batch of 8 facts exceeds the per-minute budget (HTTP 413), so consolidate one
# fact at a time with a small source-fact budget. Slower, but it fits the quota.
$env:HINDSIGHT_API_CONSOLIDATION_LLM_MODEL = "openai/gpt-oss-20b"
$env:HINDSIGHT_API_CONSOLIDATION_LLM_BATCH_SIZE = "1"
$env:HINDSIGHT_API_CONSOLIDATION_LLM_PARALLELISM = "1"
$env:HINDSIGHT_API_CONSOLIDATION_LLM_MAX_RETRIES = "2"
$env:HINDSIGHT_API_CONSOLIDATION_LLM_INITIAL_BACKOFF = "5"
$env:HINDSIGHT_API_CONSOLIDATION_LLM_MAX_BACKOFF = "30"
$env:HINDSIGHT_API_CONSOLIDATION_MAX_ATTEMPTS = "2"
$env:HINDSIGHT_API_CONSOLIDATION_MAX_TOKENS = "256"
$env:HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS = "1500"
$env:HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS_PER_OBSERVATION = "200"
$env:HINDSIGHT_API_CONSOLIDATION_MAX_MEMORIES_PER_ROUND = "4"

New-Item -ItemType Directory -Force -Path "infra" | Out-Null
$existing = Get-Process hindsight-api -ErrorAction SilentlyContinue
if ($existing) {
  "Hindsight already running (PID $($existing.Id -join ', ')); leaving it untouched."
  exit 0
}

Start-Process -FilePath "backend\.venv\Scripts\hindsight-api.exe" `
  -ArgumentList "--host", "127.0.0.1", "--port", "8888" `
  -RedirectStandardOutput "infra\hindsight.out.log" `
  -RedirectStandardError "infra\hindsight.err.log" `
  -WindowStyle Hidden

Start-Sleep -Seconds 12
$conn = Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue
if ($conn) { "Hindsight listening on http://127.0.0.1:8888" } else { "Hindsight still starting; see infra/hindsight.out.log" }



