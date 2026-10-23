from library.ingestor import build_library
from pathlib import Path

_base = Path(__file__).parent
library = build_library([
    str(_base / "data" / "questions_library.csv"),
    str(_base / "data" / "caiq_sample.csv"),
])

for i, entry in enumerate(library, 1):
    print(f"{i}. {entry['canonical_question']} — {entry['sensitivity_flag']}")