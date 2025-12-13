#!/usr/bin/env python3
"""
WIDS feature extractor for Kismet → Elasticsearch (no Filebeat).

- Polls the Kismet REST API for recently-active devices
- Derives basic per-BSSID features (RSSI, channel, SSID entropy, etc.)
- Indexes feature documents directly into Elasticsearch

Run this on the Raspberry Pi alongside Kismet and Elasticsearch.
"""

import os
import time
import math
import socket
import logging
from datetime import datetime, timezone

import requests
from elasticsearch import Elasticsearch, helpers


# ---------------------- config ----------------------

KISMET_URL = os.getenv("KISMET_URL", "http://localhost:2501")
# Relative window for "recent devices" in seconds (Kismet API uses negative seconds)
KISMET_WINDOW_SEC = int(os.getenv("KISMET_WINDOW_SEC", "10"))

ES_URL = os.getenv("ES_URL", "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "wids-wireless-features")
ES_USERNAME = os.getenv("ES_USERNAME")  # optional
ES_PASSWORD = os.getenv("ES_PASSWORD")  # optional
ES_PIPELINE = os.getenv("ES_PIPELINE")  # optional ingest pipeline name

SENSOR_ID = os.getenv("SENSOR_ID", socket.gethostname())
SENSOR_SITE = os.getenv("SENSOR_SITE", "lab")

POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("wids-feature-extractor")


# ---------------------- helpers ----------------------

def ssid_entropy(ssid: str) -> float:
    """Compute Shannon entropy of an SSID string."""
    if not ssid:
        return 0.0
    freq = {}
    for ch in ssid:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(ssid)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def epoch_to_iso(ts):
    """Convert a Unix epoch (int/float) to ISO8601, or now() if missing."""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def get_kismet_devices():
    """
    Fetch devices active in the last KISMET_WINDOW_SEC seconds.

    Uses the documented endpoint:
      /devices/last-time/{TIMESTAMP}/devices.json

    Where TIMESTAMP can be a negative number = "seconds before now".
    :contentReference[oaicite:0]{index=0}
    """
    url = f"{KISMET_URL}/devices/last-time/-{KISMET_WINDOW_SEC}/devices.json"
    log.debug("Requesting Kismet devices from %s", url)
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    # Kismet returns a list of device objects
    return data


def build_feature_doc(device: dict, sensor_time_iso: str) -> dict | None:
    """
    Map a Kismet device JSON into a feature document for Elasticsearch.

    Your Kismet JSON uses *flattened* keys like:
      "kismet.device.base.macaddr"
      "kismet.device.base.name"
    so we read those directly instead of a nested "kismet.device.base" dict.
    """

    def base(field, default=None):
        """Helper for base fields."""
        return device.get(f"kismet.device.base.{field}", default)

    # --- core identity fields ---
    bssid = base("macaddr")
    if not bssid:
        # Skip devices without a MAC (non-802.11, SDR-only, etc.)
        return None

    ssid = base("name") or base("commonname")
    manuf = base("manuf")
    channel = base("channel")
    phyname = base("phyname")

    first_time = base("first_time")
    last_time = base("last_time")

    # --- signal stats (best-effort; may or may not exist depending on Kismet build) ---
    # You can tweak these keys after dumping a full device JSON.
    rssi_last = device.get("kismet.common.signal.last")
    rssi_min  = device.get("kismet.common.signal.min")
    rssi_max  = device.get("kismet.common.signal.max")
    rssi_avg  = device.get("kismet.common.signal.avg")

    # client count (if Kismet exposes it)
    num_clients = base("num_clients", 0)

    # --- SSID entropy ---
    ssid_ent = ssid_entropy(ssid) if ssid else 0.0

    doc = {
        "@timestamp": epoch_to_iso(last_time) if last_time else sensor_time_iso,

        "sensor.id": SENSOR_ID,
        "sensor.site": SENSOR_SITE,

        "bssid": bssid,
        "ssid": ssid,
        "ssid_entropy": ssid_ent,

        "manuf": manuf,
        "channel": channel,
        "phyname": phyname,

        "first_seen": epoch_to_iso(first_time) if first_time else None,
        "last_seen": epoch_to_iso(last_time) if last_time else None,

        "rssi_last": rssi_last,
        "rssi_min": rssi_min,
        "rssi_max": rssi_max,
        "rssi_mean": rssi_avg,

        "client_count": num_clients,

        # Placeholders for future enhancements
        "deauth_count_approx": None,
        "probe_req_count_approx": None,
    }

    return doc

def get_es_client() -> Elasticsearch:
    """Create an Elasticsearch client."""
    if ES_USERNAME and ES_PASSWORD:
        es = Elasticsearch(
            ES_URL,
            basic_auth=(ES_USERNAME, ES_PASSWORD),
            verify_certs=False,
        )
    else:
        es = Elasticsearch(
            ES_URL,
            verify_certs=False,
        )
    return es


def bulk_index(es: Elasticsearch, docs: list[dict]):
    """Index a batch of documents into Elasticsearch."""
    if not docs:
        return

    actions = []
    for doc in docs:
        action = {
            "_index": ES_INDEX,
            "_source": doc,
        }
        if ES_PIPELINE:
            action["pipeline"] = ES_PIPELINE
        actions.append(action)

    helpers.bulk(es, actions)
    log.info("Indexed %d documents into %s", len(docs), ES_INDEX)


# ---------------------- main loop ----------------------

def main():
    es = get_es_client()
    log.info("Starting WIDS feature extractor")
    log.info("Kismet URL: %s  window: %ds", KISMET_URL, KISMET_WINDOW_SEC)
    log.info("Elasticsearch: %s index: %s", ES_URL, ES_INDEX)

    while True:
        sensor_now_iso = datetime.now(timezone.utc).isoformat()
        try:
            devices = get_kismet_devices()
            docs = []

            for dev in devices:
                doc = build_feature_doc(dev, sensor_now_iso)
                if doc:
                    docs.append(doc)

            if docs:
                bulk_index(es, docs)
            else:
                log.debug("No devices to index this cycle")

        except Exception as e:
            log.error("Error in main loop: %s", e, exc_info=True)

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Shutting down on Ctrl+C")
