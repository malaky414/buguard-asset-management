import json
from langchain.prompts import ChatPromptTemplate
from app.langchain_layer.query_engine import get_llm


RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are a cybersecurity expert assessing risk for digital assets in an Attack Surface Management system.

Analyze the given asset and return ONLY a JSON object:
{{
  "risk_score": "high or medium or low",
  "risk_summary": "2-3 sentences explaining the risk in plain English"
}}

Risk guidelines:
- high: expired certificates, public-facing prod assets, ip_address exposed, unknown services
- medium: subdomains with no clear owner, staging assets exposed publicly, stale assets
- low: dev/internal assets, already archived, well-known technologies

Return ONLY the JSON, no explanation.
"""),
    ("human", """
Assess this asset:
- Type: {type}
- Value: {value}
- Status: {status}
- Environment: {environment}
- Criticality: {criticality}
- Category: {category}
- Tags: {tags}
- Metadata: {metadata}
""")
])


async def score_asset_risk(asset) -> dict:
    llm = get_llm()
    chain = RISK_PROMPT | llm

    response = await chain.ainvoke({
        "type": asset.type.value if hasattr(asset.type, 'value') else asset.type,
        "value": asset.value,
        "status": asset.status.value if hasattr(asset.status, 'value') else asset.status,
        "environment": asset.environment or "unknown",
        "criticality": asset.criticality or "unknown",
        "category": asset.category or "unknown",
        "tags": ", ".join(asset.tags or []),
        "metadata": json.dumps(asset.metadata_ or {}),
    })

    raw = response.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {}

    valid_scores = {"high", "medium", "low"}

    return {
        "risk_score": result.get("risk_score") if result.get("risk_score") in valid_scores else "medium",
        "risk_summary": result.get("risk_summary") or "Unable to assess risk at this time.",
    }


async def score_asset_risk_mock(asset) -> dict:
    asset_type = asset.type.value if hasattr(asset.type, 'value') else asset.type
    status = asset.status.value if hasattr(asset.status, 'value') else asset.status
    environment = asset.environment or "unknown"
    criticality = asset.criticality or "low"

    if status == "stale" or asset_type == "certificate":
        risk_score = "high"
        risk_summary = (
            f"This {asset_type} ({asset.value}) requires immediate attention. "
            f"{'Stale assets pose significant security risks as they may be unmonitored.' if status == 'stale' else 'Certificates must be monitored for expiry to prevent service disruption.'} "
            f"Environment: {environment}."
        )
    elif criticality == "high" and environment == "prod":
        risk_score = "high"
        risk_summary = (
            f"This production {asset_type} ({asset.value}) is classified as high criticality. "
            f"Production assets are directly exposed and require continuous monitoring. "
            f"Any vulnerability here could have immediate business impact."
        )
    elif environment == "dev" or criticality == "low":
        risk_score = "low"
        risk_summary = (
            f"This {asset_type} ({asset.value}) is a low-risk asset. "
            f"It is in a {environment} environment with {criticality} criticality. "
            f"Standard monitoring procedures are sufficient."
        )
    else:
        risk_score = "medium"
        risk_summary = (
            f"This {asset_type} ({asset.value}) carries moderate risk. "
            f"It is in a {environment} environment and should be reviewed periodically. "
            f"Ensure access controls and monitoring are in place."
        )

    return {
        "risk_score": risk_score,
        "risk_summary": risk_summary,
    }