"""
Startup auto-seeder for the threat catalog.

On startup, if the catalog is empty:
  1. Try to load a cached STIX bundle from disk.
  2. If not cached, download it from MITRE GitHub (with timeout + retry).
  3. Parse the STIX bundle and enrich with automotive context.
  4. Upsert into the threat_catalog table.

Runs in a background thread so it never blocks app startup.
Falls back gracefully if the network is unavailable.

Purpose: Ship a pre-populated threat catalog out of the box — no manual steps
Depends on: core/threat_catalog/catalog_seeder.py, core/threat_catalog/stix_parser.py
Used by: api/app.py (startup event)
"""
import hashlib
import json
import logging
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from db.threat_catalog import ThreatCatalog

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

STIX_URL = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data"
    "/master/ics-attack/ics-attack.json"
)
FALLBACK_STIX_URL = (
    "https://raw.githubusercontent.com/mitre/cti"
    "/master/ics-attack/ics-attack.json"
)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "threat_catalogs"
STIX_CACHE_PATH = DATA_DIR / "ics-attack.json"
MAPPINGS_PATH = DATA_DIR / "automotive_mappings.json"
MAPPINGS_HASH_PATH = DATA_DIR / ".automotive_mappings_hash"

DOWNLOAD_TIMEOUT_SECONDS = 30


# ── Public API ────────────────────────────────────────────────────────────────

def should_auto_seed(db: Session) -> bool:
    """Return True if the catalog has no MITRE ICS entries."""
    try:
        return db.query(ThreatCatalog).filter(
            ThreatCatalog.source == "mitre_attack_ics"
        ).count() == 0
    except Exception:
        return False


def mappings_changed() -> bool:
    """
    Return True if automotive_mappings.json has changed since the last seed.
    Compares SHA-256 of the file against the stored hash.
    """
    if not MAPPINGS_PATH.exists():
        return False
    current_hash = hashlib.sha256(MAPPINGS_PATH.read_bytes()).hexdigest()
    if not MAPPINGS_HASH_PATH.exists():
        return True  # no record of previous seed — treat as changed
    return MAPPINGS_HASH_PATH.read_text().strip() != current_hash


def _record_mappings_hash() -> None:
    """Store the current automotive_mappings.json hash after a successful seed."""
    if MAPPINGS_PATH.exists():
        current_hash = hashlib.sha256(MAPPINGS_PATH.read_bytes()).hexdigest()
        MAPPINGS_HASH_PATH.write_text(current_hash)


def auto_seed_catalog(db: Session) -> Dict[str, Any]:
    """
    Seed or refresh the threat catalog.

    - First run (empty catalog): downloads STIX bundle and seeds all entries.
    - Subsequent runs: if automotive_mappings.json has changed since the last
      seed, runs a force-update so new relevance scores and component-type
      filters take effect immediately — no manual Settings action required.
    - If nothing changed: skips entirely.
    """
    empty = should_auto_seed(db)
    changed = mappings_changed()

    if not empty and not changed:
        logger.info("Threat catalog up to date — skipping seed")
        return {"created": 0, "updated": 0, "skipped": 0}

    stix_path = _ensure_stix_bundle()
    if stix_path is None:
        logger.error(
            "Could not obtain STIX bundle (no cache, download failed). "
            "Threat catalog will be empty until network is available."
        )
        return {"created": 0, "updated": 0, "skipped": 0, "error": "stix_unavailable"}

    # Force update when mappings changed so stale relevance scores and
    # component-type filters are corrected without manual intervention.
    force_update = changed and not empty

    try:
        from core.threat_catalog.catalog_seeder import seed_from_stix
        result = seed_from_stix(db, stix_path=stix_path, force_update=force_update)
        _record_mappings_hash()
        action = "force-updated" if force_update else "seeded"
        logger.info(
            "Threat catalog %s from MITRE ATT&CK ICS: "
            "created=%d updated=%d skipped=%d",
            action,
            result.get("created", 0),
            result.get("updated", 0),
            result.get("skipped", 0),
        )
        return result
    except Exception as exc:
        logger.error("Catalog seed failed: %s", exc, exc_info=True)
        return {"created": 0, "updated": 0, "skipped": 0, "error": str(exc)}


def schedule_background_seed(db_factory) -> None:
    """
    Run auto_seed_catalog in a daemon thread so app startup is not blocked.
    db_factory must be a zero-argument callable that returns a DB session.
    """
    def _run():
        db = db_factory()
        try:
            auto_seed_catalog(db)
        finally:
            db.close()

    thread = threading.Thread(target=_run, daemon=True, name="catalog-seed")
    thread.start()
    logger.info("Catalog seeder started in background thread")


# ── Internal helpers ──────────────────────────────────────────────────────────

def _ensure_stix_bundle() -> Optional[Path]:
    """
    Return path to the STIX bundle, downloading it if not already cached.
    Returns None if unavailable.
    """
    if STIX_CACHE_PATH.exists():
        logger.info("Using cached STIX bundle at %s", STIX_CACHE_PATH)
        return STIX_CACHE_PATH

    logger.info("STIX bundle not cached — downloading from MITRE GitHub…")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for url in (STIX_URL, FALLBACK_STIX_URL):
        path = _download_stix(url, STIX_CACHE_PATH)
        if path is not None:
            return path

    return None


def _download_stix(url: str, dest: Path) -> Optional[Path]:
    """
    Download the STIX bundle from url → dest.
    Returns dest on success, None on failure.
    """
    try:
        logger.info("Downloading STIX bundle from %s", url)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "QuickTARA/1.0 (threat-catalog-seeder)"},
        )
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT_SECONDS) as resp:
            raw = resp.read()

        # Validate it looks like a STIX bundle before caching
        parsed = json.loads(raw)
        if parsed.get("type") != "bundle" or "objects" not in parsed:
            logger.error("Downloaded file from %s is not a valid STIX bundle", url)
            return None

        dest.write_bytes(raw)
        size_kb = len(raw) // 1024
        logger.info(
            "STIX bundle downloaded and cached at %s (%d KB, %d objects)",
            dest, size_kb, len(parsed["objects"]),
        )
        return dest

    except urllib.error.URLError as exc:
        logger.warning("Download failed from %s: %s", url, exc)
        return None
    except (json.JSONDecodeError, KeyError) as exc:
        logger.warning("Invalid STIX data from %s: %s", url, exc)
        return None
    except Exception as exc:
        logger.warning("Unexpected error downloading from %s: %s", url, exc)
        return None
