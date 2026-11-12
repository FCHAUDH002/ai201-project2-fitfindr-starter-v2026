# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search matches on keyword overlap, not meaning, so a differently worded
query can miss an item that's actually there. 4 of 5 allows for that without
excusing a search that fails most of the time.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This branch is a plain if statement with nothing random involved. If
search_results is empty, it stops every time, so 5 of 5 is the honest target.

---

## 3. The selected item stays the same from search to suggest_outfit

For 5 different queries that match something, the id of session["selected_item"]
is exactly the same id that gets passed into suggest_outfit, in 5 of 5 tries.

**Why this target:** This is just passing a value through the session, with
nothing random involved. If it does fail even once, that is a real bug in 
how the session is built, not something caused by model variation.

---

## 4. The fit card always mentions the price and the platform

For 5 different items, the fit card text mentions the item's price at least
once and its platform (depop, thredUp, or poshmark) at least once, in 5 of 5
tries.

**Why this target:** The wording can vary since the model isn't deterministic, 
but price and platform are fed directly into the prompt, so there's no reason 
the model should ever drop them.

---

## 5. An empty wardrobe still gets a usable suggestion

For 5 runs with an empty wardrobe (using --empty-wardrobe), suggest_outfit
returns a non-empty string with real styling advice, not an error and not a
blank string, in 5 of 5 tries.

**Why this target:** An empty wardrobe is a normal, expected case, not an
edge case. The tool is built to handle it directly, so there's no reason it
should fail once that logic is in place.

---

<!-- ═══════════════════════ CAPSTONE PROJECT ═══════════════════════ -->

# Capstone criteria

All five criteria are run with AI201_CACHE=0. A cached answer never reaches
the model, so it would skip the pacer and add zero tokens.

## 1. Every request that reaches the route leaves a log record

For 10 requests to POST /ask (matching queries, the impossible query, the
empty wardrobe, and one with no query), the log has 10 new records. Each
has a timestamp, the query, an outcome (`completed`, `stopped_early`, or
`bad_request`), and `duration_s`. 10 of 10, in all 3 trials.

**Why this target:** The log is the point of this extension. If one request
is missing, I can't trust the log to explain what happened. Malformed
bodies and crashes are tested separately in criterion 5.

---

## 2. A bad API key gets a different outcome than an empty search

I break the key by changing one character of GEMINI_API_KEY in .env, then
send a matching query. The `outcome` value in that log record is different
from the `outcome` for the impossible query. 3 of 3 trials.

**Why this target:** On ModelUnavailable, run_agent puts "The model
couldn't be reached" in session["error"]. I expect serve.py to log that as
`stopped_early`, the same outcome as "nothing matched." The outcome field
is what I'd scan or filter on, so if both runs show `stopped_early`, the
log can't tell me at a glance whether to fix my key or my search.

---

## 3. Back-to-back requests finish in under 5 seconds

For 10 matching requests sent one right after another, all 10 have a
`duration_s` under 5. In all 3 trials.

**Why this target:** A normal run takes about 2 to 3 seconds: 2 model calls
plus starting a new MCP server process for the search. 5 seconds leaves
room for that. What would make it fail is the pacer. Each run makes 2 model
calls and the limit is 15 per minute, so 10 fast requests make 20 calls and
some request has to wait.

---

## 4. A completed run uses at most 700 tokens

For 10 completed runs, the `tokens` value in the log record is 700 or
fewer in at least 9 of 10 runs. In all 3 trials.

**Why this target:** The prompts are almost the same size every run, so the
variation comes from the output. When suggest_outfit writes two outfits
instead of one, its answer is longer, and that answer is also sent into
create_fit_card's prompt, so both calls grow. At temperature 0.9 this
happens often enough that it could fail. I allow 1 of 10 for a single long
answer.

---

## 5. Malformed bodies get a 400 and a log record

Three bad bodies sent to POST /ask each return a 400 with a message and
leave a log record with outcome `bad_request`: a JSON array `[1,2]`, a JSON
string `"hi"`, and the text `not json`. 3 of 3, in all 3 trials.

**Why this target:** serve.py assumes the body is a dict. My Provenance
Guard project crashed with a 500 on a JSON array for this same reason. A
crash before logging is the worst case, because it leaves no record at
all. I expect `not json` to pass already, since get_json(silent=True)
turns it into {} and that gets a 400 for a missing query. The array and
the string are the risky ones.

---