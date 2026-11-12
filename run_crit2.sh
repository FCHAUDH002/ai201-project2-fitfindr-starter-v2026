#!/bin/bash
# usage: ./run_crit2.sh <trial number>
# server must be running with a BROKEN key and AI201_CACHE=0
URL=http://localhost:5001/ask
H='Content-Type: application/json'
mkdir -p logs/archive
[ -f logs/requests.jsonl ] && mv logs/requests.jsonl logs/archive/requests_before_crit2_trial$1.jsonl
curl -s -o /dev/null -X POST $URL -H "$H" -d '{"query": "vintage graphic tee under $30"}'
curl -s -o /dev/null -X POST $URL -H "$H" -d '{"query": "designer ballgown size XXS under $5"}'
python3 - <<PY
import json
rows = [json.loads(l) for l in open("logs/requests.jsonl")]
for r in rows:
    print(r["query"], "| outcome:", r["outcome"], "| status:", r["status"])
print("different outcomes:", rows[0]["outcome"] != rows[1]["outcome"])
PY
