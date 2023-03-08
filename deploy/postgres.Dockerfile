FROM postgres:14.6-alpine
RUN apk add --no-cache build-base curl \
    && curl -fsSL https://github.com/pgvector/pgvector/archive/refs/tags/v0.4.0.tar.gz -o /tmp/pgvector.tar.gz \
    && echo "b76cf84ddad452cc880a6c8c661d137ddd8679c000a16332f4f03ecf6e10bcc8  /tmp/pgvector.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/pgvector.tar.gz -C /tmp \
    && make -C /tmp/pgvector-0.4.0 with_llvm=no && make -C /tmp/pgvector-0.4.0 install with_llvm=no \
    && apk del build-base curl && rm -rf /tmp/pgvector*
