from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, field_validator
from app.models.asset import AssetType, AssetStatus, AssetSource, RelationshipType


# ─── Asset Schemas ─────────────────────────────────────

class AssetBase(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.active
    source: AssetSource = AssetSource.import_
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class AssetCreate(AssetBase):
    external_id: Optional[str] = None

class AssetRead(AssetBase):
    id: UUID
    external_id: Optional[str]
    first_seen: datetime
    last_seen: datetime
    environment: Optional[str] = None
    category: Optional[str] = None
    criticality: Optional[str] = None
    risk_score: Optional[str] = None
    risk_summary: Optional[str] = None
    @field_validator("metadata", mode="before")
    @classmethod
    def parse_metadata(cls, v):
        if isinstance(v, dict):
            return v
        return {}

    model_config = {"from_attributes": True}

# ─── Bulk Import Schemas ───────────────────────────────

class RawAssetImport(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None
    status: Optional[str] = "active"
    source: Optional[str] = "import"
    tags: Optional[list[str]] = []
    metadata: Optional[dict[str, Any]] = {}


class BulkImportRequest(BaseModel):
    assets: list[RawAssetImport]


class BulkImportResult(BaseModel):
    total: int
    created: int
    updated: int
    skipped: int
    errors: list[str] = []


# ─── Pagination ────────────────────────────────────────

class PaginatedAssets(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AssetRead]