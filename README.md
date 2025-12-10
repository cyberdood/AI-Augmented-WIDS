# AI-Augmented Wireless Intrusion Detection System (WIDS)
Kismet → Feature Extraction → Elasticsearch → Kibana → (Optional ML + AI Explanations)

This project implements a lightweight, open-source Wireless Intrusion Detection System (WIDS) using:

- Raspberry Pi sensor(s)
- Kismet for IEEE 802.11 management-frame capture
- A custom `feature_extractor_api.py` script that polls the Kismet REST API
- Direct ingestion into Elasticsearch (no Filebeat required)
- Kibana dashboards for visualization of wireless activity and anomalies
- Optional machine learning anomaly scoring
- Optional AI contextualization using an MCP-compatible agent

The entire system can run on a **single Raspberry Pi** for lab/demo scenarios or scale across multiple sensors with a centralized Elastic cluster.

---

## Repository Contents

```
.
├── feature_extractor_api.py
├── ml/
│   ├── train_isolation_forest.ipynb
│   └── model.joblib
├── dashboards/
│   └── kibana_wids_dashboard.ndjson
├── systemd/
│   └── wids-feature-extractor.service
├── config/
│   └── elastic-index-template.json
└── README.md
```

---

## System Architecture

```
+-------------------------+        +-----------------------------+
| Raspberry Pi Sensor     |        | Elasticsearch Server        |
|-------------------------|        |-----------------------------|
| • Kismet                | -----> | • Stores wireless features  |
| • feature_extractor.py  |        | • Optional ML scoring       |
| • Optional Edge ML      |        | • Anomaly aggregation       |
+-------------------------+        +-----------------------------+
               |
               |
               v
+-----------------------------------------------+
| Kibana Dashboards                             |
| • SSID entropy, RSSI trends, rogue AP map     |
| • Deauth/probe heatmaps                        |
+-----------------------------------------------+

(optional)
               |
               v
+-----------------------------------------------+
| AI / MCP Agent                                |
| • Generates contextual explanations            |
| • Identifies suspicious AP/client behaviors    |
+-----------------------------------------------+
```

---

## 1. Install Kismet on the Raspberry Pi

```bash
sudo apt update
sudo apt install kismet kismet-capture-linux-wifi
```

Test API:

```bash
curl http://localhost:2501/system/status.json
```

Start:

```bash
sudo systemctl enable kismet
sudo systemctl start kismet
```

---

## 2. Install Elasticsearch + Kibana

Example (Docker):

```bash
sudo apt install docker.io
sudo docker pull docker.elastic.co/elasticsearch/elasticsearch:9.1.3
sudo docker.pull docker.elastic.co/kibana/kibana:9.1.3
```

Run Elasticsearch:

```bash
sudo docker run -d --name es   -p 9200:9200   -e discovery.type=single-node   docker.elastic.co/elasticsearch/elasticsearch:9.1.3
```

Run Kibana:

```bash
sudo docker run -d --name kib   -p 5601:5601 --link es:elasticsearch   docker.elastic.co/kibana/kibana:9.1.3
```

---

## 3. Install Python Dependencies

```bash
sudo apt install python3-pip
pip3 install requests elasticsearch
```

(Optional ML):

```bash
pip3 install scikit-learn pyod joblib
```

---

## 4. Running the Feature Extractor

```bash
sudo mkdir -p /opt/wids
sudo cp feature_extractor_api.py /opt/wids/
sudo chmod +x /opt/wids/feature_extractor_api.py
```

Set environment variables:

```bash
export KISMET_URL="http://localhost:2501"
export ES_URL="http://localhost:9200"
export ES_INDEX="wids-wireless-features"
export SENSOR_ID="pi-lab-01"
export SENSOR_SITE="lab-a"
export POLL_INTERVAL_SEC=10
```

Run manually:

```bash
python3 /opt/wids/feature_extractor_api.py
```

---

## 5. systemd Service

```bash
sudo cp systemd/wids-feature-extractor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl.enable wids-feature-extractor
sudo systemctl.start wids-feature-extractor
```

---

## 6. Import Dashboards

- Kibana → Stack Management → Saved Objects → Import  
- Select `dashboards/kibana_wids_dashboard.ndjson`

---

## License

MIT License
