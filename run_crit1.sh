#!/bin/bash
# usage: ./run_crit1.sh <trial number>
# server must be running: AI201_CACHE=0 PORT=5001 python3 serve.py (with the REAL key)
URL=http://localhost:5001/ask
H='Content-Type: application/json'
mkdir -p logs/archive
[ -f logs/requests.jsonl ] && mv logs/requests.jsonl logs/archive/after_requests_before_crit1_trial$1.jsonl

send() { curl -s -o /dev/null -X POST $URL -H "$H" -d "$1"; }

# 6 matching queries
send '{"query": "vintage graphic tee under $30"}'
send '{"query": "denim jacket under $50"}'
send '{"query": "platform sneakers size 8"}'
send '{"query": "90s track jacket in size M"}'
send '{"query": "oversized flannel shirt"}'
send '{"query": "leather belt under $20"}'
# 2 impossible queries
send '{"query": "designer ballgown size XXS under $5"}'
send '{"query": "tuxedo size XXL under $3"}'
# 1 empty wardrobe
send '{"query": "denim jacket under $50", "wardrobe": {"items": []}}'
# 1 with no query
send '{}'

python3 - <<PY
import json
rows = [json.loads(l) for l in open("logs/requests.jsonl")]
ok = {"completed", "stopped_early", "bad_request"}
fields = ["timestamp", "query", "outcome", "duration_s"]
complete = [r for r in rows if r.get("outcome") in ok and all(f in r for f in fields)]
print("new records:", len(rows), "(target 10)")
print("records with all fields and a valid outcome:", len(complete))
for r in rows:
    print(" ", r["outcome"], "|", r["duration_s"], "|", r["query"])
PY
