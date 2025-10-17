#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bridge de mercado (Coinbase WebSocket) → Amazon Kinesis Data Streams.

- Suscribe al canal 'ticker' para los PRODUCTOS indicados (BTC-USD, ETH-USD, etc.).
- Enriquecer cada mensaje con metadatos (_bridged_at).
- Hace buffering y envía a Kinesis por lotes (PutRecords).
- Soporta DRY_RUN para depurar sin enviar a Kinesis.

Dependencias:
  pip install websocket-client boto3
"""

import os
import json
import time
import threading
import traceback
from datetime import datetime, timezone

import boto3
import websocket  # websocket-client

# ==========================
# Configuración por entorno
# ==========================
REGION       = os.getenv("REGION", "us-east-1")
STREAM_NAME  = os.getenv("STREAM_NAME", "demo-stream")
# Lista separada por comas con pares de Coinbase, p.ej.: "BTC-USD,ETH-USD"
PRODUCTS     = [p.strip() for p in os.getenv("PRODUCTS", "BTC-USD,ETH-USD").split(",") if p.strip()]
# Endpoint WebSocket de Coinbase Exchange para market data público
WS_URL       = os.getenv("WS_URL", "wss://ws-feed.exchange.coinbase.com")

BATCH_SIZE   = int(os.getenv("BATCH_SIZE", "25"))    # tamaño de lote a Kinesis
FLUSH_SEC    = float(os.getenv("FLUSH_SEC", "5"))    # flush por tiempo (segundos)
DRY_RUN      = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")

# =========
# Globals
# =========
kinesis = boto3.client("kinesis", region_name=REGION)
buf, lock = [], threading.Lock()

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def log(level, msg):
    print(f"[{now_iso()}][{level}] {msg}", flush=True)

def to_record(obj: dict):
    """
    Transforma el objeto del WS en un record de Kinesis.
    PartitionKey = product_id para mantener orden por instrumento.
    """
    obj = dict(obj)  # copia superficial
    obj["_bridged_at"] = now_iso()
    product = obj.get("product_id") or "UNKNOWN"
    data = (json.dumps(obj) + "\n").encode("utf-8")
    return {"Data": data, "PartitionKey": product}

def flush(force=False):
    """
    Envía el buffer a Kinesis si:
      - force=True, o
      - hay al menos BATCH_SIZE elementos.
    """
    to_send = None
    with lock:
        if force and buf:
            to_send = buf[:]
            buf.clear()
        elif len(buf) >= BATCH_SIZE:
            to_send = buf[:]
            buf.clear()

    if not to_send:
        return

    if DRY_RUN:
        log("INFO", f"DRY_RUN=ON → simulo envío de {len(to_send)} eventos (no se llama Kinesis)")
        return

    try:
        resp = kinesis.put_records(StreamName=STREAM_NAME, Records=to_send)
        failed = resp.get("FailedRecordCount", 0)
        log("INFO", f"FLUSH → enviados={len(to_send)} fallidos={failed}")
        if failed:
            # Muestra algunos errores si los hubiera
            for rec in resp.get("Records", [])[:3]:
                if "ErrorCode" in rec:
                    log("WARN", f"{rec['ErrorCode']} - {rec.get('ErrorMessage')}")
                    break
    except Exception as e:
        log("ERROR", f"put_records lanzó excepción: {e}")
        traceback.print_exc()

def flusher_loop():
    log("INFO", f"Flusher cada {FLUSH_SEC}s (BATCH_SIZE={BATCH_SIZE}, DRY_RUN={DRY_RUN})")
    while True:
        time.sleep(FLUSH_SEC)
        flush(force=True)

# ==========================
# WebSocket callbacks
# ==========================
def on_open(ws):
    log("INFO", f"WS conectado: {WS_URL}")
    sub = {
        "type": "subscribe",
        "product_ids": PRODUCTS,
        # 'ticker' = actualizaciones de precio/bid/ask; 'matches' = trades ejecutados
        "channels": ["ticker"]
    }
    ws.send(json.dumps(sub))
    log("INFO", f"Suscrito a productos={PRODUCTS} canal='ticker' → destino Kinesis stream='{STREAM_NAME}' ({REGION})")

def on_message(ws, message):
    try:
        obj = json.loads(message)
        # Mantén sólo los mensajes de tipo 'ticker'
        if obj.get("type") != "ticker":
            return

        rec = to_record(obj)
        with lock:
            buf.append(rec)

        # Flush por tamaño
        if len(buf) >= BATCH_SIZE:
            flush(force=False)

    except Exception as e:
        log("ERROR", f"on_message: {e}")
        traceback.print_exc()

def on_error(ws, error):
    log("ERROR", f"WS error: {error}")

def on_close(ws, code, msg):
    log("WARN", f"WS cerrado code={code} msg={msg}")

# ==========
# main
# ==========
if __name__ == "__main__":
    log("INFO", f"WS_URL={WS_URL} STREAM_NAME={STREAM_NAME} REGION={REGION} DRY_RUN={DRY_RUN}")
    # Flusher por tiempo en hilo aparte
    t = threading.Thread(target=flusher_loop, daemon=True)
    t.start()

    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    try:
        ws.run_forever(ping_interval=20, ping_timeout=10)
    except KeyboardInterrupt:
        log("WARN", "Interrumpido por usuario. Flush final…")
        flush(force=True)
        log("INFO", "Listo.")
