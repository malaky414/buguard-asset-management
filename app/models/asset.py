import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.database import Base


# ─── Enums ────────────────────────────────────────────

class AssetType(str, enum.Enum):
    domain = "domain"
    subdomain = "subdomain"
    ip_address = "ip_address"
    service = "service"
    certificate = "certificate"
    technology = "technology"


class AssetStatus(str, enum.Enum):
    active = "active"
    stale = "stale"
    archived = "archived"


class AssetSource(str, enum.Enum):
    import_ = "import"
    scan = "scan"
    manual = "manual"


# ─── Asset Table ──────────────────────────────────────

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=True, index=True)
    type = Column(Enum(AssetType), nullable=False, index=True)
    value = Column(String, nullable=False, index=True)
    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.active)
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    source = Column(Enum(AssetSource), nullable=False, default=AssetSource.import_)
    tags = Column(ARRAY(String), nullable=False, default=list)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)

    # AI fields - بيتملوا بعدين من LangChain
    environment = Column(String, nullable=True)
    category = Column(String, nullable=True)
    criticality = Column(String, nullable=True)
    risk_score = Column(String, nullable=True)
    risk_summary = Column(String, nullable=True)

    # العلاقات مع assets تانية
    outgoing = relationship("AssetRelationship", foreign_keys="AssetRelationship.source_id", back_populates="source_asset", cascade="all, delete-orphan")
    incoming = relationship("AssetRelationship", foreign_keys="AssetRelationship.target_id", back_populates="target_asset", cascade="all, delete-orphan")


# ─── Relationship Table ────────────────────────────────

class RelationshipType(str, enum.Enum):
    subdomain_of = "subdomain_of"
    hosted_on = "hosted_on"
    resolves_to = "resolves_to"
    covers = "covers"
    runs_on = "runs_on"
    related = "related"


class AssetRelationship(Base):
    __tablename__ = "asset_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(Enum(RelationshipType), nullable=False, default=RelationshipType.related)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    source_asset = relationship("Asset", foreign_keys=[source_id], back_populates="outgoing")
    target_asset = relationship("Asset", foreign_keys=[target_id], back_populates="incoming")