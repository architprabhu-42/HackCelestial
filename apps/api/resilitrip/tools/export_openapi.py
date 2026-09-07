"""Export deterministic OpenAPI JSON for the checked-in HTTP contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from resilitrip.main import create_app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
