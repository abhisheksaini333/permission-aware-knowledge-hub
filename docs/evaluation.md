# Measured retrieval and answer quality

The benchmark uses **12 original synthetic policy documents, three tenants, 15 answerable held-out questions and four deliberate abstention questions**. Three additional calibration questions are excluded from these results. Each retrieval mode receives the identical corpus, questions and access identities. No thresholds or model weights were tuned using the held-out answers.

Actual models: MiniLM-L6-v2 revision `7dbbc90392e2f80f3d3c277d6e90027e55de9125` and FLAN-T5-small revision `371f99f1df1429771f01227c93bd662f5eec2480`, loaded from original PyTorch files. Generation uses deterministic decoding and two CPU threads. Hardware: Apple M3 Pro, 11 CPU cores, 18 GiB RAM. Exact runtime details and corpus SHA-256 are in the raw reports.

| Chunk characters / overlap | Retrieval | Recall@3 | MRR | Answer exact match | Answer token F1 | Retrieval p50 ms | Answer p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|
| 700 / 100 | lexical | 1.00 | 1.00 | 0.60 | 0.92 | 1.0 | 619.8 |
| 700 / 100 | dense | 1.00 | 1.00 | 0.60 | 0.92 | 8.1 | 162.1 |
| 700 / 100 | fusion | 1.00 | 1.00 | 0.60 | 0.92 | 10.8 | 212.0 |
| 700 / 100 | rerank | 1.00 | 1.00 | 0.60 | 0.92 | 15.3 | 251.2 |
| 240 / 40 | lexical | 1.00 | 1.00 | 0.60 | 0.76 | 3.9 | 330.3 |
| 240 / 40 | dense | 1.00 | 1.00 | 0.80 | 0.96 | 28.9 | 1235.4 |
| 240 / 40 | fusion | 1.00 | 1.00 | 0.60 | 0.76 | 16.8 | 328.0 |
| 240 / 40 | rerank | 1.00 | 1.00 | 0.60 | 0.81 | 27.6 | 692.3 |

All four abstention questions were correctly declined by every configuration. Every configuration completed without model errors. Retrieval metrics evaluate whether the relevant **document** appears among the first three passages; they do not claim exact evidence-span localization. Answer quality is evaluated separately on the 15 answerable questions.

With 700-character chunks, semantic/fused/reranked retrieval did not improve quality over keyword retrieval on this small corpus. With 240-character chunks, semantic retrieval produced more exact answers, while lexical/fusion answer token F1 decreased. This illustrates the interaction between chunk boundaries and the context a generator sees; a retrieval hit alone does not establish answer quality. The default remains 700/100 lexical while a larger, independently labeled corpus is collected.

Latency values are observed wall-clock measurements from one serial local pass, including first-use effects and shared development-machine load. They are not capacity estimates, isolated inference benchmarks, confidence intervals, or production SLO evidence. The small, repetitive policy corpus makes retrieval comparatively easy. Token-overlap grounding is a heuristic and cannot prove entailment or resistance to arbitrary malicious documents.

Raw, inspectable cases: [700-character run](evidence/evaluation-700.json), [240-character run](evidence/evaluation-240.json). Each records expected/generated answers, retrieved sources, citations, abstention, timings, model identities and the corpus digest.

Reproduce:

```sh
python scripts/evaluate.py --model-cache "$MODEL_CACHE" --chunk-size 700 --overlap 100 --output artifacts/evaluation-700.json
python scripts/evaluate.py --model-cache "$MODEL_CACHE" --chunk-size 240 --overlap 40 --output artifacts/evaluation-240.json
```
