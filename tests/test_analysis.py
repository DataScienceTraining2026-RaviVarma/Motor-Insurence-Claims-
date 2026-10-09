import pandas as pd

from src.insurance_analysis import (
    calculate_total_customers,
    calculate_total_policies,
    calculate_total_premium,
    calculate_total_claims,
    calculate_total_claim_amount,
    calculate_claim_approval_rate,
)


def sample_data():
    return {
        "customers": pd.DataFrame({
            "customer_id": [1, 2, 2]
        }),
        "policies": pd.DataFrame({
            "policy_id": [101, 102],
            "policy_status": ["Active", "Expired"],
            "premium_amount": [1000, 2000],
        }),
        "claims": pd.DataFrame({
            "claim_id": [201, 202],
            "claim_amount": [500, 1500],
            "claim_status": ["Approved", "Rejected"],
        }),
        "payments": pd.DataFrame({
            "payment_amount": [500, 1000]
        }),
    }


def test_total_customers():
    assert calculate_total_customers(sample_data()) == 2


def test_total_policies():
    assert calculate_total_policies(sample_data()) == 2


def test_total_premium():
    assert calculate_total_premium(sample_data()) == 3000.0


def test_total_claims():
    assert calculate_total_claims(sample_data()) == 2


def test_total_claim_amount():
    assert calculate_total_claim_amount(sample_data()) == 2000.0


def test_claim_approval_rate():
    assert calculate_claim_approval_rate(sample_data()) == 50.0