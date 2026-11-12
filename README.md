# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps with the thrifting process by acting on a plain-language request. A user types something like "vintage graphic tee under $30, size M" and the agent searches a set of thrifted listings for matches, picks the best one, and asks the model to suggest how to style it using pieces the user already owns. It then writes a short caption the user could actually post about the find, mentioning the price and platform. If nothing in the listings matches, the agent stops and tells the user what to change instead of guessing.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the 40 listings for items matching a description (by keyword overlap), and can also filter by size and a max price.
- **Inputs:** `description` (str): keywords describing what the user wants, like "vintage graphic tee". `size` (str, optional): a size string to filter by, like "M". `max_price` (float, optional): the highest price allowed, inclusive.
- **Returns:** A list of listing dicts, best match first. Each one has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`. At most `SEARCH_RESULT_LIMIT` (10) results.
- **When it has nothing:** Returns an empty list (`[]`). Never `None`, never an error.

### `suggest_outfit`

- **What it does:** Takes the item that was found plus the user's wardrobe, and asks the model to suggest how to style it with things the user already owns. If the wardrobe is empty, it gives general styling advice instead.
- **Inputs:** `new_item` (dict): a listing dict. `wardrobe` (dict): has an `items` key holding a list of wardrobe items, which may be empty.
- **Returns:** A non-empty string with outfit suggestions.
- **When it has nothing:** If `wardrobe["items"]` is empty, it returns general styling advice instead of failing or returning an empty string.

### `create_fit_card`

- **What it does:** Writes a short caption, two to four sentences, someone would actually post about the find. Mentions the item, the price, and the platform once each.
- **Inputs:** `outfit` (str): the suggestion text from `suggest_outfit`. `new_item` (dict): the listing dict for the item.
- **Returns:** A 2 to 4 sentence caption string.
- **When it has nothing:** If `outfit` is empty or just whitespace, it returns a simple fallback message instead of raising an error.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that tells the user what to change (loosen the price limit, try different words, or drop the size filter), and return the session right away. Do not call `suggest_outfit`. If `search_listings` finds something, take the first result as `session["selected_item"]` and move on to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex. The max price is pulled out with a pattern that catches several phrasings ("under $30", "below $30", "max $30", "up to $30", or just "$30" on its own). The size is pulled out with a pattern that matches a whole word right after "size" (like "size M" or "size US 9"), plus a second pattern that catches a bare size at the end of the query with no word "size" in front of it (like "...graphic tee, M"). Whatever text is left after removing those becomes the description.

**What moves through the session:** `query` goes in first, then `parsed` (description, size, max_price), then `search_results`, then `selected_item`, then `outfit_suggestion`, then `fit_card`.

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Pair the Y2K baby tee with your **baggy straight-leg jeans** and **chunky white sneakers** for an effortless, …
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Found the ultimate Y2K butterfly baby tee and I’m literally obsessed. 🦋 Picked it up on Depop for just $18 and…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the Y2K baby tee with your **baggy straight-leg jeans** and **chunky white sneakers** for an effortless, nostalgic streetwear look. To add some contrast, throw on your **black cropped zip hoodie** over top and accessorize with your **black crossbody bag**.

  Fit card: Found the ultimate Y2K butterfly baby tee and I’m literally obsessed. 🦋 Picked it up on Depop for just $18 and the pink and purple print is in pristine condition. Pairing this little nostalgic gem with baggy jeans and chunky sneakers is officially my new uniform.

2 model calls this session, 462 prompt + 116 output tokens

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Pair the vintage Levi's 501 jeans with the fitted white ribbed tank top and chunky white sneakers for a classic, effortless 90s-inspired look. Complete the outfit by layering the black cropped zip hoodie on top and accessorizing withthe black crossbody bag.

```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Still can’t believe I scored these vintage 501s for just $38. The medium wash fade on them is literally perfection, and they fit like a dream. Just tossed them up on depop, but honestly debating keeping them for my go-to jeans and white sneakers uniform.

