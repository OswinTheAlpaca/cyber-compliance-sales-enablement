RESTRICTED_MESSAGE = "This answer is restricted. Please contact the Security team."


def enrich_entries(entries: list[dict], controls: dict[str, str]) -> list[dict]:
    enriched_entries = []
    for entry in entries:
        control_id = entry.get("drata_control_id", "").strip()
        control_status = controls.get(control_id, "unmapped")
        source_sensitivity = entry.get("source_sensitivity", "").strip().lower()
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


def customer_answer(entry: dict) -> str:
    if entry.get("release_status") == "approved":
        return entry["answer"]
    return RESTRICTED_MESSAGE
