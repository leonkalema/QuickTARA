"""CRA Art. 14 — incident reporting deadline computation.

Pure logic. No I/O, no DB. Given a discovery timestamp (and optionally
a "corrective measure available" timestamp), produces the three CRA
deadlines and a status for each:

  Deadline             Source                                Clock starts
  ──────────────────   ──────────────────────────────────    ──────────────
  early_warning (24h)  Art. 14(2)(a)                         discovery
  incident_report (72h) Art. 14(2)(b)                        discovery
  final_report (14d)   Art. 14(2)(c)                         corrective
                                                             measure
                                                             available
                                                             (falls back to
                                                             discovery if
                                                             unknown)

Source: Regulation (EU) 2024/2847, Art. 14 paragraphs 1–4.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional


# ──────────────── Constants ────────────────

EARLY_WARNING_WINDOW: timedelta = timedelta(hours=24)
INCIDENT_REPORT_WINDOW: timedelta = timedelta(hours=72)
FINAL_REPORT_WINDOW: timedelta = timedelta(days=14)

# UI "approaching" thresholds — when a deadline gets close, surface a warning
# in the UI before it goes overdue. Tuned so the user has roughly 25 % of the
# window left.
EARLY_WARNING_APPROACHING: timedelta = timedelta(hours=6)
INCIDENT_REPORT_APPROACHING: timedelta = timedelta(hours=18)
FINAL_REPORT_APPROACHING: timedelta = timedelta(days=3)


class DeadlinePhase(str, Enum):
    """Which of the three CRA Art. 14 deadlines this is."""

    EARLY_WARNING = "early_warning"
    INCIDENT_REPORT = "incident_report"
    FINAL_REPORT = "final_report"


class DeadlineStatus(str, Enum):
    """Status of a single deadline.

    Values:
      on_track    — deadline is in the future and not approaching.
      approaching — deadline within the warning threshold, action required.
      overdue     — deadline has passed and the phase has not been submitted.
      submitted   — phase was submitted (regardless of whether before/after).
    """

    ON_TRACK = "on_track"
    APPROACHING = "approaching"
    OVERDUE = "overdue"
    SUBMITTED = "submitted"


@dataclass(frozen=True)
class DeadlineInfo:
    """Computed state of a single CRA Art. 14 deadline."""

    phase: DeadlinePhase
    deadline_at: datetime
    seconds_remaining: int  # negative when overdue
    status: DeadlineStatus
    submitted_at: Optional[datetime]


@dataclass(frozen=True)
class IncidentDeadlines:
    """All three deadlines for one incident."""

    early_warning: DeadlineInfo
    incident_report: DeadlineInfo
    final_report: DeadlineInfo
    overall_overdue: bool


# ──────────────── Public API ────────────────


def compute_deadlines(
    discovered_at: datetime,
    *,
    corrective_measure_available_at: Optional[datetime] = None,
    early_warning_submitted_at: Optional[datetime] = None,
    incident_report_submitted_at: Optional[datetime] = None,
    final_report_submitted_at: Optional[datetime] = None,
    now: Optional[datetime] = None,
) -> IncidentDeadlines:
    """Compute deadlines + status for one incident.

    All timestamps must be timezone-aware. Pass ``now`` explicitly in tests
    so results are deterministic.
    """
    if discovered_at.tzinfo is None:
        raise ValueError("discovered_at must be timezone-aware")
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    final_clock_start = corrective_measure_available_at or discovered_at
    if final_clock_start.tzinfo is None:
        raise ValueError("corrective_measure_available_at must be timezone-aware")

    early_warning = _build(
        DeadlinePhase.EARLY_WARNING,
        deadline_at=discovered_at + EARLY_WARNING_WINDOW,
        approaching=EARLY_WARNING_APPROACHING,
        submitted_at=early_warning_submitted_at,
        now=now,
    )
    incident_report = _build(
        DeadlinePhase.INCIDENT_REPORT,
        deadline_at=discovered_at + INCIDENT_REPORT_WINDOW,
        approaching=INCIDENT_REPORT_APPROACHING,
        submitted_at=incident_report_submitted_at,
        now=now,
    )
    final_report = _build(
        DeadlinePhase.FINAL_REPORT,
        deadline_at=final_clock_start + FINAL_REPORT_WINDOW,
        approaching=FINAL_REPORT_APPROACHING,
        submitted_at=final_report_submitted_at,
        now=now,
    )

    overall_overdue = any(
        d.status == DeadlineStatus.OVERDUE
        for d in (early_warning, incident_report, final_report)
    )

    return IncidentDeadlines(
        early_warning=early_warning,
        incident_report=incident_report,
        final_report=final_report,
        overall_overdue=overall_overdue,
    )


# ──────────────── Internal ────────────────


def _build(
    phase: DeadlinePhase,
    *,
    deadline_at: datetime,
    approaching: timedelta,
    submitted_at: Optional[datetime],
    now: datetime,
) -> DeadlineInfo:
    seconds_remaining = int((deadline_at - now).total_seconds())

    if submitted_at is not None:
        status = DeadlineStatus.SUBMITTED
    elif seconds_remaining < 0:
        status = DeadlineStatus.OVERDUE
    elif seconds_remaining <= int(approaching.total_seconds()):
        status = DeadlineStatus.APPROACHING
    else:
        status = DeadlineStatus.ON_TRACK

    return DeadlineInfo(
        phase=phase,
        deadline_at=deadline_at,
        seconds_remaining=seconds_remaining,
        status=status,
        submitted_at=submitted_at,
    )
