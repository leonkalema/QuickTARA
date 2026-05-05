"""
SQLAlchemy models for Damage Scenarios (canonical definition).

This is the single authoritative DamageScenario model used by all parts of
the application.  db.product_asset_models re-exports DamageScenario from here
so that ``from db.product_asset_models import DamageScenario`` keeps working.
"""
from sqlalchemy import Column, String, ForeignKey, Table, DateTime, Integer, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime

from db.product_asset_models import Base

# Association table for many-to-many relationship between components and damage scenarios
component_damage_scenario = Table(
    'component_damage_scenario',
    Base.metadata,
    Column('component_id', String, ForeignKey('components.component_id')),
    Column('scenario_id', String, ForeignKey('damage_scenarios.scenario_id')),
    UniqueConstraint('component_id', 'scenario_id', name='uq_component_damage_scenario')
)


class DamageScenario(Base):
    """SQLAlchemy model for damage scenarios (canonical, unified definition).

    This model merges the legacy (LegacyBase) and product-centric (ProductBase)
    definitions into a single class backed by the ``damage_scenarios`` table.
    """
    __tablename__ = "damage_scenarios"

    # ── Primary key ──────────────────────────────────────────────────────────
    # String PK (product-centric style) — routes and services query by scenario_id.
    scenario_id = Column(String, primary_key=True, index=True)

    # ── Basic information ─────────────────────────────────────────────────────
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # ── Damage-scenario properties ────────────────────────────────────────────
    damage_category = Column(String, nullable=False)   # Physical / Operational / Financial / Privacy …
    impact_type = Column(String, nullable=False, default="Direct")  # Direct / Indirect / Cascading

    # ── Security properties affected (C-I-A booleans) ────────────────────────
    confidentiality_impact = Column(Boolean, default=False)
    integrity_impact = Column(Boolean, default=False)
    availability_impact = Column(Boolean, default=False)

    # ── Severity and impact details ───────────────────────────────────────────
    severity = Column(String, nullable=False, default="Medium")  # Low / Medium / High / Critical
    impact_details = Column(JSON, nullable=True)

    # ── SFOP impact ratings ───────────────────────────────────────────────────
    safety_impact = Column(String, nullable=True, default="negligible")
    financial_impact = Column(String, nullable=True, default="negligible")
    operational_impact = Column(String, nullable=True, default="negligible")
    privacy_impact = Column(String, nullable=True, default="negligible")
    impact_rating_notes = Column(Text, nullable=True)

    # ── SFOP audit fields (UN R155 / ISO 21434) ───────────────────────────────
    sfop_rating_auto_generated = Column(Boolean, default=True, nullable=False)
    sfop_rating_last_edited_by = Column(String, nullable=True)
    sfop_rating_last_edited_at = Column(DateTime, nullable=True)
    sfop_rating_override_reason = Column(Text, nullable=True)

    # ── Review status ─────────────────────────────────────────────────────────
    status = Column(String, default="accepted", nullable=False)

    # ── Product-centric additions ─────────────────────────────────────────────
    # JSON blob of violated security properties (new field from ProductBase)
    violated_properties = Column(JSON, nullable=True)
    # Human-readable category tag (new field from ProductBase)
    category = Column(String, nullable=True)

    # ── Versioning and audit ──────────────────────────────────────────────────
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True, nullable=False)
    revision_notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)  # soft-delete flag

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ── Foreign keys ──────────────────────────────────────────────────────────
    # nullable=True: legacy records that pre-date product_scopes still load.
    scope_id = Column(String, ForeignKey("product_scopes.scope_id"), nullable=True)
    # nullable=True: product-centric records may not have a component reference.
    primary_component_id = Column(String, ForeignKey("components.component_id"), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    # Forward-reference strings avoid import-order issues inside the shared Base.
    product_scope = relationship("ProductScope", back_populates="damage_scenarios")
    primary_component = relationship("Component", foreign_keys=[primary_component_id])

    # Many-to-many: legacy components
    affected_components = relationship(
        "Component",
        secondary=component_damage_scenario,
        back_populates="damage_scenarios"
    )

    # Many-to-many: product assets (asset_damage_scenario is defined in product_asset_models)
    affected_assets = relationship(
        "Asset",
        secondary="asset_damage_scenario",
        back_populates="damage_scenarios"
    )

    # One-to-many: threat scenarios that reference this damage scenario
    threat_scenarios = relationship(
        "ThreatScenario",
        back_populates="damage_scenario",
        foreign_keys="ThreatScenario.damage_scenario_id"
    )
