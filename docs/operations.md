# Operator runbook

## Start and verify

Follow the root README to generate local credentials, fetch verified models and start Compose. `/health` confirms the process; `/ready` additionally probes storage and reports whether semantic retrieval and answers are configured. A healthy process alone does not establish functioning identity or model inference. Sign in through the browser, upload a source, wait for `ready`, ask a question and open its citation.

Keep `POSTGRES_PASSWORD`, `KEYCLOAK_ADMIN_PASSWORD` and `DEMO_PASSWORD` outside Git. `.runtime/realm.json` contains generated local credentials; its parent is owner-only. Exported Docker volumes, dumps and any backup containing revisions must be handled as private data. `.env.example` contains names and non-secret defaults only.

The local fixture realm is intentionally named `knowledge`. Removing/recreating an identity volume can generate new subject IDs. Membership overrides use subject IDs, so reconcile them after identity restoration rather than assuming usernames identify the same principal.

## Indexing and document changes

- Uploading the same source name and unchanged content/title/access is idempotent.
- Changed content or permissions creates a revision. Old chunks stop appearing while the current revision is pending.
- Index workers use 60-second leases and a three-attempt budget. Failure backoff is bounded; only the live lease owner can publish chunks/vectors or complete work.
- Inspect `/api/jobs` and `/api/index-health` as an administrator. Failure text is deliberately limited to error classes/codes, without document contents or tokens. Check the model cache, storage availability and supported upload format before using **Retry indexing**.
- Deleted documents become tombstones. Live chunks and vectors are removed; historical revisions stay in the database but are inaccessible through source-reading endpoints. Apply your own retention policy to revisions and backups if erasure is required.

A worker crash can be recovered by restarting the API and allowing the lease to expire. A crashed worker cannot overwrite a later owner's published vectors. Tests exercise both expiration/reclaim and independent PostgreSQL connections.

## Access changes

The administrator's **Manage account access** form takes the account ID shown in session details. An override replaces the account's effective groups and application roles immediately for future checks, including existing signed tokens and cache hits. Empty document groups mean company-wide access; an empty account role list removes access to the application entirely.

An administrator's management role does not grant permission to read every document. Source reads still enforce current and historical group restrictions. Use the `finance` group for the restricted fixture documents when testing allowed reads.

## Back up and restore

PostgreSQL:

```sh
# Restrict the output directory before creating the dump.
umask 077
mkdir -p backups
docker compose exec -T postgres pg_dump -U knowledge -d knowledge -Fc > backups/knowledge.dump
# Restore to a new database first, then verify before switching traffic.
docker compose exec postgres createdb -U knowledge knowledge_restore
docker compose exec -T postgres pg_restore -U knowledge -d knowledge_restore --no-owner < backups/knowledge.dump
```

Verify document/revision/chunk/vector counts, membership overrides, job state and an authorized source lookup before promotion. Never restore over the live database as the first step. The acceptance run restored an actual PostgreSQL dump into a separate database and matched all nine application table counts: documents, revisions, chunks, vectors, memberships, jobs, feedback, audit and cache.

For the SQLite reference, `knowledge.backup.backup_sqlite` uses the SQLite backup API under the store lock. `restore_sqlite` checks integrity and refuses an existing destination. Tests verify preserved revisions and membership state.

## Vector index maintenance

Exact search is the default. For an adequately sized corpus, an administrator can explicitly try IVFFlat:

```sh
python scripts/vector_index.py ivfflat
# Revert to exact search:
python scripts/vector_index.py exact
```

Back up first and use a maintenance window. The reference IVFFlat configuration uses ten lists; it is not a tuned recommendation for every corpus. Compare against exact retrieval using your labeled, permission-filtered queries before adopting an approximate index. Approximate nearest-neighbor indexes can reduce recall after tenant/group filtering. The application never relaxes authorization to fill a result page.

## Tested boundaries

Local evidence covers:

- Actual PostgreSQL/pgvector persistence, SQL-level ACL filtering, revision replacement, deletion, lease fencing and backup/restore.
- Six real Keycloak PKCE identities across three tenants and reader/admin roles; invalid signatures and forbidden source reads.
- Real browser file ingestion, actual MiniLM/FLAN inference, source-dialog keyboard handling, feedback and a mobile viewport.
- The same signed token before/after group and whole-account revocation, including a previously populated answer cache.
- Updating a document changes the generated answer and citation revision; deleting it denies old source access and removes its generated citations.
- Fixed-corpus comparisons with separate retrieval and answer metrics; see the evaluation report.

Limits: this is a bounded local reference application. It does not establish production multi-region availability, high-throughput ingestion, distributed rate limiting, enterprise identity administration, arbitrary PDF malware isolation or model accuracy on customer data. The packaged identity runs in development mode on loopback ports. Review and upgrade dependencies, deploy TLS, use managed secrets, harden identity/database privileges and isolate untrusted document processing before an internet-facing deployment. Native ARM inference and the x86 container are separate execution environments; their latency should not be conflated.
