from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetRead
from app.services.query_service import natural_language_search
from app.langchain_layer.risk_scorer import score_asset_risk_mock
from app.langchain_layer.report_generator import generate_report_mock

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
async def query_assets(
    body: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = await natural_language_search(body.query, db)
    return result


@router.post("/risk/{asset_id}")
async def assess_risk(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    import uuid

    try:
        parsed_uuid = uuid.UUID(asset_id)
        result = await db.execute(select(Asset).where(Asset.id == parsed_uuid))
    except ValueError:
        result = await db.execute(select(Asset).where(Asset.external_id == asset_id))

    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    risk = await score_asset_risk_mock(asset)

    asset.risk_score = risk["risk_score"]
    asset.risk_summary = risk["risk_summary"]

    return {
        "asset_id": str(asset.id),
        "external_id": asset.external_id,
        "value": asset.value,
        "risk_score": risk["risk_score"],
        "risk_summary": risk["risk_summary"],
    }


@router.post("/risk-all")
async def assess_all_risks(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    if not assets:
        raise HTTPException(status_code=404, detail="No assets found")

    results = []
    for asset in assets:
        risk = await score_asset_risk_mock(asset)
        asset.risk_score = risk["risk_score"]
        asset.risk_summary = risk["risk_summary"]

        results.append({
            "asset_id": str(asset.id),
            "external_id": asset.external_id,
            "value": asset.value,
            "risk_score": risk["risk_score"],
            "risk_summary": risk["risk_summary"],
        })

    return {
        "total": len(results),
        "results": results,
    }
@router.post("/report")
async def generate_asset_report(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    if not assets:
        raise HTTPException(status_code=404, detail="No assets found")

    report = generate_report_mock(assets)
    return report