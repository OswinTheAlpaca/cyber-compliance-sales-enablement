# Shared response used when a customer request is blocked by policy.
RESTRICTED_MESSAGE = "This answer is restricted. Please contact the Security team."


# Add release-policy metadata to each entry so callers can decide whether an answer is safe to
# disclose without re-deriving the same business rules repeatedly.
def enrich_entries(entries: list[dict], controls: dict[str, str]) -> list[dict]:
    # Track the enhanced results in a separate list so the original input data remains unchanged.
    enriched_entries = []
    for entry in entries:
        # Normalize the Drata control ID so it matches the keys used in the control map.
        control_id = entry.get("drata_control_id", "").strip()
        # Look up the control status by ID, defaulting to "unmapped" if the source record is
        # missing or not yet aligned with the registry.
        control_status = controls.get(control_id, "unmapped")
        # Standardize source sensitivity to a lowercase value so comparisons are stable.
        source_sensitivity = entry.get("source_sensitivity", "").strip().lower()
        # Release is approved only when the content is public and the required control is passing.
        release_status = (
            "approved"
            if source_sensitivity == "public" and control_status == "passing"
            else "restricted"
        )
        enriched_entries.append({
            **entry,
            "control_status": control_status,
            "release_status": release_status,
        })

    return enriched_entries


# Return the answer only when the entry has already been approved by the release policy.
def customer_answer(entry: dict) -> str:
    if entry.get("release_status") == "approved":
        return entry["answer"]
    return RESTRICTED_MESSAGE
