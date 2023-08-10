# Permission-aware Knowledge Hub

A company knowledge desk that answers questions from the documents a signed-in user can read. Every supported answer links to its source revision, page and text offsets. Administrators can upload, update, reindex and remove documents, and revoke account access without waiting for an existing access token to expire.

## What works

- Markdown, UTF-8 text and searchable PDF ingestion with content identity, immutable revisions and page-aware chunks.
- Three-tenant demonstration with reader/admin identities, real Keycloak authorization-code PKCE, RS256 access-token validation and group-level document permissions.
- Keyword, MiniLM semantic, reciprocal-rank fusion and relevance-reranked retrieval; PostgreSQL/pgvector stores vectors and applies tenant/group filtering in SQL.
- Local FLAN-T5 answers through a pinned LangChain adapter, conservative abstention and passage-level source links. Models are downloaded from immutable revisions with SHA-256 checks.
- Permission- and revision-aware answer caching, immediate account overrides, administrator ingestion/status controls, feedback and audit records.
- Durable indexing leases, bounded retries, stale-worker fencing and document deletion that removes live search/vector results.

The measured small corpus does not establish general enterprise accuracy. See [evaluation results](docs/evaluation.md) and [tested boundaries](docs/operations.md#tested-boundaries).

## Run locally

Prerequisites: Python 3.10, Node 18, Docker and about 2 GB available memory for the local identity/database services, plus model/runtime memory. On Apple Silicon the packaged API and Keycloak run through x86 emulation; native Python is faster for model experiments.

```sh
python3.10 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm ci --prefix frontend

export MODEL_CACHE="$HOME/.cache/knowledge-hub-models"
python scripts/fetch_models.py "$MODEL_CACHE"
export POSTGRES_PASSWORD="$(openssl rand -hex 24)"
export KEYCLOAK_ADMIN_PASSWORD="$(openssl rand -hex 24)"
export DEMO_PASSWORD="$(openssl rand -hex 16)"
python scripts/create_demo_realm.py

docker compose up -d --build
# Wait for http://localhost:8083/ready and the Keycloak sign-in page.
docker compose exec api python -m knowledge seed fixtures/corpus.json
```

Open **http://localhost:8083**. Sign in as `acme-admin` or `acme-reader` using the `DEMO_PASSWORD` you generated. The other tenant accounts are `beta-admin`, `beta-reader`, `cobalt-admin`, and `cobalt-reader`. These are local demonstration identities. Store your environment values privately if you intend to restart the stack later. Credentials, databases and weights are excluded from Git.

The first model download is about 380 MB. On Linux, a native CPU-only install can preinstall `torch==1.13.1+cpu` from `https://download.pytorch.org/whl/cpu` before installing the requirements; the container already does this.

For native development, start only `postgres` and `keycloak` with Compose, then:

```sh
export DATABASE_URL="postgresql://knowledge:${POSTGRES_PASSWORD}@localhost:54383/knowledge"
python -m knowledge seed fixtures/corpus.json
python -m knowledge serve
# In another terminal:
npm run dev --prefix frontend
```

The browser development URL is **http://localhost:5183**. Both browser origins are registered in the local realm.

## Verify

```sh
python -m pytest tests -q
npm test --prefix frontend
npm run build --prefix frontend

# Real database checks (use an expendable database owner account):
export KNOWLEDGE_TEST_DATABASE="$DATABASE_URL"
python -m pytest tests/integration -q

# Actual model comparison:
python scripts/evaluate.py --model-cache "$MODEL_CACHE"

# Real browser + identity + model lifecycle checks against the running demo:
export KNOWLEDGE_DEMO_PASSWORD="$DEMO_PASSWORD"
export KNOWLEDGE_WEB_URL=http://localhost:8083
npx --prefix frontend playwright install chromium
node scripts/browser_acceptance.cjs
```

Set `CHROME_BIN` to an installed Chrome executable if using that browser instead of the Playwright download. The browser test exercises all six identities, cached-answer revocation, upload/update/delete, source reading, feedback and a mobile viewport. Its generated documents are project-owned test fixtures.

GitHub Actions runs backend tests against actual PostgreSQL/pgvector, browser contracts and the production browser build. Full model and identity evidence is obtained with the explicit runtime commands above.

## How it fits together

```mermaid
flowchart LR
  User[Signed-in browser] --> API[FastAPI + current access policy]
  IdP[Keycloak PKCE / RS256] --> API
  API --> Search[Authorized lexical / vector retrieval]
  Search --> DB[(PostgreSQL + pgvector)]
  Search --> Model[Local FLAN-T5 + grounding check]
  Model --> Cite[Rechecked source revisions]
  Cite --> User
  Admin[Administrator upload] --> Queue[Durable indexing lease]
  Queue --> Encoder[Page chunks + MiniLM]
  Encoder --> DB
```

See the [architecture](docs/architecture.md), [operator runbook](docs/operations.md), [evaluation](docs/evaluation.md), and [third-party notices](THIRD_PARTY_NOTICES.md).
