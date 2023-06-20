FROM node:18.12.1-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.10.9-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir torch==1.13.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt
COPY knowledge/ ./knowledge/
COPY fixtures/ ./fixtures/
COPY scripts/ ./scripts/
COPY models/ ./models/
COPY --from=web /web/dist ./frontend/dist/
RUN useradd --uid 10001 --create-home hub && mkdir -p /app/data && chown -R hub:hub /app
USER hub
EXPOSE 8083
CMD ["python","-m","knowledge","serve","--host","0.0.0.0","--port","8083"]
