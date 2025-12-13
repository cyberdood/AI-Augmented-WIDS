# AI-Augmented WIDS
### *Wireless Intrusion Detection Enhanced with Elastic Stack, Machine Learning, and AI Contextualization*

This project implements an **AI-augmented Wireless Intrusion Detection System (WIDS)** that combines open-source wireless telemetry collection, data analytics, machine-learning–based anomaly detection, and large language model (LLM)–driven contextual analysis.

The system is designed to run on a **single Raspberry Pi** for lab and research use, while remaining modular and scalable for distributed or higher-throughput deployments.

---

## Key Technologies

- **Kismet** — wireless telemetry collection (IEEE 802.11 management frames)
- **Elasticsearch + Kibana** — centralized storage, analytics, dashboards
- **Custom Python feature extraction** — Kismet REST API → Elasticsearch
- **Machine learning (Isolation Forest)** — anomaly detection on wireless features
- **AI Context Enricher (Ollama)** — autonomous LLM-based event contextualization
- **Elastic Model Context Protocol (MCP)** — interactive AI analysis of Elastic data
- **Docker / Docker Compose** — modular, portable deployment

---

## System Overview

AI-Augmented-WIDS processes wireless activity through four logical layers:

### Data Acquisition
- Kismet captures IEEE 802.11 management frames
- Feature Extractor polls the Kismet REST API
- Structured feature documents are written to Elasticsearch

### Analytics & Anomaly Detection
- Isolation Forest model trained in a container
- Live wireless telemetry is scored for anomalies

### AI Context Enrichment
- Context Enricher finds docs missing `context.summary`
- Ollama LLM generates threat context and mitigations
- Context is written back into Elasticsearch

### Visualization & Interactive AI
- Kibana dashboards visualize activity and alerts
- MCP enables interactive AI investigation of Elastic data

---

## Repository Structure

```
AI-Augmented-WIDS/
├── context_enricher/
|   ├── context_enricher.py
|   └──Dockerfile
├── feature_extractor
|   ├──feature_extractor.py
|   └──Dockerfile
├── kismet/
|   └──Dockerfile
├── ml/
│   ├── train_iforest.py
│   ├── Dockerfile
│   └── ml_output/
├── dashboards/
│   ├── kibana_wids_dashboard.ndjson
│   └── kibana_wids_dashboard_geo.ndjson
├── docker-compose.yml
├── .env
└── README.md
```

---

## Prerequisites

- Raspberry Pi 5 or x86 Linux
- USB Wi-Fi adapter with monitor mode
- Docker & Docker Compose
- Kismet

---

## Environment File (.env)

```bash
ES_URL=https://es01:9200
ES_USERNAME=elastic
ES_PASSWORD=changeme
ES_INDEX=wids-wireless-features
ES_VERIFY_CERTS=false
KISMET_URL=http://kismet:2501
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1
```

---

## Running the System

```bash
docker compose up -d elasticsearch kibana ollama
docker run --rm --env-file .env --network elastic wids-feature-extractor
docker run --rm --env-file .env --network elastic -v $(pwd)/ml/ml_output:/app/ml_output wids-train-ml
docker run -d --env-file .env --network elastic wids-context-enricher
```

---

## Future Work

- Event-driven remediation
- MCP-powered Chat UI
- Multi-sensor triangulation
- Advanced ML models
