#!/bin/bash
# usage: ./run_capstone.sh <trial number>
# start the server first: AI201_CACHE=0 PORT=5001 python3 serve.py
mkdir -p logs/archive
[ -f logs/requests.jsonl ] && mv logs/requests.jsonl logs/archive/after_requests_before_trial$1.jsonl

URL=http://localhost:5001/ask
H='Content-Type: application/json'

# criterion 3 and 4: 10 matching queries back to back
for q in 'vintage graphic tee under $30' 'denim jacket under $50' 'platform sneakers size 8' '90s track jacket in size M' 'silk slip dress in midi length under $40' 'vintage graphic tee under $25' 'denim jacket under $45' 'platform sneakers size 9' 'oversized flannel shirt' 'leather belt under $20'; do
  curl -s -X POST $URL -H "$H" -d "{\"query\": \"$q\"}" > /dev/null
done
cp logs/requests.jsonl logs/archive/after_trial$1_criteria3_4.jsonl

python3 - <<PY
import json
rows = [json.loads(l) for l in open("logs/requests.jsonl")]
done = [r for r in rows if r["outcome"] == "completed"]
print("rows:", len(rows), "completed:", len(done))
print("under 5s:", sum(r["duration_s"] < 5 for r in done), "of", len(done))
print("tokens <= 700:", sum(r["tokens"] <= 700 for r in done), "of", len(done))
print("slowest:", max(r["duration_s"] for r in done))
PY
