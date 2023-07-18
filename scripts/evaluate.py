"""Evaluate actual local models on the fixed, held-out corpus."""
import argparse, json, time, sys, platform, hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from knowledge.runtime import build_hub
from knowledge.cli import seed
from knowledge.worker import IndexWorker
from knowledge.identity import Principal
from knowledge.evaluation import retrieval_metrics, answer_metrics, summarize


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-cache", required=True)
    p.add_argument("--corpus", default="fixtures/corpus.json")
    p.add_argument("--output", default="artifacts/evaluation.json")
    p.add_argument("--chunk-size", type=int, default=700)
    p.add_argument("--overlap", type=int, default=100)
    args = p.parse_args()
    corpus = Path(args.corpus)
    data = json.loads(corpus.read_text())
    hub = build_hub("sqlite:///:memory:", args.model_cache)
    seed(hub.store, data["documents"])
    worker = IndexWorker(hub.store, hub.encoder, args.chunk_size, args.overlap)
    start = time.perf_counter()
    while worker.once():
        pass
    index_ms = (time.perf_counter() - start) * 1000
    rows = []
    for mode in ["lexical", "dense", "fusion", "rerank"]:
        for q in data["questions"]:
            if q["split"] != "heldout":
                continue
            principal = Principal(
                "evaluation-" + q["id"],
                q["tenant"],
                frozenset(q["groups"]),
                frozenset({q["role"]}),
            )
            begin = time.perf_counter()
            hits = hub.search(principal, q["question"], mode, 3)
            retrieval_ms = (time.perf_counter() - begin) * 1000
            begin = time.perf_counter()
            error = None
            try:
                answer = hub.ask(principal, q["question"], mode)
            except Exception as exc:
                answer = {"answer": "", "abstained": True, "citations": []}
                error = type(exc).__name__
            rows.append(
                dict(
                    id=q["id"],
                    mode=mode,
                    expected=q["answer"],
                    actual=answer["answer"],
                    abstained=answer["abstained"],
                    citations=answer["citations"],
                    sources=[h["source"] for h in hits],
                    **retrieval_metrics(hits, q["source"]),
                    **answer_metrics(
                        answer["answer"], answer["abstained"], q["answer"]
                    ),
                    retrieval_ms=retrieval_ms,
                    answer_ms=(time.perf_counter() - begin) * 1000,
                    error=error
                )
            )
    report = dict(
        corpus_sha256=hashlib.sha256(corpus.read_bytes()).hexdigest(),
        hardware=dict(
            machine=platform.machine(),
            processor=platform.processor(),
            python=platform.python_version(),
            platform=platform.platform(),
            torch_threads=2,
        ),
        models=dict(
            encoder="all-MiniLM-L6-v2@7dbbc90392e2f80f3d3c277d6e90027e55de9125",
            answer="flan-t5-small@371f99f1df1429771f01227c93bd662f5eec2480",
        ),
        index_ms=index_ms,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        summary=summarize(rows),
        cases=rows,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
