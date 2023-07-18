import argparse, json, os
from .database import open_store
from .settings import Settings


def seed(store, documents):
    changed = 0
    for d in documents:
        from .content import document_key

        old = store.document(document_key(d["tenant"], d["source"]))
        new = store.ingest(
            d["tenant"], d["source"], d["title"], d["content"], d.get("groups", [])
        )
        changed += not old or new["revision"] != old["revision"]
    return changed


def main():
    parser = argparse.ArgumentParser(description="Knowledge Hub service and ingestion")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8083)
    load = sub.add_parser("seed")
    load.add_argument("corpus")
    args = parser.parse_args()
    if args.command == "serve":
        import uvicorn

        uvicorn.run(
            "knowledge.runtime:application",
            factory=True,
            host=args.host,
            port=args.port,
        )
    else:
        store = open_store(Settings.from_env().database_url)
        try:
            with open(args.corpus) as f:
                data = json.load(f)
            print(json.dumps({"changed_documents": seed(store, data["documents"])}))
        finally:
            store.close()
