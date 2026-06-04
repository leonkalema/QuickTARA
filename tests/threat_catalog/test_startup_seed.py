"""
Tests for core/threat_catalog/startup_seed.py and automotive_mapping.py changes.

Covers:
  - _ensure_stix_bundle returns cached file when it exists
  - _download_stix returns None on network error (no real HTTP calls)
  - _download_stix rejects non-STIX JSON
  - should_auto_seed returns True when catalog empty, False when seeded
  - auto_seed_catalog returns error dict when STIX unavailable
  - auto_seed_catalog seeds from a local STIX fixture
  - enrich_all_techniques includes unmapped techniques with defaults
  - _default_enrichment produces a valid dict with correct STRIDE from tactic
  - schedule_background_seed spawns a daemon thread
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# ── _ensure_stix_bundle ───────────────────────────────────────────────────────

class TestEnsureStixBundle:
    def test_returns_cached_file_when_exists(self, tmp_path: Path) -> None:
        from core.threat_catalog import startup_seed as ss
        fake_cache = tmp_path / "ics-attack.json"
        fake_cache.write_text('{"type": "bundle", "objects": []}')

        with patch.object(ss, "STIX_CACHE_PATH", fake_cache):
            result = ss._ensure_stix_bundle()

        assert result == fake_cache

    def test_returns_none_when_download_fails(self, tmp_path: Path) -> None:
        from core.threat_catalog import startup_seed as ss
        missing = tmp_path / "no-cache" / "ics-attack.json"

        with (
            patch.object(ss, "STIX_CACHE_PATH", missing),
            patch.object(ss, "DATA_DIR", tmp_path / "no-cache"),
            patch.object(ss, "_download_stix", return_value=None),
        ):
            result = ss._ensure_stix_bundle()

        assert result is None

    def test_tries_fallback_url_when_primary_fails(self, tmp_path: Path) -> None:
        from core.threat_catalog import startup_seed as ss
        missing = tmp_path / "ics-attack.json"
        call_log = []

        def fake_download(url, dest):
            call_log.append(url)
            return dest if "mitre/cti" in url else None  # fallback succeeds

        with (
            patch.object(ss, "STIX_CACHE_PATH", missing),
            patch.object(ss, "DATA_DIR", tmp_path),
            patch.object(ss, "_download_stix", side_effect=fake_download),
        ):
            result = ss._ensure_stix_bundle()

        assert len(call_log) == 2
        assert result is not None


# ── _download_stix ────────────────────────────────────────────────────────────

class TestDownloadStix:
    def test_returns_none_on_url_error(self, tmp_path: Path) -> None:
        import urllib.error
        from core.threat_catalog import startup_seed as ss
        dest = tmp_path / "bundle.json"
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no network")):
            result = ss._download_stix("http://example.com/bundle.json", dest)
        assert result is None
        assert not dest.exists()

    def test_returns_none_for_non_stix_json(self, tmp_path: Path) -> None:
        from core.threat_catalog import startup_seed as ss
        dest = tmp_path / "bundle.json"
        bad_json = json.dumps({"not": "a bundle"}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = bad_json
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = ss._download_stix("http://example.com/bundle.json", dest)
        assert result is None

    def test_caches_valid_stix_bundle(self, tmp_path: Path) -> None:
        from core.threat_catalog import startup_seed as ss
        dest = tmp_path / "bundle.json"
        valid = json.dumps({"type": "bundle", "objects": []}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = valid
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = ss._download_stix("http://example.com/bundle.json", dest)
        assert result == dest
        assert dest.exists()


# ── should_auto_seed ──────────────────────────────────────────────────────────

class TestShouldAutoSeed:
    @pytest.fixture
    def db(self, tmp_path):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from db.threat_catalog import Base
        engine = create_engine(f"sqlite:///{tmp_path}/tc.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
            engine.dispose()

    def test_returns_true_when_catalog_empty(self, db) -> None:
        from core.threat_catalog.startup_seed import should_auto_seed
        assert should_auto_seed(db) is True

    def test_returns_false_when_mitre_entries_exist(self, db) -> None:
        from core.threat_catalog.startup_seed import should_auto_seed
        from db.threat_catalog import ThreatCatalog
        from datetime import datetime
        db.add(ThreatCatalog(
            id="MITRE-T0001", title="Test", description="",
            stride_category="tampering", source="mitre_attack_ics",
            source_version="v14", mitre_technique_id="T0001", mitre_tactic="impact",
            automotive_relevance=3, typical_likelihood=3, typical_severity=3,
            is_user_modified=False, created_at=datetime.now(), updated_at=datetime.now(),
        ))
        db.commit()
        assert should_auto_seed(db) is False


# ── auto_seed_catalog ─────────────────────────────────────────────────────────

class TestAutoSeedCatalog:
    @pytest.fixture
    def db(self, tmp_path):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from db.threat_catalog import Base
        engine = create_engine(f"sqlite:///{tmp_path}/tc2.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
            engine.dispose()

    def test_returns_error_when_stix_unavailable(self, db) -> None:
        from core.threat_catalog import startup_seed as ss
        with patch.object(ss, "_ensure_stix_bundle", return_value=None):
            result = ss.auto_seed_catalog(db)
        assert result.get("error") == "stix_unavailable"
        assert result["created"] == 0

    def test_skips_when_already_seeded(self, db) -> None:
        from core.threat_catalog.startup_seed import auto_seed_catalog, should_auto_seed
        from db.threat_catalog import ThreatCatalog
        from datetime import datetime
        db.add(ThreatCatalog(
            id="MITRE-T0002", title="Existing", description="",
            stride_category="tampering", source="mitre_attack_ics",
            source_version="v14", mitre_technique_id="T0002", mitre_tactic="impact",
            automotive_relevance=3, typical_likelihood=3, typical_severity=3,
            is_user_modified=False, created_at=datetime.now(), updated_at=datetime.now(),
        ))
        db.commit()
        result = auto_seed_catalog(db)
        assert result["created"] == 0
        assert result["updated"] == 0

    def test_seeds_from_local_stix_fixture(self, db, tmp_path) -> None:
        """Uses a minimal synthetic STIX bundle — no real download."""
        from core.threat_catalog import startup_seed as ss

        # Minimal STIX bundle with one attack-pattern
        bundle = {
            "type": "bundle",
            "id": "bundle--test",
            "objects": [
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--test-1",
                    "name": "Test Technique",
                    "description": "A test ICS technique",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T9999"}
                    ],
                    "kill_chain_phases": [
                        {"kill_chain_name": "mitre-ics-attack", "phase_name": "impact"}
                    ],
                    "revoked": False,
                    "x_mitre_deprecated": False,
                }
            ],
        }
        stix_file = tmp_path / "test-bundle.json"
        stix_file.write_text(json.dumps(bundle))

        with patch.object(ss, "_ensure_stix_bundle", return_value=stix_file):
            result = ss.auto_seed_catalog(db)

        assert result.get("error") is None
        assert result["created"] >= 1


# ── enrich_all_techniques (include_unmapped) ──────────────────────────────────

class TestEnrichAllTechniques:
    def _make_technique(self, technique_id: str, tactic: str = "impact") -> dict:
        return {
            "stix_id": f"attack-pattern--{technique_id}",
            "mitre_technique_id": technique_id,
            "name": f"Technique {technique_id}",
            "description": "Test",
            "tactic_names": [tactic],
            "mitigations": [],
        }

    def test_includes_unmapped_with_defaults(self) -> None:
        from core.threat_catalog.automotive_mapping import enrich_all_techniques
        techniques = [self._make_technique("T9991")]
        # Empty mapping config — technique is unmapped
        result = enrich_all_techniques(techniques, mapping_config={"mappings": {}}, include_unmapped=True)
        assert len(result) == 1
        assert result[0]["mitre_technique_id"] == "T9991"
        assert result[0]["automotive_relevance"] == 2

    def test_excludes_unmapped_when_flag_false(self) -> None:
        from core.threat_catalog.automotive_mapping import enrich_all_techniques
        techniques = [self._make_technique("T9992")]
        result = enrich_all_techniques(techniques, mapping_config={"mappings": {}}, include_unmapped=False)
        assert len(result) == 0

    def test_mapped_takes_precedence_over_default(self) -> None:
        from core.threat_catalog.automotive_mapping import enrich_all_techniques
        techniques = [self._make_technique("T9993")]
        config = {"mappings": {"T9993": {"automotive_relevance": 5, "component_types": ["ECU"], "trust_zones": [], "attack_vectors": [], "typical_likelihood": 4, "typical_severity": 5, "automotive_context": "High risk ECU attack", "cwe_ids": [], "capec_ids": [], "examples": []}}}
        result = enrich_all_techniques(techniques, mapping_config=config, include_unmapped=True)
        assert result[0]["automotive_relevance"] == 5
        assert result[0]["applicable_component_types"] == ["ECU"]

    def test_default_stride_maps_from_tactic(self) -> None:
        from core.threat_catalog.automotive_mapping import enrich_all_techniques
        techniques = [self._make_technique("T9994", tactic="inhibit-response-function")]
        result = enrich_all_techniques(techniques, mapping_config={"mappings": {}}, include_unmapped=True)
        assert result[0]["stride_category"] == "denial_of_service"


# ── schedule_background_seed ──────────────────────────────────────────────────

class TestScheduleBackgroundSeed:
    def test_spawns_daemon_thread(self) -> None:
        from core.threat_catalog.startup_seed import schedule_background_seed

        called = threading.Event()

        def fake_factory():
            db = MagicMock()
            return db

        with patch("core.threat_catalog.startup_seed.auto_seed_catalog") as mock_seed:
            mock_seed.side_effect = lambda db: called.set() or {"created": 0}
            schedule_background_seed(fake_factory)
            called.wait(timeout=5)

        assert called.is_set(), "Background seed thread did not run"
