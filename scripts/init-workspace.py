#!/usr/bin/env python3
"""Initialize an analysis workspace directory for invest-agent."""

import argparse
import json
import os
import uuid
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(
        description="Initialize an invest-agent analysis workspace."
    )
    parser.add_argument(
        "target",
        help="Stock code or industry name to analyze",
    )
    parser.add_argument(
        "--output-dir",
        default="./invest-reports",
        help="Base output directory (default: ./invest-reports)",
    )
    args = parser.parse_args()

    date_str = datetime.now().strftime("%Y%m%d")
    workspace_dir = os.path.join(args.output_dir, f"{date_str}-{args.target}")
    os.makedirs(workspace_dir, exist_ok=True)

    metadata = {
        "session_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "status": "in_progress",
    }

    metadata_path = os.path.join(workspace_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(workspace_dir)


if __name__ == "__main__":
    main()
