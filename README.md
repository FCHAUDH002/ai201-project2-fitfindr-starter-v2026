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

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
