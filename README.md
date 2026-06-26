# Buguard Asset Management — Track B (AI Applications)

LangChain-powered Attack Surface Management API built with FastAPI + PostgreSQL.

## Quick Start

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd buguard-asset-management

# 2. Setup environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Run everything
docker-compose up --build
```

API is live at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://buguard:buguard_pass@localhost:5432/asset_db` |
| `LLM_PROVIDER` | `anthropic` or `openai` | `anthropic` |
| `ANTHROPIC_API_KEY` | Anthropic API key | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `API_SECRET_KEY` | Secret key for the API | `changeme` |

---

## API Endpoints

### Assets
| Method | Endpoint | Description |
|---|---|---|
| POST | `/assets/import` | Bulk import assets with deduplication |
| GET | `/assets/` | List all assets (with filtering & pagination) |
| GET | `/assets/{id}` | Get single asset by UUID or external_id |

### AI Analysis
| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze/query` | Natural language asset search |
| POST | `/analyze/risk/{asset_id}` | Risk score for a single asset |
| POST | `/analyze/risk-all` | Risk score for all assets |
| POST | `/analyze/report` | Generate full security report |

---

## Seed the Database

```bash
curl -X POST http://localhost:8000/assets/import \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"id": "a1", "type": "domain", "value": "example.com", "tags": ["prod"]},
      {"id": "a2", "type": "subdomain", "value": "api.example.com", "tags": ["prod"]},
      {"id": "a10", "type": "certificate", "value": "prod.example.com"},
      {"id": "a11", "type": "subdomain", "value": "dev.api.example.com"},
      {"id": "a12", "type": "domain", "value": "www.buguard.io"}
    ]
  }'
```

---

## Example Prompts & Outputs

### Natural Language Query
**Request:**
```json
POST /analyze/query
{ "query": "show me all active domains" }
```
**Output:**
```json
{
  "query": "show me all active domains",
  "filters_used": { "type": "domain", "status": "active" },
  "total": 2,
  "results": [...]
}
```

### Risk Assessment
**Request:**
```bash
POST /analyze/risk/a10
```
**Output:**
```json
{
  "value": "prod.example.com",
  "risk_score": "high",
  "risk_summary": "This certificate requires immediate attention. Certificates must be monitored for expiry to prevent service disruption."
}
```

### Full Report
**Request:**
```bash
POST /analyze/report
```
**Output:**
```
ATTACK SURFACE MANAGEMENT REPORT
==================================
EXECUTIVE SUMMARY
4 of 5 assets are high risk...

HIGH RISK ASSETS
* prod.example.com [certificate] → ...
* example.com [domain] → ...
```

---

## Design Decisions & Assumptions

- **Mock LangChain layer**: Since OpenAI quota was limited, a rule-based mock was implemented for enrichment, risk scoring, and report generation. The `get_llm()` function is ready to swap in any LangChain-supported LLM.
- **Deduplication**: Assets are matched first by `external_id`, then by `type + value`. Re-importing updates `last_seen` and merges tags/metadata.
- **Enrichment on import**: Every new asset is automatically classified (environment, criticality, category) right after being saved.
- **No auth implemented**: Authentication was out of scope for Track B. The `API_SECRET_KEY` env var is reserved for future use.
- **Asset types**: domain, subdomain, ip_address, service, certificate, technology.

---

## Project Structure

```
app/
├── core/config.py          # Settings from environment variables
├── db/database.py          # Async PostgreSQL connection
├── models/asset.py         # SQLAlchemy models (tables)
├── schemas/asset.py        # Pydantic schemas (validation)
├── services/
│   ├── asset_service.py    # Bulk import + dedup logic
│   └── query_service.py    # NL query → DB query
├── langchain_layer/
│   ├── query_engine.py     # NL → filters (LangChain)
│   ├── enrichment.py       # Auto-classify assets
│   ├── risk_scorer.py      # Risk assessment
│   └── report_generator.py # Report generation
└── api/routes/
    ├── assets.py           # Asset endpoints
    └── analysis.py         # AI analysis endpoints
