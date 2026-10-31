import os
import requests
from dotenv import load_dotenv

load_dotenv()
crust_key = os.getenv("CRUSTDATA_API_KEY")

HEADERS = {
    "authorization": f"Bearer {crust_key}",
    "x-api-version": "2025-11-01",
    "content-type": "application/json"
}


def fetch_company_data(domain):
    url = "https://api.crustdata.com/company/search"
    payload = {
        "filters": {
            "field": "basic_info.primary_domain",
            "type": "=",
            "value": domain.lower().strip()
        },
        "sorts": [{"field": "headcount.total", "order": "desc"}],
        "limit": 1,
        "fields": [
            "basic_info.name",
            "basic_info.description",
            "headcount.total",
            "funding.total_investment_usd"
        ]
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get('companies', [])
        if data:
            return data[0]
    return None


def analyze_company_footprint(domain):
    """
    Autonomous footprint analysis. No manual claims needed.
    """
    company_data = fetch_company_data(domain)

    if not company_data:
        return {
            "error": True,
            "message": f"Zero digital footprint found for '{domain}'. High risk of being a synthetic or unregistered entity."
        }

    name = company_data.get('basic_info', {}).get('name', domain)
    desc = company_data.get('basic_info', {}).get(
        'description') or "No description available."
    headcount = company_data.get('headcount', {}).get('total') or 0
    funding = company_data.get('funding', {}).get('total_investment_usd') or 0

    risk_score = 0
    flags = []

    # 1. Ghost Entity Check
    if headcount == 0:
        risk_score += 60
        flags.append(
            "Ghost Entity: Zero verified employees on professional networks.")
    elif headcount < 5 and funding > 5000000:
        # 2. Shell Company Check (Massive funding, nobody working there)
        risk_score += 80
        flags.append(
            f"Shell Risk: Massive capital (${funding:,}) deployed to a micro-team ({headcount} people).")

    # 3. Capital Efficiency / Bootstrap Check
    if funding == 0 and headcount > 500:
        flags.append(
            f"Bootstrap Anomaly: Large workforce ({headcount}) but zero institutional capital footprint.")

    # 4. Burn Rate / Capital per Employee Metric
    capital_per_head = (funding / headcount) if headcount > 0 else 0
    if capital_per_head > 5000000:
        risk_score += 30
        flags.append(
            f"Hyper-Capitalized: Exceptional capital-to-employee ratio (${capital_per_head:,.0f} per head).")

    return {
        "error": False,
        "company_name": name,
        "domain": domain,
        "headcount": headcount,
        "funding": funding,
        "capital_per_employee": capital_per_head,
        "risk_score_out_of_100": min(risk_score, 100),
        "algorithmic_flags": flags,
        # Truncated for the LLM prompt
        "description_snippet": desc[:400] + "..."
    }
