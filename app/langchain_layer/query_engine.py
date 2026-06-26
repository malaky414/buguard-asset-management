import json
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings


def get_llm():
    if settings.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0,
        )
    return ChatOpenAI(
        model="gpt-4o",
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )

QUERY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are an assistant that converts natural language queries about cybersecurity assets into structured JSON filters.

Available asset types: domain, subdomain, ip_address, service, certificate, technology
Available statuses: active, stale, archived
Available criticality: high, medium, low
Available environments: prod, staging, dev

Return ONLY a JSON object with these optional fields:
{{
  "type": "asset type or null",
  "status": "status or null",
  "criticality": "criticality or null",
  "environment": "environment or null",
  "value_contains": "search term in value or null",
  "tag": "tag to filter by or null"
}}

Rules:
- expired = status stale
- Return null for fields not mentioned
- Return ONLY the JSON, no explanation
"""),
    ("human", "{query}")
])


async def parse_query(user_query: str) -> dict:
    query_lower = user_query.lower()
    filters = {}

    # Type detection
    if "certificate" in query_lower:
        filters["type"] = "certificate"
    elif "domain" in query_lower:
        filters["type"] = "domain"
    elif "subdomain" in query_lower:
        filters["type"] = "subdomain"
    elif "ip" in query_lower:
        filters["type"] = "ip_address"
    elif "service" in query_lower:
        filters["type"] = "service"

    # Status detection
    if "expired" in query_lower or "stale" in query_lower:
        filters["status"] = "stale"
    elif "active" in query_lower:
        filters["status"] = "active"
    elif "archived" in query_lower:
        filters["status"] = "archived"

    # Criticality detection
    if "high" in query_lower:
        filters["criticality"] = "high"
    elif "medium" in query_lower:
        filters["criticality"] = "medium"
    elif "low" in query_lower:
        filters["criticality"] = "low"

    # Environment detection
    if "prod" in query_lower:
        filters["environment"] = "prod"
    elif "staging" in query_lower:
        filters["environment"] = "staging"
    elif "dev" in query_lower:
        filters["environment"] = "dev"

    return filters