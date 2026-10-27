from library.ingestor import build_library
from library.control_loader import load_controls
from library.release_policy import customer_answer, enrich_entries
from pathlib import Path

_base = Path(__file__).parent
library = build_library([
    str(_base / "data" / "questions_library.csv"),
    str(_base / "data" / "caiq_sample.csv"),
])
controls = load_controls(str(_base / "data" / "mock_drata_controls.json"))
customer_library = enrich_entries(library, controls)

for i, entry in enumerate(customer_library, 1):
    print(f"{i}. {entry['canonical_question']}\n   {customer_answer(entry)}")