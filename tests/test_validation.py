import pandas as pd
import pytest

from src.validation import (
    validate_customers,
    validate_vehicles,
    validate_policies,
    validate_claims,
    validate_payments,
)


def test_validate_customers_success():
    df = pd.DataFrame({
        "customer_id": [1],
        "customer_name": ["Ravi"],
        "gender": ["Male"],
        "date_of_birth": ["2000-01-01"],
        "age": [26],
        "city": ["Hyderabad"],
        "state": ["Telangana"],
        "occupation": ["Engineer"],
    })
    assert validate_customers(df) is True


def test_validate_customers_duplicate_id():
    df = pd.DataFrame({
        "customer_id": [1, 1],
        "customer_name": ["Ravi", "Sita"],
        "gender": ["Male", "Female"],
        "date_of_birth": ["2000-01-01", "2001-01-01"],
        "age": [26, 25],
        "city": ["Hyderabad", "Vijayawada"],
        "state": ["Telangana", "Andhra Pradesh"],
        "occupation": ["Engineer", "Teacher"],
    })
    with pytest.raises(ValueError):
        validate_customers(df)


def test_validate_vehicles_missing_columns():
    df = pd.DataFrame({"vehicle_id": [1]})
    with pytest.raises(ValueError):
        validate_vehicles(df)


def test_validate_policies_negative_premium():
    df = pd.DataFrame({
        "policy_id": [1],
        "customer_id": [1],
        "vehicle_id": [1],
        "policy_start_date": ["2026-01-01"],
        "policy_end_date": ["2027-01-01"],
        "policy_type": ["Comprehensive"],
        "premium_amount": [-100],
        "coverage_amount": [10000],
        "policy_status": ["Active"],
        "payment_frequency": ["Annual"],
    })
    with pytest.raises(ValueError):
        validate_policies(df)


def test_validate_claims_negative_amount():
    df = pd.DataFrame({
        "claim_id": [1],
        "policy_id": [1],
        "customer_id": [1],
        "claim_date": ["2026-01-05"],
        "accident_date": ["2026-01-04"],
        "claim_type": ["Accident"],
        "accident_location": ["Hyderabad"],
        "claim_amount": [-500],
        "claim_status": ["Pending"],
        "approval_date": [None],
        "settlement_date": [None],
        "damage_severity": ["Minor"],
    })
    with pytest.raises(ValueError):
        validate_claims(df)


def test_validate_payments_negative_amount():
    df = pd.DataFrame({
        "payment_id": [1],
        "claim_id": [1],
        "policy_id": [1],
        "payment_date": ["2026-01-10"],
        "payment_amount": [-200],
        "payment_status": ["Paid"],
        "payment_method": ["Bank Transfer"],
    })
    with pytest.raises(ValueError):
        validate_payments(df)