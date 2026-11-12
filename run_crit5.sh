#!/bin/bash
# usage: ./run_crit5.sh <trial number>
# server must be running: AI201_CACHE=0 PORT=5001 python3 serve.py
URL=http://localhost:5001/ask
H='Content-Type: application/json'
touch logs/requests.jsonl
for body in '[1,2]' '"hi"' 'not json'; do
  before=$(wc -l < logs/requests.jsonl)
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $URL -H "$H" -d "$body")
  after=$(wc -l < logs/requests.jsonl)
  echo "trial $1 | body: $body | status: $code | new log lines: $((after-before))"
done
