import re

# Canonicalizes a question string for deduplication.
def normalize_text(text: str) -> str:
    lowercased = text.lower()
    no_punctuation = re.sub(r"[^\w\s]", "", lowercased)
    normalized_space = re.sub(r"\s+", " ", no_punctuation)
    return normalized_space.strip()

# Deduplicates questions from a combined list of entries.
def deduplicate_entries(entries: list[dict]) -> list[dict]:
    seen = {}

    for entry in entries:
        key = normalize_text(entry["canonical_question"])
        # If the normalized key is not in seen, add it with the current entry and an empty list of variants.
        if key not in seen:
            # Store the original entry along with an empty list for variants and the normalized key for reference.
            seen[key] = {**entry, "variants": [], "normalized_key": key}
        else:
            # If the normalized key is already in seen, append the current canonical question to the variants list.
            seen[key]["variants"].append(entry["canonical_question"])
    return list(seen.values())

