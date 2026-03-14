"""One-off cleanup for duplicate persisted image history entries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app as app_module


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove duplicate image rows from data/history.json.")
    parser.add_argument("--dry-run", action="store_true", help="Report duplicate counts without writing changes.")
    args = parser.parse_args()

    entries = app_module._load_history()
    deduped = app_module._dedupe_history_entries(entries)

    removed = len(entries) - len(deduped)
    print(f"Scanned {len(entries)} history entries")
    print(f"Duplicate image rows removed: {removed}")
    print(f"Remaining entries: {len(deduped)}")

    if args.dry_run or removed <= 0:
        return 0

    app_module._save_history(deduped)
    print(f"Updated {app_module.HISTORY_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())