```

---

## How I Used AI

**Moment 1**

- *What I asked for:* Help figuring out how to match a size filter like "M" against the listings data without false-matching unrelated sizes.
- *What came back:* A plain substring check would match "M" inside "XL" and inside sizes like "US 9", because those letters appear as substrings. The fix was to split each listing's size string into whole tokens (splitting on spaces, slashes, and parentheses) and check for an exact token match instead.
- *What I changed:* Rewrote the size filter in search_listings to split on `[\s/()]+` and compare against the resulting tokens, rather than using `in` for substring containment.

**Moment 2**

- *What I asked for:* Help understanding why create_fit_card returned the exact same caption twice in a row when I ran it on the same item.
- *What came back:* Two possible causes, both in config.py: CACHE_ENABLED reusing an answer to an identical prompt, or TEMPERATURE being set to 0.0. Since I hadn't changed either setting, it was almost certainly the cache reusing a response to an identical prompt.
- *What I changed:* Nothing in the code. I confirmed it by running the same tool with a different outfit pairing as input, which produced genuinely different wording, confirming the tool itself was working correctly and the repeat was just the cache doing its job.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════ -->

---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item matches suggest_outfit input | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe gets usable suggestion | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**

```
**Criterion 1** — `tools.py::search_listings`, `agent.py::run_agent`

$ python -c “...” (from run_eval.py, scenario: matching query completes, try 1)
[1] parse_query
in: vintage graphic tee under $30
out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
→ 10 match(es)
[3] select_item
out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
in: Y2K Baby Tee — Butterfly Print ($18.0, depop)
out: Pair the butterfly baby tee with your baggy dark-wash jeans and chunky white sneakers for an effortless, authentic Y2K streetwear look. Layer the black cropped zip hoodie over top on cooler days to complete the vintage aesthetic.
→ 10 wardrobe item(s)
[5] create_fit_card
in: Y2K Baby Tee — Butterfly Print ($18.0, depop)
out: Found the ultimate Y2K butterfly baby tee and I’m actually obsessed with the purple and pink print. Snagged it on Depop for just $18 and it looks completely brand new. Ready to live out my early 2000s pop star dreams in this.


**Criterion 2** — `agent.py::run_agent` (the branch)

$ python -c “...” (from run_eval.py, scenario: impossible query stops early, try 1)
[1] parse_query
in: designer ballgown size XXS under $5
out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: [] (empty)
→ 0 match(es)
[3] branch
→ search returned []: stopping before suggest_outfit


**Criterion 3** — `agent.py::run_agent` (session state)

$ python -c “...” (from run_eval.py, scenario: selected item matches what suggest_outfit received, try 1)
[3] select_item
out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
[4] suggest_outfit
in: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
out: Outfit 1: Pair the new light wash denim jacket with the white ribbed tank top and baggy dark wash straight-leg jeans for a classic, high-contrast “denim on denim” look. Finish the outfit with your chunky white sneakers and black crossbody bag for a casual streetwear vibe.


**Criterion 4** — `tools.py::create_fit_card`

$ python -c “...” (from run_eval.py, scenario: fit card mentions price and platform, try 1)
[5] create_fit_card
in: Platform Sneakers — White Chunky Sole ($48.0, poshmark)
out: Finally scored these chunky platform sneaks on Poshmark and I’m obsessed. Got them for $48 and they are seriously in pristine condition. Can’t wait to style them with baggy denim and a little baby tee for the ultimate Y2K moment.


**Criterion 5** — `tools.py::suggest_outfit` (empty wardrobe branch)

$ python -c “...” (from run_eval.py, scenario: empty wardrobe, try 1)
[4] suggest_outfit
in: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
out: Pair this cropped denim jacket with a classic white t-shirt and high-waisted black leggings or straight-leg trousers for an effortless, balanced silhouette. Complete the look with your favorite white sneakers or chunky boots for a casual, streetwear-ready vibe.
→ 0 wardrobe item(s)

