def chunk_text(text, size=700, overlap=100, page=1):
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("Overlap must be smaller than chunk size")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(
            dict(
                ordinal=len(chunks),
                start=start,
                end=end,
                text=text[start:end],
                page=page,
            )
        )
        if end == len(text):
            break
        start = end - overlap
    return chunks
