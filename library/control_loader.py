import json


# Load control statuses from a JSON file and normalize them into a stable ID-to-status map.
def load_controls(filepath: str) -> dict[str, str]:
    # Read the JSON payload from disk so we can validate and normalize the structure.
    with open(filepath, "r", encoding="utf-8") as control_file:
        payload = json.load(control_file)

    # Expect the top-level object to contain a `controls` array, since the source format
    # may vary across vendors while the downstream logic wants a common schema.
    controls = payload.get("controls") if isinstance(payload, dict) else None
    if not isinstance(controls, list):
        raise ValueError("Control data must contain a 'controls' list.")

    # Maintain a lookup by control ID so consumers can resolve status without caring where
    # the original data came from.
    control_statuses = {}
    for control in controls:
        # Each entry in the list must be a dictionary containing the core control metadata.
        if not isinstance(control, dict):
            raise ValueError("Each control must be a JSON object.")

        # Require a non-empty string ID so we can safely use it as a dictionary key.
        control_id = control.get("id")
        if not isinstance(control_id, str) or not control_id.strip():
            raise ValueError("Each control must have a non-empty string ID.")

        # Normalize human-entered statuses into consistent, comparable values for downstream
        # checks. Unknown or malformed statuses are intentionally mapped to `unknown`.
        status = control.get("status")
        normalized_status = status.strip().lower() if isinstance(status, str) else ""
        control_statuses[control_id.strip()] = (
            normalized_status
            if normalized_status in {"passing", "failing"}
            else "unknown"
        )

    return control_statuses