```

---

## What I Would Do Next

- Add JWT authentication on write operations
- Implement relationship endpoints (asset graph)
- Add automated tests (pytest)
- Connect real LangChain agents with tool-use
- Add caching for LLM responses
- CI pipeline with GitHub Actions# Buguard Asset Management — Track B (AI Applications)

LangChain-powered Attack Surface Management API built with FastAPI + PostgreSQL.

## Quick Start

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd buguard-asset-management

# 2. Setup environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Run everything
docker-compose up --build
```

API is live at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://buguard:buguard_pass@localhost:5432/asset_db` |
| `LLM_PROVIDER` | `anthropic` or `openai` | `anthropic` |
| `ANTHROPIC_API_KEY` | Anthropic API key | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `API_SECRET_KEY` | Secret key for the API | `changeme` |

---

## API Endpoints

### Assets
| Method | Endpoint | Description |
|---|---|---|
| POST | `/assets/import` | Bulk import assets with deduplication |
| GET | `/assets/` | List all assets (with filtering & pagination) |
| GET | `/assets/{id}` | Get single asset by UUID or external_id |

### AI Analysis
| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze/query` | Natural language asset search |
| POST | `/analyze/risk/{asset_id}` | Risk score for a single asset |
| POST | `/analyze/risk-all` | Risk score for all assets |
| POST | `/analyze/report` | Generate full security report |

---

## Seed the Database

```bash
curl -X POST http://localhost:8000/assets/import \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"id": "a1", "type": "domain", "value": "example.com", "tags": ["prod"]},
      {"id": "a2", "type": "subdomain", "value": "api.example.com", "tags": ["prod"]},
      {"id": "a10", "type": "certificate", "value": "prod.example.com"},
      {"id": "a11", "type": "subdomain", "value": "dev.api.example.com"},
      {"id": "a12", "type": "domain", "value": "www.buguard.io"}
    ]
  }'
```

---

## Example Prompts & Outputs

### Natural Language Query
**Request:**
```json
POST /analyze/query
{ "query": "show me all active domains" }
```
**Output:**
```json
{
  "query": "show me all active domains",
  "filters_used": { "type": "domain", "status": "active" },
  "total": 2,
  "results": [...]
}
```

### Risk Assessment
**Request:**
```bash
POST /analyze/risk/a10
```
**Output:**
```json
{
  "value": "prod.example.com",
  "risk_score": "high",
  "risk_summary": "This certificate requires immediate attention. Certificates must be monitored for expiry to prevent service disruption."
}
```

### Full Report
**Request:**
```bash
POST /analyze/report
```
**Output:**
```
ATTACK SURFACE MANAGEMENT REPORT
==================================
EXECUTIVE SUMMARY
4 of 5 assets are high risk...

HIGH RISK ASSETS
* prod.example.com [certificate] → ...
* example.com [domain] → ...
```

---

## Design Decisions & Assumptions

- **Mock LangChain layer**: Since OpenAI quota was limited, a rule-based mock was implemented for enrichment, risk scoring, and report generation. The `get_llm()` function is ready to swap in any LangChain-supported LLM.
- **Deduplication**: Assets are matched first by `external_id`, then by `type + value`. Re-importing updates `last_seen` and merges tags/metadata.
- **Enrichment on import**: Every new asset is automatically classified (environment, criticality, category) right after being saved.
- **No auth implemented**: Authentication was out of scope for Track B. The `API_SECRET_KEY` env var is reserved for future use.
- **Asset types**: domain, subdomain, ip_address, service, certificate, technology.

---

## Project Structure

```
app/
├── core/config.py          # Settings from environment variables
├── db/database.py          # Async PostgreSQL connection
├── models/asset.py         # SQLAlchemy models (tables)
├── schemas/asset.py        # Pydantic schemas (validation)
├── services/
│   ├── asset_service.py    # Bulk import + dedup logic
│   └── query_service.py    # NL query → DB query
├── langchain_layer/
│   ├── query_engine.py     # NL → filters (LangChain)
│   ├── enrichment.py       # Auto-classify assets
│   ├── risk_scorer.py      # Risk assessment
│   └── report_generator.py # Report generation
└── api/routes/
    ├── assets.py           # Asset endpoints
    └── analysis.py         # AI analysis endpoints
```
