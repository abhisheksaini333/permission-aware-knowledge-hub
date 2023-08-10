# Architecture and authorization invariants

## Identity and access

Keycloak issues an RS256 access token with subject, tenant, audience, expiry, application roles and groups. The API accepts only the configured issuer/audience and its trusted signing-key endpoint. The browser uses authorization-code PKCE; access tokens remain in memory. The local realm disables password grants and implicit flow.

A document is visible only when the effective principal has an application role, belongs to its tenant, and either shares a document group or the document is company-wide. An administrator can manage its tenant's index metadata, but does not bypass group permission when reading source content or asking questions. Opaque document IDs reveal no authorization authority.

Membership overrides are authoritative for existing tokens. Retrieval filters before scoring and rechecks afterward. Answer generation rechecks access and document revisions after inference. Cache identity contains effective roles/groups and live chunk identities; a cache hit rechecks every returned citation. Citation reads require both current and historical revision permissions, and reject deleted documents.

These checks prevent an asynchronous model or previously populated cache from authorizing itself. The model never receives a forbidden document as deliberate context. The documented reference service is a single-process application; distributed authorization consistency requires a shared, transactionally managed policy service.

## Document lifecycle

Document identity is a hash of tenant and source name. Identical content/title/access uploads are idempotent. A changed upload creates an immutable revision and pending job. Pending/current-version checks hide superseded chunks immediately. Page extraction retains page-local and document-wide offsets.

Workers claim bounded leases. Publication checks owner, unique lease token, attempt, expiry and revision in the same transaction as chunk/vector replacement. Completion is also lease-fenced. After deletion a tombstone increments the revision and removes live chunks/vectors; old work cannot resurrect it. Failed/expired jobs have a three-attempt budget and bounded exponential backoff. An administrator can explicitly request a new indexing attempt.

Historical revision content remains in the database for audit/recovery; deletion means logical removal from the application, not secure erasure of every backup. The runbook describes retention and backup handling.

## Retrieval and answers

BM25 provides the low-cost baseline. MiniLM uses attention-mask-aware mean pooling and L2 normalization. PostgreSQL executes cosine ranking with tenant and group predicates; the portable SQLite reference uses the same domain contracts with in-process vector ranking. Fusion combines rank positions, and reranking uses query-term coverage/phrase evidence.

FLAN-T5 receives a bounded prompt built from authorized passages. Generation is deterministic and limited to 64 new tokens by default, with one concurrent model call and a two-second admission wait. A token-overlap support check removes unsupported outputs and citations. This is a conservative heuristic, not an entailment proof or a guarantee against prompt injection. Users must inspect citations for consequential decisions.

The selected application dependencies and model artifacts are explicit. The default local setup makes no hosted API calls for inference. Model downloading is a separate verified preparation step.

## Boundaries and resource assumptions

The reference storage adapter serializes writes with a PostgreSQL transaction advisory lock. This favors understandable correctness over high write throughput. Lexical retrieval scans the current tenant corpus; it is intended for bounded team document collections. Request body limits, document/page limits, model budgets and in-process rate limits bound ordinary use. Public internet deployment needs maintained dependency versions, TLS, centralized quotas, stronger upload isolation, and an operational identity/database configuration.