```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET | 5/5 passes, counted against the 4-of-5 target |
| 2 | Impossible query stops before second tool | 5 of 5 | MET | 5/5 passes, branch triggered every time |
| 3 | Selected item matches suggest_outfit input | 5 of 5 | MET | 5/5 passes, same id at both trace steps every time |
| 4 | Fit card mentions price and platform | 5 of 5 | MET | 5/5 passes, both facts present every time |
| 5 | Empty wardrobe gets usable suggestion | 5 of 5 | MET | 5/5 passes, non-empty general advice every time |


**Diagnoses**

Nothing was missed, so there's nothing to diagnose in the usual sense. But
criterion 1's test was weak. It reused the same query five times instead of
testing different phrasings, so the 5/5 doesn't really prove the search
handles varied wording. That's the one I'd tighten.

---

## Loop Trace

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Pair the Y2K baby tee with your baggy straight-leg jeans and chunky white sneakers for an effortless, …
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Found the ultimate Y2K butterfly baby tee and I'm literally obsessed. 🦋 Picked it up on Depop for just $18 and…
      
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit
```

**On the MCP move:** 

search_listings now goes through mcp_server.py instead of being called
directly. To confirm it was really using MCP and not falling back, I added a
print to the except block, nothing printed, so MCP worked. The output matched
the direct call from unit 3 exactly, which is what we want.

---

## The Improvement

**What I changed:**

In `tools.py::search_listings`, I changed the keyword 4 matching to strip 
trailing "s" from words before comparing the description against each 
listing's text, so "tees" matches "tee" and similar plural or
variant word forms.

**Which failure it was meant to fix:**

My diagnosis of criterion 1 found that my test scenario used the same query 
five times, so it never actually tested whether the search handles different 
phrasings. This fix targets that gap directly, by making the search itself 
more tolerant of word variants.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item matches suggest_outfit input | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe gets usable suggestion | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

Yes. Before the fix, `search_listings('graphic tees', max_price=30)` returned 
5 results. After the fix, the same call returns 7, picking up listings that 
use "tee" where the query said "tees." I confirmed this with a direct before/after
comparison, reverting the change, running the query, then reapplying it and
running again.

---

## What's Still Broken

Nothing failed in this round of testing, but there's still room to improve.

My search only matches on exact words, now with basic plural handling
added. It still can't tell that "old band shirt" and "vintage graphic tee"
mean roughly the same thing, since there's no real synonym matching. A
better fix would be a small list of related words, or having the model pull
out search terms instead of using regex.

My criteria mostly test the normal cases and the one required branch. I
never tested what happens if a wardrobe item is missing a field, like
colors, which could break suggest_outfit when it builds the prompt. None of
my five criteria covered this, and I ran out of time to add one.


<!-- ═══════════════════════ CAPSTONE PROJECT ═══════════════════════ -->

# Capstone

## What This Extends

This extends FitFindr. The agent itself will stay the same. What will be new is that it runs through serve.py and writes a log entry every time someone uses it.

## The Shape

Shape A: deploy and instrument. Before, FitFindr only ran in my terminal. It will run as a small web service, and each request will be saved to a log file with the time, the query, what happened, and how long it took. I'm running it locally (Path B), not hosting it.

Out of scope: I'm not adding new tools or changing how search works. I'm not hosting it online. I'm not timing each individual tool, only the whole request. I'm also leaving the rate limiting and cache alone.
## Running It

I run FitFindr as a local web service (Path B). The start command and setup steps are in RUNNING.md. I tested them from a clean clone of my repo, and they worked.

## Instrumentation

Every request to /ask writes one line to logs/requests.jsonl. Each record has the timestamp, the query, the outcome (completed, stopped_early, bad_request, or crashed), the status code, how long it took in seconds, how many tokens it used, and the error message if there was one. Failed requests get a record too, not just successful ones.

