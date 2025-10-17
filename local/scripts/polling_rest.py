import os, time, json, requests, boto3
from datetime import datetime, timezone

REGION=os.getenv("REGION","us-east-1")
STREAM=os.getenv("STREAM","demo-stream")
URL=os.getenv("URL","https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson")
INTERVAL=int(os.getenv("INTERVAL","15"))
SEEN=set()

kds=boto3.client("kinesis", region_name=REGION)

while True:
    try:
        r = requests.get(URL, timeout=15); r.raise_for_status()
        data = r.json()
        features = data.get("features", [])
        new = []
        for f in features:
            fid = f.get("id")
            if fid and fid not in SEEN:
                SEEN.add(fid)
                event = {
                    "id": fid,
                    "magnitude": f["properties"].get("mag"),
                    "place": f["properties"].get("place"),
                    "ts": f["properties"].get("time")
                }
                new.append({"Data": (json.dumps(event)+"\n").encode("utf-8"),
                            "PartitionKey": event.get("place","unknown")})
        if new:
            resp = kds.put_records(StreamName=STREAM, Records=new)
            print("[POLL] nuevos:", len(new), "fallidos:", resp.get("FailedRecordCount",0))
    except Exception as e:
        print("[WARN]", e)
    time.sleep(INTERVAL)
