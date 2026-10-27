import json


def load_controls(filepath: str) -> dict[str, str]:
    """Load controls into a source-independent ID-to-status mapping."""
    with open(filepath, "r", encoding="utf-8") as control_file:
        payload = json.load(control_file)

    controls = payload.get("controls") if isinstance(payload, dict) else None
    if not isinstance(controls, list):
        raise ValueError("Control data must contain a 'controls' list.")

    control_statuses = {}
    for control in controls:
        if not isinstance(control, dict):
            raise ValueError("Each control must be a JSON object.")

        control_id = control.get("id")
        if not isinstance(control_id, str) or not control_id.strip():
            raise ValueError("Each control must have a non-empty string ID.")

        status = control.get("status")
        normalized_status = status.strip().lower() if isinstance(status, str) else ""
        control_statuses[control_id.strip()] = (
            normalized_status
            if normalized_status in {"passing", "failing"}
            else "unknown"
        )

    return control_statuses
