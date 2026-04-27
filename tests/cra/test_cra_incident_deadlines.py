"""Tests for `core.cra_incident_deadlines` — CRA Art. 14 deadlines."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from core.cra_incident_deadlines import (
    DeadlinePhase,
    DeadlineStatus,
    compute_deadlines,
)

DISCOVERED = datetime(2026, 5, 1, 10, 0, 0, tzinfo=timezone.utc)


# ──────────────── On-track ────────────────


def test_just_discovered_all_on_track() -> None:
    """Five minutes after discovery, every deadline is on_track."""
    now = DISCOVERED + timedelta(minutes=5)
    result = compute_deadlines(DISCOVERED, now=now)

    assert result.early_warning.status == DeadlineStatus.ON_TRACK
    assert result.incident_report.status == DeadlineStatus.ON_TRACK
    assert result.final_report.status == DeadlineStatus.ON_TRACK
    assert result.overall_overdue is False


def test_deadline_at_values() -> None:
    """Deadlines are discovered_at + (24h | 72h | 14d) by default."""
    result = compute_deadlines(DISCOVERED, now=DISCOVERED + timedelta(seconds=1))
    assert result.early_warning.deadline_at == DISCOVERED + timedelta(hours=24)
    assert result.incident_report.deadline_at == DISCOVERED + timedelta(hours=72)
    assert result.final_report.deadline_at == DISCOVERED + timedelta(days=14)


def test_seconds_remaining_is_positive_when_on_track() -> None:
    now = DISCOVERED + timedelta(hours=1)
    result = compute_deadlines(DISCOVERED, now=now)
    # 24h - 1h = 23h = 82800s
    assert result.early_warning.seconds_remaining == 23 * 3600


# ──────────────── Approaching ────────────────


def test_early_warning_approaching_at_t_minus_5h() -> None:
    """Within 6h of the 24h deadline → approaching."""
    now = DISCOVERED + timedelta(hours=19)  # 5h left
    result = compute_deadlines(DISCOVERED, now=now)
    assert result.early_warning.status == DeadlineStatus.APPROACHING
    assert result.incident_report.status == DeadlineStatus.ON_TRACK


def test_incident_report_approaching_at_t_minus_12h() -> None:
    now = DISCOVERED + timedelta(hours=60)  # 12h left of 72h
    result = compute_deadlines(DISCOVERED, now=now)
    assert result.early_warning.status == DeadlineStatus.OVERDUE  # 36h ago
    assert result.incident_report.status == DeadlineStatus.APPROACHING


# ──────────────── Overdue ────────────────


def test_overdue_after_24h_with_no_submission() -> None:
    now = DISCOVERED + timedelta(hours=25)
    result = compute_deadlines(DISCOVERED, now=now)

    assert result.early_warning.status == DeadlineStatus.OVERDUE
    assert result.early_warning.seconds_remaining < 0
    assert result.overall_overdue is True


def test_submission_clears_overdue_for_that_phase() -> None:
    """Submitting locks the phase to 'submitted', even if late."""
    now = DISCOVERED + timedelta(hours=25)
    result = compute_deadlines(
        DISCOVERED,
        now=now,
        early_warning_submitted_at=now,
    )
    assert result.early_warning.status == DeadlineStatus.SUBMITTED
    assert result.early_warning.submitted_at == now


def test_overall_overdue_false_when_only_overdue_phase_is_submitted() -> None:
    now = DISCOVERED + timedelta(hours=25)
    result = compute_deadlines(
        DISCOVERED,
        now=now,
        early_warning_submitted_at=now - timedelta(minutes=5),
    )
    assert result.overall_overdue is False


# ──────────────── Final-report 14d clock ────────────────


def test_final_report_clock_starts_from_corrective_measure_available() -> None:
    """Art. 14(2)(c) — 14 days from when the fix is available, not discovery."""
    fix_available = DISCOVERED + timedelta(days=30)
    now = fix_available + timedelta(days=10)
    result = compute_deadlines(
        DISCOVERED,
        corrective_measure_available_at=fix_available,
        now=now,
    )
    assert result.final_report.deadline_at == fix_available + timedelta(days=14)
    # 4 days left
    assert result.final_report.status == DeadlineStatus.ON_TRACK


def test_final_report_falls_back_to_discovery_when_no_fix_yet() -> None:
    result = compute_deadlines(
        DISCOVERED,
        corrective_measure_available_at=None,
        now=DISCOVERED + timedelta(hours=1),
    )
    assert result.final_report.deadline_at == DISCOVERED + timedelta(days=14)


def test_final_report_approaching_within_3_days() -> None:
    fix_available = DISCOVERED + timedelta(days=1)
    now = fix_available + timedelta(days=12)  # 2 days left of 14d
    result = compute_deadlines(
        DISCOVERED,
        corrective_measure_available_at=fix_available,
        now=now,
    )
    assert result.final_report.status == DeadlineStatus.APPROACHING


# ──────────────── Validation ────────────────


def test_naive_discovered_at_rejected() -> None:
    naive = datetime(2026, 5, 1, 10, 0, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        compute_deadlines(naive)


def test_naive_now_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        compute_deadlines(DISCOVERED, now=datetime(2026, 5, 2, 10))


def test_naive_corrective_measure_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        compute_deadlines(
            DISCOVERED,
            corrective_measure_available_at=datetime(2026, 5, 5),
            now=DISCOVERED + timedelta(hours=1),
        )


# ──────────────── Phase enum sanity ────────────────


def test_phase_values_match_each_info() -> None:
    result = compute_deadlines(DISCOVERED, now=DISCOVERED + timedelta(seconds=1))
    assert result.early_warning.phase == DeadlinePhase.EARLY_WARNING
    assert result.incident_report.phase == DeadlinePhase.INCIDENT_REPORT
    assert result.final_report.phase == DeadlinePhase.FINAL_REPORT
