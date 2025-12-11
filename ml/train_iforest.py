#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
from joblib import dump
from sklearn.ensemble import IsolationForest

ES_URL = os.getenv("ES_URL", "http://localhost:9200")          # adjust if remote
ES_INDEX = os.getenv("ES_INDEX", "wids-wireless-features")       # same index your extractor writes to
ES_USERNAME = os.getenv("ES_USERNAME")  # optional
ES_PASSWORD = os.getenv("ES_PASSWORD")  # optional

# pick the numeric features you actually have in ES
FEATURE_FIELDS = [
    "ssid_entropy",
    "rssi_mean",
    "rssi_min",
    "rssi_max",
    "client_count",
    # add deauth/probe counts, etc. when you implement them
]

def fetch_data(es, size=5000):
    query = {
        "size": size,
        "_source": FEATURE_FIELDS,
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "ssid_entropy"}},
                    {"exists": {"field": "rssi_mean"}}
                ]
            }
        }
    }
    resp = es.search(index=ES_INDEX, body=query)
    hits = resp["hits"]["hits"]
    docs = [h["_source"] for h in hits]
    return pd.DataFrame(docs)

def main():
    es = Elasticsearch(ES_URL, verify_certs=False)
    df = fetch_data(es)

    if df.empty:
        print("No data returned from Elasticsearch; populate index first.")
        return

    # Fill missing values with 0 or a neutral value
    df = df.fillna(0.0)

    X = df[FEATURE_FIELDS].to_numpy(dtype=float)

    # Isolation Forest for unsupervised anomaly detection
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,   # expected fraction of anomalies, tweak as needed
        random_state=42
    )
    model.fit(X)

    dump(
        {"model": model, "features": FEATURE_FIELDS},
        "model.joblib"
    )
    print("Model trained and saved to model.joblib")

if __name__ == "__main__":
    main()
