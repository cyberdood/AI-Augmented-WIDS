# Use a lightweight Python image
FROM python:3.11-slim

# System dependencies (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only what we need
# Adjust path if train_iforest.py lives under ml/
COPY ./train_iforest.py /app/train_iforest.py

# Install Python dependencies
RUN pip install --no-cache-dir \
    elasticsearch \
    scikit-learn \
    joblib \
    pandas \
    numpy

# Default environment variables (override at runtime)
ENV ES_URL="https://elasticsearch:9200" \
    ES_USER="elastic" \
    ES_PASS="changeme" \
    ES_VERIFY_CERTS="false"

# Run the training script when the container starts
CMD ["python", "/app/train_iforest.py"]
