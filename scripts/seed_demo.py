"""Seed the labeled synthetic demo organization and its Hindsight memories.

Usage:
    python scripts/seed_demo.py [--force] [--no-memories]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import SessionLocal  # noqa: E402
from app.services.seed import seed_demo  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="wipe and recreate synthetic rows")
    parser.add_argument("--no-memories", action="store_true", help="skip Hindsight retains")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        result = seed_demo(db, force=args.force, retain_memories=not args.no_memories)
        print(json.dumps(result, indent=2, default=str))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
