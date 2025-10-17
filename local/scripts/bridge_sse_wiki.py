import os, json, time, requests, boto3

REGION = os.getenv("REGION","us-east-1")
STREAM = os.getenv("STREAM","demo-stream")
SSE_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
USER_AGENT = os.getenv("USER_AGENT","AlumnoStreaming/1.0 (contacto: correo@example.com)")

kds = boto3.client("kinesis", region_name=REGION)

def sse_events():
    headers = {"Accept":"text/event-stream","Cache-Control":"no-cache","User-Agent":USER_AGENT}
    while True:
        try:
            with requests.get(SSE_URL, headers=headers, stream=True, timeout=60) as r:
                r.raise_for_status()
                buff = []
                for line in r.iter_lines(decode_unicode=True):
                    if line is None:
                        continue
                    line = line.strip()
                    if not line:
                        data = [l[5:] for l in buff if l.startswith("data:")]
                        if data:
                            yield json.loads("\n".join(data))
                        buff = []
                    else:
                        buff.append(line)
        except Exception as e:
            print("[WARN] SSE error:", e, "reintentando…")
            time.sleep(2)

def to_record(obj):
    pk = obj.get("wiki") or obj.get("user") or "unknown"
    return {"Data": (json.dumps(obj)+"\n").encode("utf-8"), "PartitionKey": pk}

if __name__ == "__main__":
    batch = []
    for ev in sse_events():
        batch.append(to_record(ev))
        if len(batch) >= 25:
            resp = kds.put_records(StreamName=STREAM, Records=batch)
            print("[PUT] enviados=", len(batch), "fallidos=", resp.get("FailedRecordCount",0))
            batch.clear()
