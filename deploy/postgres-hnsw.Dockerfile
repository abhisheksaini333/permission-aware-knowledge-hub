# Build the baseline image first; it retains the 0.4 extension SQL for upgrade tests.
FROM knowledge-postgres:0.4.0
RUN apk add --no-cache build-base curl \
    && curl -fsSL https://github.com/pgvector/pgvector/archive/refs/tags/v0.5.0.tar.gz -o /tmp/pgvector.tar.gz \
    && echo "d8aa3504b215467ca528525a6de12c3f85f9891b091ce0e5864dd8a9b757f77b  /tmp/pgvector.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/pgvector.tar.gz -C /tmp \
    && make -C /tmp/pgvector-0.5.0 with_llvm=no && make -C /tmp/pgvector-0.5.0 install with_llvm=no \
    && apk del build-base curl && rm -rf /tmp/pgvector*
