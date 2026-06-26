import json
from langchain.prompts import ChatPromptTemplate
from app.langchain_layer.query_engine import get_llm


REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are a cybersecurity expert generating an Attack Surface Management report.

Given a list of assets with their risk assessments, generate a clear professional report with these sections:

1. Executive Summary (2-3 sentences overview)
2. Risk Overview (counts of high/medium/low risk assets)
3. High Risk Assets (list each one with why it's risky)
4. Assets by Environment (prod/staging/dev breakdown)
5. Recommendations (3-5 actionable items)

Write in plain English. Be specific about asset names and risks.
Do not add any JSON or code blocks — just clean readable text.
"""),
    ("human", """
Generate a security report for these assets:

{assets_data}
""")
])


def format_assets_for_report(assets) -> str:
    lines = []
    for a in assets:
        asset_type = a.type.value if hasattr(a.type, 'value') else a.type
        status = a.status.value if hasattr(a.status, 'value') else a.status
        lines.append(
            f"- [{asset_type}] {a.value} | "
            f"status: {status} | "
            f"environment: {a.environment or 'unknown'} | "
            f"criticality: {a.criticality or 'unknown'} | "
            f"risk: {a.risk_score or 'not assessed'} | "
            f"summary: {a.risk_summary or 'N/A'}"
        )
    return "\n".join(lines)


async def generate_report(assets) -> dict:
    llm = get_llm()
    chain = REPORT_PROMPT | llm

    assets_text = format_assets_for_report(assets)

    response = await chain.ainvoke({"assets_data": assets_text})

    return {
        "report": response.content.strip(),
        "assets_count": len(assets),
    }


def generate_report_mock(assets) -> dict:
    high = [a for a in assets if a.risk_score == "high"]
    medium = [a for a in assets if a.risk_score == "medium"]
    low = [a for a in assets if a.risk_score == "low"]
    not_assessed = [a for a in assets if not a.risk_score]

    prod_assets = [a for a in assets if a.environment == "prod"]
    dev_assets = [a for a in assets if a.environment == "dev"]
    staging_assets = [a for a in assets if a.environment == "staging"]
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("ATTACK SURFACE MANAGEMENT REPORT")
    report_lines.append("=" * 60)
    report_lines.append("")
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 40)
    report_lines.append(
        f"A total of {len(assets)} assets were analyzed across the organization's attack surface. "
        f"Of these, {len(high)} assets were identified as high risk, {len(medium)} as medium risk, "
        f"and {len(low)} as low risk. Immediate attention is required for high risk assets."
    )
    report_lines.append("")

    # Risk Overview
    report_lines.append("RISK OVERVIEW")
    report_lines.append("-" * 40)
    report_lines.append(f"  High Risk   : {len(high)} assets")
    report_lines.append(f"  Medium Risk : {len(medium)} assets")
    report_lines.append(f"  Low Risk    : {len(low)} assets")
    if not_assessed:
        report_lines.append(f"  Not Assessed: {len(not_assessed)} assets")
    report_lines.append("")

    # High Risk Assets
    if high:
        report_lines.append("HIGH RISK ASSETS")
        report_lines.append("-" * 40)
        for a in high:
            asset_type = a.type.value if hasattr(a.type, 'value') else a.type
            report_lines.append(f"  * {a.value} [{asset_type}]")
            if a.risk_summary:
                report_lines.append(f"    → {a.risk_summary}")
        report_lines.append("")

    # Assets by Environment
    report_lines.append("ASSETS BY ENVIRONMENT")
    report_lines.append("-" * 40)
    report_lines.append(f"  Production : {len(prod_assets)} assets")
    for a in prod_assets:
        report_lines.append(f"    - {a.value} (risk: {a.risk_score or 'N/A'})")
    report_lines.append(f"  Staging    : {len(staging_assets)} assets")
    for a in staging_assets:
        report_lines.append(f"    - {a.value} (risk: {a.risk_score or 'N/A'})")
    report_lines.append(f"  Dev        : {len(dev_assets)} assets")
    for a in dev_assets:
        report_lines.append(f"    - {a.value} (risk: {a.risk_score or 'N/A'})")
    report_lines.append("")

    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-" * 40)
    if high:
        report_lines.append(f"  1. Immediately review {len(high)} high risk assets, especially certificates and production domains.")
    if not_assessed:
        report_lines.append(f"  2. Run risk assessment on {len(not_assessed)} unassessed assets.")
    if staging_assets:
        report_lines.append(f"  3. Verify that {len(staging_assets)} staging assets are not publicly accessible.")
    report_lines.append("  4. Schedule regular asset reviews every 30 days.")
    report_lines.append("  5. Enable automated alerts for any new assets discovered in production.")
    report_lines.append("")
    report_lines.append("=" * 60)

    return {
        "report": "\n".join(report_lines),
        "assets_count": len(assets),
        "stats": {
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
            "not_assessed": len(not_assessed),
        }
    }