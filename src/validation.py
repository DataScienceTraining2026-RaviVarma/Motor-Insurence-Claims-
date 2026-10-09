

import pandas as pd


def validate_customers(df):
    """Validate the customers table."""
    required_columns = [
        "customer_id",
        "customer_name",
        "gender",
        "date_of_birth",
        "age",
        "city",
        "state",
        "occupation",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Customers table missing columns: {missing_columns}"
        )

    if df["customer_id"].isna().any():
        raise ValueError("customer_id contains missing values")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer_id values found")

    return True


def validate_vehicles(df):
    """Validate the vehicles table."""
    required_columns = [
        "vehicle_id",
        "customer_id",
        "vehicle_type",
        "vehicle_make",
        "vehicle_model",
        "vehicle_year",
        "fuel_type",
        "vehicle_value",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Vehicles table missing columns: {missing_columns}"
        )

    if df["vehicle_id"].isna().any():
        raise ValueError("vehicle_id contains missing values")

    if df["vehicle_id"].duplicated().any():
        raise ValueError("Duplicate vehicle_id values found")

    return True


def validate_policies(df):
    """Validate the policies table."""
    required_columns = [
        "policy_id",
        "customer_id",
        "vehicle_id",
        "policy_start_date",
        "policy_end_date",
        "policy_type",
        "premium_amount",
        "coverage_amount",
        "policy_status",
        "payment_frequency",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Policies table missing columns: {missing_columns}"
        )

    if df["policy_id"].isna().any():
        raise ValueError("policy_id contains missing values")

    if df["policy_id"].duplicated().any():
        raise ValueError("Duplicate policy_id values found")

    if (df["premium_amount"].dropna() < 0).any():
        raise ValueError("Negative premium_amount values found")

    if (df["coverage_amount"].dropna() < 0).any():
        raise ValueError("Negative coverage_amount values found")

    return True

def validate_claims(df):
    """Validate the claims table."""
    required_columns = [
        "claim_id",
        "policy_id",
        "customer_id",
        "claim_date",
        "accident_date",
        "claim_type",
        "accident_location",
        "claim_amount",
        "claim_status",
        "approval_date",
        "settlement_date",
        "damage_severity",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Claims table missing columns: {missing_columns}"
        )

    if df["claim_id"].isna().any():
        raise ValueError("claim_id contains missing values")

    if df["claim_id"].duplicated().any():
        raise ValueError("Duplicate claim_id values found")

    if (df["claim_amount"].dropna() < 0).any():
        raise ValueError("Negative claim_amount values found")

    return True


def validate_relationships(data):
    """Validate relationships between insurance tables."""

    customers = data["customers"]
    vehicles = data["vehicles"]
    policies = data["policies"]
    claims = data["claims"]
    payments = data["payments"]

    customer_ids = set(customers["customer_id"].dropna())
    vehicle_ids = set(vehicles["vehicle_id"].dropna())
    policy_ids = set(policies["policy_id"].dropna())
    claim_ids = set(claims["claim_id"].dropna())

    if not vehicles["customer_id"].dropna().isin(customer_ids).all():
        raise ValueError(
            "Vehicles contain unknown customer_id values"
        )

    if not policies["customer_id"].dropna().isin(customer_ids).all():
        raise ValueError(
            "Policies contain unknown customer_id values"
        )

    if not policies["vehicle_id"].dropna().isin(vehicle_ids).all():
        raise ValueError(
            "Policies contain unknown vehicle_id values"
        )

    if not claims["policy_id"].dropna().isin(policy_ids).all():
        raise ValueError(
            "Claims contain unknown policy_id values"
        )

    if not payments["claim_id"].dropna().isin(claim_ids).all():
        raise ValueError(
            "Payments contain unknown claim_id values"
        )

    if not payments["policy_id"].dropna().isin(policy_ids).all():
        raise ValueError(
            "Payments contain unknown policy_id values"
        )

    return True


def validate_all_tables(data):
    """Validate all insurance tables and their relationships."""

    validate_customers(data["customers"])
    validate_vehicles(data["vehicles"])
    validate_policies(data["policies"])
    validate_claims(data["claims"])
    validate_payments(data["payments"])

    validate_relationships(data)

    return True


import pandas as pd


def handle_missing_values(data):
    """Handle missing values in the insurance tables."""

    cleaned_data = {}

    for table_name, df in data.items():
        df = df.copy()

        print(f"\nMissing values in {table_name}:")

        missing_counts = df.isnull().sum()
        print(missing_counts[missing_counts > 0])

        for column in df.columns:
            if df[column].isnull().any():

                if pd.api.types.is_object_dtype(df[column]):
                    df[column] = df[column].fillna("Unknown")

                elif pd.api.types.is_numeric_dtype(df[column]):
                    median_value = df[column].median()

                    if pd.notna(median_value):
                        df[column] = df[column].fillna(median_value)

        cleaned_data[table_name] = df

    return cleaned_data

def validate_payments(df):
    required_columns = [
        "payment_id",
        "claim_id",
        "policy_id",
        "payment_amount",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df["payment_id"].isna().any():
        raise ValueError("payment_id contains missing values")

    if df["payment_id"].duplicated().any():
        raise ValueError("Duplicate payment_id found")

    if (df["payment_amount"].dropna() < 0).any():
        raise ValueError("Negative payment amount found")

    return True
