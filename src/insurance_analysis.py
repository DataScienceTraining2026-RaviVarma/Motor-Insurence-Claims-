"""Summary metrics for motor insurance tables."""


def calculate_total_customers(data):
    """Return the number of distinct customers."""
    return int(data["customers"]["customer_id"].nunique())


def calculate_total_policies(data):
    """Return the number of policies."""
    return int(data["policies"]["policy_id"].nunique())


def calculate_total_premium(data):
    """Return the sum of policy premiums."""
    return float(data["policies"]["premium_amount"].sum())


def calculate_total_claims(data):
    """Return the number of claims."""
    return int(data["claims"]["claim_id"].nunique())


def calculate_total_claim_amount(data):
    """Return the sum of claim amounts."""
    return float(data["claims"]["claim_amount"].sum())


def calculate_claim_approval_rate(data):
    """Return the share of claims approved or settled, as a percentage."""
    claim_status = data["claims"]["claim_status"].astype("string").str.lower()
    if claim_status.empty:
        return 0.0

    approved = claim_status.isin(["approved", "settled"])
    return float(approved.mean() * 100)