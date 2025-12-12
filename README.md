
# AI-Augmented WIDS
### *Wireless Intrusion Detection Enhanced with Elastic Stack, Machine Learning, and AI Contextualization*

This project implements an **AI-augmented Wireless Intrusion Detection System (WIDS)** using:

- **Kismet** for wireless telemetry acquisition  
- **Elasticsearch + Kibana** for analytics and visualization  
- **Custom Python feature extraction** (Kismet API → Elasticsearch)  
- **Machine-learning anomaly detection** using Isolation Forest  
- **Elastic’s Model Context Protocol (MCP)** for AI-driven contextual summaries  
- **Docker-based modular deployment** for portability and reproducibility  

The system is optimized for running on a **single Raspberry Pi** or on distributed nodes for scalable deployments.

---

## Table of Contents
1. System Overview  
2. Repository Structure  
3. Architecture  
4. Prerequisites  
5. Environment File (.env)  
6. Building Custom Containers  
7. Running the System  
8. Machine Learning Workflow  
9. Using the MCP Server for AI Contextualization  
10. Kibana Dashboards  
11. Future Work  

---

## System Overview
AI-Augmented-WIDS collects and analyzes wireless activity using:

### 1. Data Acquisition
- Kismet captures IEEE 802.11 management frames  
- Feature Extractor container polls the Kismet REST API  
- Extracted features are forwarded directly to Elasticsearch  

### 2. Analytics & Machine Learning
- ML trainer container builds an Isolation Forest anomaly model  
- Live wireless telemetry is scored for unusual behavior  

### 3. AI Contextualization
- MCP server retrieves feature docs missing `context.summary`  
- A local or remote LLM generates readable explanations  
- Summaries are written back into Elasticsearch  

---

## Repository Structure

```
AI-Augmented-WIDS/
│
├── feature_extractor.py         # Polls Kismet API and stores feature docs in ES
├── Dockerfile                   # Builds Feature Extractor container
│
├── ml/
│   ├── train_iforest.py         # ML model trainer (Isolation Forest)
│   ├── Dockerfile               # Builds ML training container
│   └── ml_output/               # Model persistence
│
├── dashboards/
│   ├── kibana_wids_dashboard.ndjson
│   ├── kibana_wids_dashboard_geo.ndjson
│   └── README.md
│
├── kismet_elastic_pipeline.md   # Data flow documentation
├── .env.example                 # Template environment file
└── README.md
```

---

## Architecture

```
┌──────────────────────────┐
│      Raspberry Pi        │
│  (or Linux sensor node)  │
└─────────────┬────────────┘
              │
     ┌────────▼────────┐
     │     Kismet      │
     │  (monitor mode) │
     └────────┬────────┘
              │ REST API
     ┌────────▼───────────────┐
     │  Feature Extractor     │
     │  (Docker container)    │
     └────────┬───────────────┘
              │ JSON docs
     ┌────────▼────────┐
     │ Elasticsearch   │ (vendor container)
     └────────┬────────┘
              │
   ┌──────────▼───────────┐
   │ ML Trainer Container │
   │ (Isolation Forest)   │
   └──────────┬───────────┘
              │
     ┌────────▼──────────────┐
     │    MCP Server         │ (vendor container)
     │   + Local LLM         │
     └────────┬──────────────┘
              │
     ┌────────▼──────────┐
     │     Kibana        │
     │ Dashboards & UI   │
     └────────────────────┘
```

---

## Prerequisites

### Hardware
- Raspberry Pi 5 (16GB RAM) or x86 Linux host  
- USB Wi-Fi adapter with **monitor mode**  

### Software
- Docker & Docker Compose  
- Kismet installed on host  

Vendor containers:
- `elasticsearch:8.x`  
- `kibana:8.x`  
- `mcp-server:latest`  

---

## Environment File (.env)

Place a `.env` file at the repository root:

```
ES_URL=https://es01:9200
ES_USERNAME=elastic
ES_PASSWORD=changeme
ES_INDEX=wids-wireless-features
KISMET_URL=http://kismet:2501
VERIFY_CERTS=false
```

Copy `.env.example` to get started.

---

## Building Custom Containers

### Feature Extractor

```bash
docker build -t wids-feature-extractor .
```

### ML Trainer

```bash
cd ml
docker build -t wids-train-ml .
```

---

## Running the System

### 1. Start Elasticsearch, Kibana, and MCP

```bash
docker-compose up -d es01 kibana mcp
```

### 2. Run the Feature Extractor

```bash
docker run --rm \
  --env-file .env \
  --network elastic \
  --name wids-extractor \
  wids-feature-extractor
```

### 3. Train Isolation Forest Model

```bash
docker run --rm \
  --env-file ../.env \
  --network elastic \
  -v $(pwd)/ml_output:/app/ml_output \
  wids-train-ml
```

### 4. Import Kibana Dashboards
Kibana → Stack Management → Saved Objects → Import

---

## Machine Learning Workflow

1. ML Trainer retrieves recent feature documents  
2. Isolation Forest model is trained  
3. Model saved to `ml/ml_output/model.pkl`  
4. Feature Extractor loads model during ingestion  
5. Wireless AP/device entries are scored in real time  
6. Adds fields:
   - `anomaly_score`  
   - `anomaly_label`  

---

## Using the MCP Server for AI Contextualization

The MCP server identifies documents missing contextual summaries.

### For each feature document:
1. Extracts relevant fields  
2. Sends data to an LLM (local or external)  
3. LLM generates an explanation, e.g.:

```
SSID entropy is unusually high and no manufacturer metadata is available.
Signal strength is unstable and the device was first seen recently.
Possible transient or rogue AP.
```

4. Writes `context.summary` back into Elasticsearch  
5. Kibana dashboards display enriched analysis  

---

## Kibana Dashboards

Provided dashboards include:

- SSID entropy over time  
- Rogue AP indicators  
- Device first-seen / last-seen timelines  
- RSSI stability analysis  
- AI contextual summaries panel  
- Geo-map visualization (optional GPS module)  

---

## Future Work

Possible extensions include:

- Automated MCP-powered responses (event-driven remediation)  
- Natural-language ChatUI for wireless investigations  
- Multi-sensor triangulation for rogue AP localization  
- Advanced ML models (LSTM, transformers)  
- PHY-layer features (CSI, radiotap)  
- Distributed inference across multiple sensor nodes  

---

