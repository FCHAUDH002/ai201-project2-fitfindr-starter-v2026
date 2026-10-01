import re
import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # Step 1: Load every listing with load_listings().
    listings = load_listings()

    # Step 2: Filter by max_price, when provided.
    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    # Whole-token match, so "M" matches "S/M" but not "XL (oversized)".
    if size is not None:
        target = size.strip().upper()
        matched = []
        for listing in listings:
            tokens = re.split(r"[\s/()]+", listing["size"].upper())
            tokens = [t for t in tokens if t]
            if target in tokens:
                matched.append(listing)
        listings = matched

    # Step 3: Score what's left by keyword overlap with `description`.
    desc_words = set(re.findall(r"\w+", description.lower()))

    scored = []
    for listing in listings:
        haystack = " ".join([
            listing["title"],
            listing["description"],
            " ".join(listing["style_tags"]),
        ]).lower()
        haystack_words = set(re.findall(r"\w+", haystack))
        score = len(desc_words & haystack_words)

        # Step 4: Drop anything scoring zero.
        if score > 0:
            scored.append((score, listing))

    # Step 5: Sort by score, highest first, and return the listing dicts,
    # at most config.SEARCH_RESULT_LIMIT of them.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    results = [listing for _, listing in scored]
    return results[: config.SEARCH_RESULT_LIMIT]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items") or []

    item_description = (
        f"{new_item['title']} ({new_item['category']}, "
        f"{', '.join(new_item['colors'])}, "
        f"style: {', '.join(new_item['style_tags'])})"
    )

    # Step 1 + 2: empty wardrobe, general advice.
    if not items:
        prompt = (
            f"Someone is considering buying this thrifted item:\n"
            f"{item_description}\n\n"
            f"They don't have any wardrobe items saved yet. Give them one or "
            f"two general outfit ideas for how to style this piece, using "
            f"common wardrobe basics a person might already own. Keep it to "
            f"2-3 sentences."
        )
    # Step 3: real wardrobe, specific combinations.
    else:
        wardrobe_lines = "\n".join(
            f"- {it['name']} ({it['category']}, {', '.join(it['colors'])}, "
            f"style: {', '.join(it['style_tags'])})"
            for it in items
        )
        prompt = (
            f"Someone is considering buying this thrifted item:\n"
            f"{item_description}\n\n"
            f"Here is their current wardrobe:\n{wardrobe_lines}\n\n"
            f"Suggest one or two outfits that pair the new item with pieces "
            f"they already own. Name the specific pieces from their wardrobe. "
            f"Keep it to 2-3 sentences."
        )

    # Step 4: call the model and return its response.
    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # Step 1: guard against empty or whitespace-only outfit.
    if not outfit or not outfit.strip():
        return (
            f"{new_item['title']} — ${new_item['price']:.2f} on "
            f"{new_item['platform']}. No outfit details available yet."
        )

    # Step 2: build the prompt.
    brand_part = f"by {new_item['brand']} " if new_item.get("brand") else ""
    prompt = (
        f"Write a short, casual social-media caption (2-4 sentences) for a "
        f"thrifted fashion find someone is posting about. Write it like a "
        f"real person posting, not a product listing.\n\n"
        f"Item: {new_item['title']} {brand_part}"
        f"({new_item['condition']} condition, {', '.join(new_item['colors'])})\n"
        f"Price: ${new_item['price']:.2f}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit idea: {outfit}\n\n"
        f"Mention the price and the platform naturally, once each. Capture "
        f"the vibe of the piece specifically, don't write something generic "
        f"enough to apply to any item."
    )

    # Step 3: call the model and return its response.
    return generate(prompt)
