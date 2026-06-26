from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.asset import Asset
from app.schemas.asset import (
    BulkImportRequest,
    BulkImportResult,
    AssetRead,
    PaginatedAssets,
)
from app.services.asset_service import bulk_import

router = APIRouter()


@router.post("/import", response_model=BulkImportResult)
async def import_assets(
    body: BulkImportRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await bulk_import(body.assets, db)
    return result


@router.get("/", response_model=PaginatedAssets)
async def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str = Query(None),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Asset)

    # Filtering
    if type:
        query = query.where(Asset.type == type)
    if status:
        query = query.where(Asset.status == status)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    assets = result.scalars().all()

    return PaginatedAssets(
        total=total,
        page=page,
        page_size=page_size,
        items=assets,
    )


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    import uuid

    try:
        parsed_uuid = uuid.UUID(asset_id)
        result = await db.execute(
            select(Asset).where(Asset.id == parsed_uuid)
        )
    except ValueError:
        result = await db.execute(
            select(Asset).where(Asset.external_id == asset_id)
        )

    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset