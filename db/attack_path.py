"""
SQLAlchemy models for Attack Path Analysis
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Float, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
from uuid import uuid4

from .base import Base


# Association table for attack chains and attack paths
chain_paths = Table(
    'attack_chain_paths',
    Base.metadata,
    Column('chain_id', String, ForeignKey('attack_chains.chain_id'), primary_key=True),
    Column('path_id', String, ForeignKey('attack_paths.path_id'), primary_key=True)
)


class AttackStep(Base):
    """SQLAlchemy model for attack steps"""
    __tablename__ = "attack_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(String, unique=True, index=True, default=lambda: f"step_{uuid4().hex}")
    path_id = Column(String, ForeignKey("attack_paths.path_id"), nullable=False)
    component_id = Column(String, ForeignKey("components.component_id"), nullable=False)
    step_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    prerequisites = Column(JSON, nullable=True)
    vulnerability_ids = Column(JSON, nullable=True)
    threat_ids = Column(JSON, nullable=True)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    path = relationship("AttackPath", back_populates="steps")
    component = relationship("Component")


class AttackPath(Base):
    """SQLAlchemy model for attack paths"""
    __tablename__ = "attack_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(String, unique=True, index=True, default=lambda: f"path_{uuid4().hex}")
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    scope_id = Column(String, ForeignKey("system_scopes.scope_id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    path_type = Column(String, nullable=False)
    complexity = Column(String, nullable=False)
    entry_point_id = Column(String, ForeignKey("components.component_id"), nullable=False)
    target_id = Column(String, ForeignKey("components.component_id"), nullable=False)
    success_likelihood = Column(Float, nullable=False)
    impact = Column(JSON, nullable=False)
    risk_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    analysis = relationship("Analysis", backref="attack_paths")
    scope = relationship("SystemScope")
    entry_point = relationship("Component", foreign_keys=[entry_point_id])
    target = relationship("Component", foreign_keys=[target_id])
    steps = relationship("AttackStep", back_populates="path", cascade="all, delete-orphan")
    chains = relationship("AttackChain", secondary=chain_paths, back_populates="paths")


class AttackChain(Base):
    """SQLAlchemy model for attack chains"""
    __tablename__ = "attack_chains"
    
    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(String, unique=True, index=True, default=lambda: f"chain_{uuid4().hex}")
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    scope_id = Column(String, ForeignKey("system_scopes.scope_id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    entry_points = Column(JSON, nullable=False)
    targets = Column(JSON, nullable=False)
    attack_goal = Column(String, nullable=False)
    complexity = Column(String, nullable=False)
    success_likelihood = Column(Float, nullable=False)
    impact = Column(JSON, nullable=False)
    risk_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    analysis = relationship("Analysis", backref="attack_chains")
    scope = relationship("SystemScope")
    paths = relationship("AttackPath", secondary=chain_paths, back_populates="chains")
