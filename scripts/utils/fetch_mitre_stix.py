#!/usr/bin/env python3
"""
Download MITRE ATT&CK ICS STIX 2.1 bundle from GitHub.

Purpose: One-time or periodic download of raw STIX data
Depends on: urllib (stdlib)
Used by: Admin / CI pipeline before running catalog seeder

Usage:
    python scripts/utils/fetch_mitre_stix.py [--output data/threat_catalogs/ics-attack.json]
"""
import argparse
import json
import logging
import sys
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

STIX_REPO_BASE = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master"
)
ICS_BUNDLE_URL = f"{STIX_REPO_BASE}/ics-attack/ics-attack.json"

DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "threat_catalogs"
    / "ics-attack.json"
)


def fetch_stix_bundle(url: str, output_path: Path) -> None:
    """Download STIX bundle and write to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading STIX bundle from %s", url)

    req = urllib.request.Request(url, headers={"User-Agent": "QuickTARA/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()

    # Validate it's parseable JSON
    bundle = json.loads(raw)
    obj_count = len(bundle.get("objects", []))
    logger.info("Downloaded bundle with %d objects", obj_count)

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, indent=2)

    logger.info("Saved to %s", output_path)


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Download MITRE ATT&CK ICS STIX bundle"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=ICS_BUNDLE_URL,
        help="STIX bundle URL",
    )
    args = parser.parse_args()

    try:
        fetch_stix_bundle(args.url, args.output)
        print(f"✅ STIX bundle saved to {args.output}")
    except Exception as exc:
        print(f"❌ Failed to download STIX bundle: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
