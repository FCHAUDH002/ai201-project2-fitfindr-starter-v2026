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

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
