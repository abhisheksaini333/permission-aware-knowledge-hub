import re, math
from collections import Counter


def tokens(text):
    return re.findall(r"[^\W_]+", text.lower())


def lexical(query, chunks):
    terms = set(tokens(query))
    docs = [Counter(tokens(c["text"])) for c in chunks]
    if not docs or not terms:
        return []
    avg = sum(sum(d.values()) for d in docs) / len(docs) or 1
    freq = {t: sum(t in d for d in docs) for t in terms}
    out = []
    for chunk, d in zip(chunks, docs):
        score = 0.0
        length = sum(d.values())
        for t in terms:
            if d[t]:
                idf = math.log(1 + (len(docs) - freq[t] + 0.5) / (freq[t] + 0.5))
                score += idf * d[t] * 2.5 / (d[t] + 1.5 * (0.25 + 0.75 * length / avg))
        if score:
            out.append((chunk, score))
    return sorted(out, key=lambda x: (-x[1], x[0]["id"]))


def cosine(a, b):
    if len(a) != len(b) or not a or not all(
        type(v) in (int, float) and math.isfinite(v) for v in [*a, *b]
    ):
        raise ValueError("Invalid embedding vector")
    scale_a, scale_b = max(abs(v) for v in a), max(abs(v) for v in b)
    if not scale_a or not scale_b:
        return 0.0
    a, b = [v / scale_a for v in a], [v / scale_b for v in b]
    norm = math.sqrt(sum(x * x for x in a) * sum(x * x for x in b))
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / norm))


def dense(vector, chunks):
    return sorted(
        [(c, cosine(vector, c["vector"])) for c in chunks if "vector" in c],
        key=lambda x: (-x[1], x[0]["id"]),
    )


def fuse(*rankings, k=60):
    scores = {}
    chunks = {}
    for ranking in rankings:
        seen = set()
        for rank, (chunk, _) in enumerate(ranking, 1):
            key = chunk["id"]
            if key in seen:
                continue
            seen.add(key)
            chunks[key] = chunk
            scores[key] = scores.get(key, 0) + 1 / (k + rank)
    return sorted(
        [(chunks[k], s) for k, s in scores.items()], key=lambda x: (-x[1], x[0]["id"])
    )


def rerank(query, ranking):
    q = tokens(query)
    terms = set(q)

    def score(item):
        c, _ = item
        ct = set(tokens(c["text"]))
        coverage = len(terms & ct) / max(1, len(terms))
        phrase = 0.25 if " ".join(q) in " ".join(tokens(c["text"])) else 0
        return coverage + phrase

    return sorted(
        [(c, score((c, s))) for c, s in ranking], key=lambda x: (-x[1], x[0]["id"])
    )
