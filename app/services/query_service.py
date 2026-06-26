from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset
from app.schemas.asset import AssetRead
from app.langchain_layer.query_engine import parse_query


async def natural_language_search(
    user_query: str,
    db: AsyncSession,
) -> dict:

    filters = await parse_query(user_query)

    query = select(Asset)

    if filters.get("type"):
        query = query.where(Asset.type == filters["type"])

    if filters.get("status"):
        query = query.where(Asset.status == filters["status"])

    if filters.get("criticality"):
        query = query.where(Asset.criticality == filters["criticality"])

    if filters.get("environment"):
        query = query.where(Asset.environment == filters["environment"])

    if filters.get("value_contains"):
        query = query.where(Asset.value.ilike(f"%{filters['value_contains']}%"))

    if filters.get("tag"):
        query = query.where(Asset.tags.contains([filters["tag"]]))

    result = await db.execute(query)
    assets = result.scalars().all()

    return {
        "query": user_query,
        "filters_used": filters,
        "total": len(assets),
        "results": [AssetRead.model_validate(a) for a in assets],
    }