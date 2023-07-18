from collections import Counter
from .retrieval import tokens


def retrieval_metrics(hits, expected):
    if expected is None:
        return {"recall_at_3": None, "reciprocal_rank": None}
    ranks = [i for i, h in enumerate(hits[:3], 1) if h["source"] == expected]
    return {
        "recall_at_3": float(bool(ranks)),
        "reciprocal_rank": 1 / ranks[0] if ranks else 0.0,
    }


def answer_metrics(answer, abstained, expected):
    if expected is None:
        return {
            "exact_match": None,
            "token_f1": None,
            "correct_abstention": float(abstained),
        }
    a = tokens(answer) if not abstained else []
    b = tokens(expected)
    shared = sum((Counter(a) & Counter(b)).values())
    precision = shared / len(a) if a else 0
    recall = shared / len(b) if b else 0
    return {
        "exact_match": float(a == b),
        "token_f1": 2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0,
        "correct_abstention": None,
    }


def average(rows, key):
    values = [r[key] for r in rows if r.get(key) is not None]
    return sum(values) / len(values) if values else None


def percentile(values, p):
    import math

    if not values:
        return None
    return sorted(values)[max(0, math.ceil(p * len(values)) - 1)]


def summarize(rows):
    result = {}
    for mode in sorted({r["mode"] for r in rows}):
        cases = [r for r in rows if r["mode"] == mode]
        result[mode] = dict(
            cases=len(cases),
            errors=sum(bool(r.get("error")) for r in cases),
            retrieval={
                k: average(cases, k) for k in ["recall_at_3", "reciprocal_rank"]
            },
            answer={
                k: average(cases, k)
                for k in ["exact_match", "token_f1", "correct_abstention"]
            },
            latency={
                "retrieval_p50_ms": percentile([r["retrieval_ms"] for r in cases], 0.5),
                "answer_p95_ms": percentile([r["answer_ms"] for r in cases], 0.95),
            },
        )
    return result