Here are ten entries from a real run with the cache off:

```json
{"timestamp": "2026-11-11T21:52:27.458334+00:00", "query": "vintage graphic tee under $30", "outcome": "completed", "status": 200, "duration_s": 3.15, "tokens": 591, "error": null}
{"timestamp": "2026-11-11T21:52:29.302998+00:00", "query": "denim jacket under $50", "outcome": "completed", "status": 200, "duration_s": 1.81, "tokens": 576, "error": null}
{"timestamp": "2026-11-11T21:52:31.887311+00:00", "query": "platform sneakers size 8", "outcome": "completed", "status": 200, "duration_s": 2.55, "tokens": 578, "error": null}
{"timestamp": "2026-11-11T21:52:34.114407+00:00", "query": "90s track jacket in size M", "outcome": "completed", "status": 200, "duration_s": 2.19, "tokens": 702, "error": null}
{"timestamp": "2026-11-11T21:52:36.264742+00:00", "query": "silk slip dress in midi length under $40", "outcome": "completed", "status": 200, "duration_s": 2.12, "tokens": 699, "error": null}
{"timestamp": "2026-11-11T21:52:38.415507+00:00", "query": "vintage graphic tee under $25", "outcome": "completed", "status": 200, "duration_s": 2.12, "tokens": 580, "error": null}
{"timestamp": "2026-11-11T21:52:40.564581+00:00", "query": "denim jacket under $45", "outcome": "completed", "status": 200, "duration_s": 2.11, "tokens": 562, "error": null}
{"timestamp": "2026-11-11T21:53:26.630529+00:00", "query": "platform sneakers size 9", "outcome": "completed", "status": 200, "duration_s": 46.03, "tokens": 560, "error": null}
{"timestamp": "2026-11-11T21:53:28.901296+00:00", "query": "oversized flannel shirt", "outcome": "completed", "status": 200, "duration_s": 2.23, "tokens": 638, "error": null}
{"timestamp": "2026-11-11T21:53:30.949215+00:00", "query": "leather belt under $20", "outcome": "completed", "status": 200, "duration_s": 2.01, "tokens": 545, "error": null}
```

## What It Costs

I measured cost in tokens. The server reads the total token count before and after each run and logs the difference, so every request in logs/requests.jsonl has its own number. Over ten runs with the cache off, the average was 603.1 tokens per run (the lowest was 545 and the highest was 702). Each run makes two model calls, one for the outfit and one for the fit card.

For 100 people a day, one run each: 603.1 tokens x 100 runs = 60,310 tokens a day. My key is on the free tier, so my actual spend is $0. A paid rate would be that token total times the price per token for my model, which I haven't looked up.

The limit matters more than money here. With 2 model calls per run and 15 requests a minute, I can do about 7 runs a minute, so 100 runs in a burst would take around 14 minutes of pacing.

## Run Log and Verdicts

How I ran the trials: all runs used AI201_CACHE=0. Before each trial I moved the old log to logs/archive/ so each trial started with an empty logs/requests.jsonl. The targets for criteria 3 and 4 come from the ten-request run in Milestone 3 (about 2.3s for 9 of 10 requests, 603 tokens on average). For criterion 2 I broke the key by changing one character of GEMINI_API_KEY, restarted the server, and put the key back afterward. For criterion 5 I sent the three bodies with curl, using Content-Type: application/json.

### Run Log: Before

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request that reaches the route is logged | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 2. Bad key logs a different outcome than an empty search | 3 of 3 | not different | not different | not different | MISSED |
| 3. 10 back-to-back requests all under 5s | 10 of 10 | 9/10 | 9/10 | 9/10 | MISSED |
| 4. At most 700 tokens in at least 9 of 10 runs | 9 of 10 | 9/10 | 10/10 | 9/10 | MET |
| 5. Three malformed bodies get a 400 and a log record | 3 of 3 | 1/3 | 1/3 | 1/3 | MISSED |

