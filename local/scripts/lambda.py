import os, base64, json
from datetime import datetime, timezone

THRESH=float(os.getenv("THRESH", "30"))

def lambda_handler(event, context):
    processed=0; alerts=0
    for rec in event.get("Records", []):
        payload = base64.b64decode(rec["kinesis"]["data"]).decode("utf-8")
        try:
            obj = json.loads(payload)
        except Exception:
            continue
        obj["processed_at"]=datetime.now(timezone.utc).isoformat()
        obj["alert"]=should_alert(obj)
        print("[EVT]", obj)
        processed+=1; alerts+=1 if obj["alert"] else 0
    print(f"[RES] processed={processed} alerts={alerts}")
    return {"processed": processed, "alerts": alerts}

def should_alert(o):
    # Ejemplos:
    # Wikipedia: alert if o.get("type") == "new" or (not o.get("bot") and not o.get("minor"))
    # Cripto: alert if abs(price change) > X%
    # USGS: alert if magnitude >= 4.5
    # OpenAQ: alert if pm25 > umbral
    v = o.get("value") or o.get("magnitude") or 0
    try:
        return float(v) >= THRESH
    except Exception:
        return False
