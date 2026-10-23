import csv
from library.normalizer import deduplicate_entries

ALLOWED_FILE_TYPES = {".csv"}

# Checks if the file extension is allowed. Raises ValueError if not.
def validate_file_type(filepath: str):
        if not any(filepath.endswith(ext) for ext in ALLOWED_FILE_TYPES):
            raise ValueError(
            f"Rejected file type: {filepath}."
            f"Only {ALLOWED_FILE_TYPES} are accepted."
        )

# Strips characters that could represent injection attempts or scripts.
# For production: use a dedicated sanitization library with a maintained blocklist.
def sanitize_text(text: str) -> str:
    for char in ["<", ">", "{", "}", "[", "]", "=", ";"]:
        text = text.replace(char, "")
    return text.strip()


# Parses a CSV question file and returns a list of entry dictionaries.
# Applies file type validation and text sanitization to every field.
def parse_csv(filepath: str) -> list[dict]:
    validate_file_type(filepath)
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                "question_id":          sanitize_text(row.get("question_id", "")),
                "canonical_question":   sanitize_text(row.get("canonical_question", "")),
                "answer":               sanitize_text(row.get("answer", "")),
                "drata_control_id":     sanitize_text(row.get("drata_control_id", "")),
                "sensitivity_flag":     sanitize_text(row.get("sensitivity_flag", "public")),
                "category":             sanitize_text(row.get("category", "")),
                "source":               filepath,
                "control_status":       "unknown"   # populated later by Drata sync
            })
        return entries


# Reads and parses multiple CSV files, combines tehir entries, and deduplicates them.
# Returns a deduplicated list of canonical question entries.       
def build_library(filepaths: list[str]) -> list[dict]:
    all_entries = []
    
    for filepath in filepaths:
        print(f"Ingesting: {filepath}")
        entries = parse_csv(filepath)
        all_entries.extend(entries)
    print(f"Loaded {len(all_entries)} entries. Now deduplicating...")

    deduplicated = deduplicate_entries(all_entries)
    duplicates_removed = len(all_entries) - len(deduplicated)

    print(f"\nIngestion complete. \n"
    f"  Total entries loaded: {len(all_entries)}\n"
    f"  Duplicates removed: {duplicates_removed}\n"
    f"  Canonical library entries: {len(deduplicated)}" )

    return deduplicated

