# AI Context Enricher
# Runs an autonomous enrichment loop:
#   Elasticsearch -> Ollama (LLM) -> Elasticsearch

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    elasticsearch==8.* \
    requests

# Copy application code
COPY context_enricher.py /app/context_enricher.py

# Default environment values (can be overridden by docker-compose/.env)
ENV ES_VERIFY_CERTS=false \
    POLL_SECONDS=10 \
    BATCH_SIZE=10 \
    TIME_WINDOW=now-24h \
    WRITE_STRUCTURED_CONTEXT=true \
    OLLAMA_URL=http://ollama:11434 \
    OLLAMA_MODEL=llama3.1 \
    PYTHONUNBUFFERED=1

# Run the enrichment worker
CMD ["python", "/app/context_enricher.py"]
