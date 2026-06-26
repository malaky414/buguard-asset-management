from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset, AssetType, AssetStatus, AssetSource
from app.schemas.asset import RawAssetImport, BulkImportResult
from app.langchain_layer.enrichment import enrich_asset


def parse_asset(raw: RawAssetImport) -> dict | None:
    try:
        if not raw.type or not raw.value:
            return None
        asset_type = AssetType(raw.type)
        status = AssetStatus(raw.status) if raw.status else AssetStatus.active
        source = AssetSource(raw.source) if raw.source else AssetSource.import_

        return {
            "external_id": raw.id,
            "type": asset_type,
            "value": raw.value.strip(),
            "status": status,
            "source": source,
            "tags": raw.tags or [],
            "metadata_": raw.metadata or {},
        }

    except (ValueError, Exception):
        return None


async def bulk_import(
    records: list[RawAssetImport],
    db: AsyncSession,
) -> BulkImportResult:
    created = 0
    updated = 0
    skipped = 0
    errors = []

    for raw in records:
        data = parse_asset(raw)

        if data is None:
            skipped += 1
            errors.append(f"Skipped invalid record: {raw.model_dump()}")
            continue

        try:
            existing = None

            if data["external_id"]:
                result = await db.execute(
                    select(Asset).where(Asset.external_id == data["external_id"])
                )
                existing = result.scalar_one_or_none()

            if existing is None:
                result = await db.execute(
                    select(Asset).where(
                        Asset.type == data["type"],
                        Asset.value == data["value"],
                    )
                )
                existing = result.scalar_one_or_none()

            if existing is None:
                asset = Asset(**data)
                db.add(asset)
                await db.flush()
                created += 1

                try:
                    enrichment = await enrich_asset(asset)
                    asset.environment = enrichment["environment"]
                    asset.criticality = enrichment["criticality"]
                    asset.category = enrichment["category"]
                    await db.flush()
                except Exception as e:
                    errors.append(f"Enrichment failed for {asset.value}: {str(e)}")

            else:
                existing.last_seen = datetime.now(timezone.utc)
                existing.status = data["status"]

                existing_tags = set(existing.tags or [])
                new_tags = set(data["tags"] or [])
                existing.tags = list(existing_tags | new_tags)

                existing_metadata = existing.metadata_ or {}
                existing_metadata.update(data["metadata_"] or {})
                existing.metadata_ = existing_metadata

                updated += 1
                if not existing.environment or not existing.criticality:
                    try:
                        enrichment = await enrich_asset(existing)
                        existing.environment = enrichment["environment"]
                        existing.criticality = enrichment["criticality"]
                        existing.category = enrichment["category"]
                        await db.flush()
                    except Exception as e:
                        errors.append(f"Enrichment failed for {existing.value}: {str(e)}")

        except Exception as e:
            skipped += 1
            errors.append(f"Error processing record {raw.id}: {str(e)}")
            continue

    return BulkImportResult(
        total=len(records),
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
    )