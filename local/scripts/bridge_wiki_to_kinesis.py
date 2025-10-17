import os, json, time, requests, boto3

REGION = os.getenv("AWS_REGION", "us-east-1")
STREAM = os.getenv("STREAM_NAME", "demo-wiki-stream")
SSE_URL = "https://stream.wikimedia.org/v2/stream/recentchange"

# User-Agent DESCRIPTIVO con forma de contacto (requisito de Wikimedia)
USER_AGENT = os.getenv(
    "USER_AGENT",
    "UdeAWikiDemo/1.0 (contact: tu-correo@udea.edu.co)"
)

kinesis = boto3.client("kinesis", region_name=REGION)

def sse_events(url):
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "User-Agent": USER_AGENT
    }

    # Reintentos con backoff exponencial simple
    backoff = 1
    while True:
        try:
            with requests.get(url, headers=headers, stream=True, timeout=60) as r:
                if r.status_code == 403:
                    raise RuntimeError(
                        "403 Forbidden: revisa que USER_AGENT sea descriptivo "
                        "e incluya un medio de contacto (política de Wikimedia)."
                    )
                r.raise_for_status()
                event_lines = []
                for raw in r.iter_lines(decode_unicode=True):
                    if raw is None:
                        continue
                    line = raw.strip()
                    if not line:
                        # fin de un evento -> devolver bloque(s) data:
                        data_lines = [l[5:] for l in event_lines if l.startswith("data:")]
                        if data_lines:
                            yield "\n".join(data_lines)
                        event_lines = []
                    else:
                        event_lines.append(line)

            # si el servidor cerró la conexión sin error, reintenta suave
            backoff = min(backoff * 2, 30)

        except Exception as e:
            print(f"[WARN] SSE error: {e}. Reintentando en {backoff}s…")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

def to_partition_key(evt):
    try:
        o = json.loads(evt)
        return o.get("wiki") or o.get("user") or "unknown"
    except Exception:
        return "unknown"

def main():
    print("[INFO] Conectando a SSE:", SSE_URL)
    batch = []
    sent = 0

    for s in sse_events(SSE_URL):
        # Puedes filtrar bots si quieres, pero para demo déjalo pasar
        try:
            obj = json.loads(s)
        except Exception:
            continue

        batch.append({
            "Data": (json.dumps(obj) + "\n").encode("utf-8"),
            "PartitionKey": to_partition_key(s)
        })

        # Envía cada 25 (o por tiempo si prefieres)
        if len(batch) >= 25:
            try:
                resp = kinesis.put_records(StreamName=STREAM, Records=batch)
                failed = resp.get("FailedRecordCount", 0)
                print(f"[PUT] enviados={len(batch)} fallidos={failed}")
            except Exception as e:
                print("[ERROR PutRecords]", e)
            batch.clear()
            sent += 25

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] fin")
