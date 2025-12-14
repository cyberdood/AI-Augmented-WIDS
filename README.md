# AI-Augmented WIDS

![GitHub stars](https://img.shields.io/github/stars/cyberdood/AI-Augmented-WIDS)
![GitHub forks](https://img.shields.io/github/forks/cyberdood/AI-Augmented-WIDS)
![GitHub watchers](https://img.shields.io/github/watchers/cyberdood/AI-Augmented-WIDS)
![GitHub repo size](https://img.shields.io/github/repo-size/cyberdood/AI-Augmented-WIDS)
![GitHub language count](https://img.shields.io/github/languages/count/cyberdood/AI-Augmented-WIDS)
![GitHub top language](https://img.shields.io/github/languages/top/cyberdood/AI-Augmented-WIDS)
![GitHub last commit](https://img.shields.io/github/last-commit/cyberdood/AI-Augmented-WIDS)
![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/cyberdood/AI-Augmented-WIDS)

### *Wireless Intrusion Detection Enhanced with Elastic Stack, Machine Learning, and AI Contextualization*

This project implements an **AI-augmented Wireless Intrusion Detection System (WIDS)** that combines open-source wireless telemetry collection, data analytics, machine-learning–based anomaly detection, and large language model (LLM)–driven contextual analysis.

The system is designed to run on a **single Raspberry Pi 5** for lab and research use, while remaining modular and scalable for distributed or higher-throughput deployments.

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
#Run first to stand up elasticsearch, kibana, kismet, and ollama.
docker-compose up -d elasticsearch kibana kismet ollama

#View elasticsearch logs for setup token and username and password to setup kibana.
#Setup kismet by going to http://IP/2501 and set usernmae and password. Set username
#and password in the .env file for elasticsearch and kismet before executing the next steps.
docker-compose up -d feature-extractor
docker-compose run --rm ml-trainer
docker-compose up -d context-enricher
```

---

## Future Work

- Event-driven remediation
- MCP-powered Chat UI
- Multi-sensor triangulation
- Advanced ML models
