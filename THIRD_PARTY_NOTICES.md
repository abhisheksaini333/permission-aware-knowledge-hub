# Third-party components

Application code is MIT licensed. Dependencies retain their own licenses; installation does not relicense them.

| Component | Use | Upstream license/source |
|---|---|---|
| FastAPI / React / LangChain / Keycloak / PostgreSQL / pgvector | API, browser, local chain adapter, identity and database | See each pinned upstream distribution; Keycloak uses Apache-2.0 and PostgreSQL/pgvector use the PostgreSQL license |
| google/flan-t5-small | Local answer generation | [Apache-2.0 model card](https://huggingface.co/google/flan-t5-small/tree/371f99f1df1429771f01227c93bd662f5eec2480) |
| sentence-transformers/all-MiniLM-L6-v2 | Dense sentence embeddings | [Apache-2.0 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/7dbbc90392e2f80f3d3c277d6e90027e55de9125) |

Model weights are not included in this repository. The downloader fetches original, revision-pinned files and verifies their SHA-256 digests. The synthetic documents and labels in `fixtures/corpus.json` are original project fixtures and contain no customer records.
