import json
import tempfile
import unittest
from pathlib import Path

from library.control_loader import load_controls
from library.release_policy import RESTRICTED_MESSAGE, customer_answer, enrich_entries


# Verify that control data is validated and normalized before policy evaluation.
class ControlLoaderTests(unittest.TestCase):
    # Confirm valid statuses are retained and unsupported or missing statuses become unknown.
    def test_loads_control_statuses_and_marks_unusable_status_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a temporary file so the test does not depend on repository data.
            control_file = Path(temp_dir) / "controls.json"
            control_file.write_text(json.dumps({
                "controls": [
                    {"id": "CTL-001", "status": "passing"},
                    {"id": "CTL-002", "status": "not available"},
                    {"id": "CTL-003"},
                ]
            }), encoding="utf-8")

            self.assertEqual(load_controls(str(control_file)), {
                "CTL-001": "passing",
                "CTL-002": "unknown",
                "CTL-003": "unknown",
            })

    # Ensure documents without the required controls list fail validation.
    def test_rejects_malformed_control_document(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            control_file = Path(temp_dir) / "controls.json"
            control_file.write_text('{"items": []}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_controls(str(control_file))


# Exercise the allow/restrict decisions and the customer-facing response.
class ReleasePolicyTests(unittest.TestCase):
    # Only public entries backed by passing controls should be approved.
    def test_only_public_answers_with_passing_controls_are_approved(self):
        entries = [
            {"answer": "public answer", "source_sensitivity": "public", "drata_control_id": "CTL-001"},
            {"answer": "restricted answer", "source_sensitivity": "restricted", "drata_control_id": "CTL-001"},
            {"answer": "failing answer", "source_sensitivity": "public", "drata_control_id": "CTL-002"},
            {"answer": "unmapped answer", "source_sensitivity": "public", "drata_control_id": "CTL-003"},
            {"answer": "unknown answer", "source_sensitivity": "public", "drata_control_id": "CTL-004"},
            {"answer": "missing sensitivity", "drata_control_id": "CTL-001"},
        ]

        result = enrich_entries(entries, {
            "CTL-001": "passing",
            "CTL-002": "failing",
            "CTL-004": "unknown",
        })

        # Check both the release decision and the control lookup result for each input.
        self.assertEqual(
            [entry["release_status"] for entry in result],
            ["approved", "restricted", "restricted", "restricted", "restricted", "restricted"],
        )
        self.assertEqual(
            [entry["control_status"] for entry in result],
            ["passing", "passing", "failing", "unmapped", "unknown", "passing"],
        )

    # Confirm restricted responses do not reveal either the answer or internal control state.
    def test_restricted_customer_output_does_not_disclose_internal_state(self):
        entry = {
            "answer": "Confidential source answer",
            "control_status": "failing",
            "release_status": "restricted",
        }

        output = customer_answer(entry)

        # Assert the safe message is returned and sensitive details stay hidden.
        self.assertEqual(output, RESTRICTED_MESSAGE)
        self.assertNotIn("failing", output)
        self.assertNotIn("Confidential source answer", output)


# Keep the module runnable directly as well as through the test runner.
if __name__ == "__main__":
    unittest.main()
