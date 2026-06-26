import json
from langchain.prompts import ChatPromptTemplate
from app.langchain_layer.query_engine import get_llm


ENRICHMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are a cybersecurity expert analyzing digital assets for an Attack Surface Management system.

Given an asset, classify it and return ONLY a JSON object with these fields:
{{
  "environment": "prod or staging or dev or unknown",
  "criticality": "high or medium or low",
  "category": "one of: web, api, infrastructure, security, database, email, cdn, other"
}}

Rules for environment:
- Contains "prod" or "www" or no env keyword → prod
- Contains "staging", "stg", "uat" → staging  
- Contains "dev", "test", "local" → dev
- Not clear → unknown

Rules for criticality:
- certificate, ip_address, or prod domain → high
- subdomain or service → medium
- technology or dev/staging asset → low

Return ONLY the JSON, no explanation.
"""),
    ("human", """
Asset details:
- Type: {type}
- Value: {value}
- Tags: {tags}
- Metadata: {metadata}
""")
])


async def enrich_asset(asset) -> dict:

    value = asset.value.lower()
    asset_type = asset.type.value if hasattr(asset.type, 'value') else asset.type

    # Environment
    if any(x in value for x in ["dev.", "test.", "local.", "staging.", "stg."]):
        environment = "dev" if "dev" in value else "staging"
    elif any(x in value for x in ["prod.", "www.", "app."]):
        environment = "prod"
    else:
        environment = "prod"  # default

    # Criticality
    if asset_type in ["certificate", "ip_address"]:
        criticality = "high"
    elif asset_type in ["domain"] or environment == "prod":
        criticality = "high"
    elif asset_type in ["subdomain", "service"]:
        criticality = "medium"
    else:
        criticality = "low"

    # Category
    category_map = {
        "certificate": "security",
        "domain": "web",
        "subdomain": "web",
        "ip_address": "infrastructure",
        "service": "api",
        "technology": "other",
    }
    category = category_map.get(asset_type, "other")

    return {
        "environment": environment,
        "criticality": criticality,
        "category": category,
    }