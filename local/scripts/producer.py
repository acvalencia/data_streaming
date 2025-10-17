# producer.py
import os
import json
import time
import uuid
import random
from datetime import datetime, timezone
import boto3

# ================== CONFIGURACIÓN ==================
REGION = os.getenv("REGION", "us-east-1")          # cambia si tu stream está en otra región
STREAM_NAME = os.getenv("STREAM_NAME", "demo-stream")
MODE = os.getenv("MODE", "stream")                 # "stream" (1x1) o "micro-batch"
INTERVAL_S = float(os.getenv("INTERVAL_S", "5"))   # cada cuánto generamos datos (segundos)

# Micro-batch
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "3"))     # eventos por lote en micro-batch
PARTITION_KEY_FIELD = "device_id"                  # clave de partición (mantén orden por dispositivo)

# ===================================================
kinesis = boto3.client("kinesis", region_name=REGION)

def build_event(seq_num: int) -> dict:
    """Genera un evento tipo 'sensor' con temperatura."""
    return {
        "id": str(uuid.uuid4()),
        "seq": seq_num,
        "device_id": "sensor-001",
        "value": round(random.uniform(18.0, 36.0), 2),  # temperatura simulada
        "sent_at_utc": datetime.now(timezone.utc).isoformat()
    }

def send_one(event: dict):
    """Envío 1 a 1 -> PutRecord (stream real)."""
    pk = str(event.get(PARTITION_KEY_FIELD, "default"))
    resp = kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=(json.dumps(event) + "\n").encode("utf-8"),
        PartitionKey=pk
    )
    print(f"[STREAM] seq={event['seq']} shard={resp.get('ShardId')} value={event['value']}")

def send_batch(events: list[dict]):
    """Envío por lotes -> PutRecords (micro-batch)."""
    records = [{
        "Data": (json.dumps(e) + "\n").encode("utf-8"),
        "PartitionKey": str(e.get(PARTITION_KEY_FIELD, "default"))
    } for e in events]
    resp = kinesis.put_records(StreamName=STREAM_NAME, Records=records)
    failed = resp.get("FailedRecordCount", 0)
    seqs = [e["seq"] for e in events]
    print(f"[BATCH] enviados={len(events)} fallidos={failed} seqs={seqs}")

def main():
    print(f"[INFO] Enviando a Kinesis stream='{STREAM_NAME}' region='{REGION}' "
          f"modo='{MODE}' cada {INTERVAL_S}s. Ctrl+C para detener.")
    seq = 1
    batch = []

    while True:
        event = build_event(seq)
        if MODE == "stream":
            send_one(event)
        else:
            batch.append(event)
            if len(batch) >= BATCH_SIZE:
                send_batch(batch)
                batch.clear()

        seq += 1
        time.sleep(INTERVAL_S)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Detenido por el usuario.")
