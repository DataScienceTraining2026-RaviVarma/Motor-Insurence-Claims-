
import pandas as pd
from pathlib import Path


# 1. Handle missing values
def handle_missing_values(data):
    """Handle missing values without changing IDs or dates."""

    cleaned_data = {}

    date_columns = {
        "date_of_birth",
        "policy_start_date",
        "policy_end_date",
        "claim_date",
        "accident_date",
        "approval_date",
        "settlement_date",
        "payment_date",
    }

    for table_name, df in data.items():
        df = df.copy()

        for column in df.columns:

            # Do not fill ID or date columns
            if column.endswith("_id") or column in date_columns:
                continue

            if df[column].isna().any():

                if pd.api.types.is_numeric_dtype(df[column]):
                    median_value = df[column].median()

                    if pd.notna(median_value):
                        df[column] = df[column].fillna(median_value)

                else:
                    df[column] = df[column].fillna("Unknown")

        cleaned_data[table_name] = df

    return cleaned_data


# 2. Remove duplicate rows
def remove_duplicates(data):
    """Remove duplicate rows from all insurance tables."""

    cleaned_data = {}

    for table_name, df in data.items():
        before_count = len(df)

        df = df.drop_duplicates().copy()

        removed_count = before_count - len(df)

        print(
            f"{table_name}: "
            f"{removed_count} duplicate rows removed"
        )

        cleaned_data[table_name] = df

    return cleaned_data


# 3. Clean text columns
def clean_text_columns(data):
    """Remove leading and trailing spaces from text columns."""

    cleaned_data = {}

    for table_name, df in data.items():
        df = df.copy()

        for column in df.select_dtypes(include=["object"]).columns:
            df[column] = df[column].apply(
                lambda value: value.strip()
                if isinstance(value, str)
                else value
            )

        cleaned_data[table_name] = df

    return cleaned_data


# 4. Convert date columns
def clean_date_columns(data):
    """Convert known date columns to datetime format."""

    date_columns = {
        "customers": ["date_of_birth"],
        "policies": ["policy_start_date", "policy_end_date"],
        "claims": [
            "claim_date",
            "accident_date",
            "approval_date",
            "settlement_date",
        ],
        "payments": ["payment_date"],
    }

    cleaned_data = {}

    for table_name, df in data.items():
        df = df.copy()

        for column in date_columns.get(table_name, []):
            if column in df.columns:
                df[column] = pd.to_datetime(
                    df[column], errors="coerce"
                )

        cleaned_data[table_name] = df

    return cleaned_data


# 5. Validate numeric columns
def validate_numeric_columns(data):
    """Convert numeric columns and report invalid values."""

    numeric_columns = {
        "customers": ["age"],
        "vehicles": ["vehicle_year", "vehicle_value"],
        "policies": ["premium_amount", "coverage_amount"],
        "claims": ["claim_amount"],
        "payments": ["payment_amount"],
    }

    cleaned_data = {}

    for table_name, df in data.items():
        df = df.copy()

        for column in numeric_columns.get(table_name, []):
            if column in df.columns:
                original = df[column]

                converted = pd.to_numeric(
                    original, errors="coerce"
                )

                invalid = original.notna() & converted.isna()

                if invalid.any():
                    print(
                        f"Warning: {table_name}.{column}: "
                        f"{invalid.sum()} invalid numeric values"
                    )

                df[column] = converted

        cleaned_data[table_name] = df

    return cleaned_data


# 6. Validate business rules
def validate_business_rules(data):
    """Report negative financial values and invalid policy dates."""

    cleaned_data = {}

    financial_columns = {
        "vehicles": ["vehicle_value"],
        "policies": ["premium_amount", "coverage_amount"],
        "claims": ["claim_amount"],
        "payments": ["payment_amount"],
    }

    for table_name, df in data.items():
        df = df.copy()

        for column in financial_columns.get(table_name, []):
            if column in df.columns:
                invalid = df[column] < 0

                if invalid.any():
                    print(
                        f"Warning: {table_name}.{column} "
                        f"contains {invalid.sum()} negative values"
                    )

        if {
            "policy_start_date",
            "policy_end_date",
        }.issubset(df.columns):

            invalid_dates = (
                df["policy_start_date"].notna()
                & df["policy_end_date"].notna()
                & (
                    df["policy_end_date"]
                    < df["policy_start_date"]
                )
            )

            if invalid_dates.any():
                print(
                    f"Warning: {invalid_dates.sum()} policies "
                    "have end dates before start dates"
                )

        cleaned_data[table_name] = df

    return cleaned_data


# 7. Create derived columns
def create_derived_columns(data):
    """Create additional columns for insurance analysis."""

    data = {
        name: df.copy()
        for name, df in data.items()
    }

    # Policy duration
    if "policies" in data:
        policies = data["policies"]

        if {
            "policy_start_date",
            "policy_end_date",
        }.issubset(policies.columns):

            policies["policy_duration_days"] = (
                policies["policy_end_date"]
                - policies["policy_start_date"]
            ).dt.days

    # Vehicle age
    if "vehicles" in data:
        vehicles = data["vehicles"]

        if "vehicle_year" in vehicles.columns:
            vehicles["vehicle_age"] = (
                pd.Timestamp.today().year
                - pd.to_numeric(
                    vehicles["vehicle_year"],
                    errors="coerce",
                )
            )

    # Claim processing and settlement durations
    if "claims" in data:
        claims = data["claims"]

        if {
            "claim_date",
            "approval_date",
        }.issubset(claims.columns):

            claims["claim_processing_days"] = (
                claims["approval_date"]
                - claims["claim_date"]
            ).dt.days

        if {
            "claim_date",
            "settlement_date",
        }.issubset(claims.columns):

            claims["claim_settlement_days"] = (
                claims["settlement_date"]
                - claims["claim_date"]
            ).dt.days

        # Add policy premium and coverage to claims
        if "policies" in data:
            policies = data["policies"]

            if {
                "policy_id",
                "premium_amount",
                "coverage_amount",
            }.issubset(policies.columns) and "policy_id" in claims.columns:

                policy_premiums = policies.drop_duplicates(
                    "policy_id"
                ).set_index("policy_id")["premium_amount"]

                policy_coverage = policies.drop_duplicates(
                    "policy_id"
                ).set_index("policy_id")["coverage_amount"]

                claims["premium_amount"] = claims["policy_id"].map(
                    policy_premiums
                )

                claims["coverage_amount"] = claims["policy_id"].map(
                    policy_coverage
                )

                claims["claim_to_premium_ratio"] = (
                    claims["claim_amount"]
                    / claims["premium_amount"].replace(0, float("nan"))
                    if "claim_amount" in claims.columns
                    else float("nan")
                )

                claims["claim_to_coverage_ratio"] = (
                    claims["claim_amount"]
                    / claims["coverage_amount"].replace(
                        0, float("nan")
                    )
                    if "claim_amount" in claims.columns
                    else float("nan")
                )

        # Add total payments for each claim
        if "payments" in data:
            payments = data["payments"]

            if {
                "claim_id",
                "payment_amount",
            }.issubset(payments.columns) and "claim_id" in claims.columns:

                total_payments = payments.groupby("claim_id")[
                    "payment_amount"
                ].sum()

                claims["total_payment_amount"] = (
                    claims["claim_id"]
                    .map(total_payments)
                    .fillna(0)
                )

                if "claim_amount" in claims.columns:
                    claims["paid_claim_ratio"] = (
                        claims["total_payment_amount"]
                        / claims["claim_amount"].replace(
                            0, float("nan")
                        )
                    )

        data["claims"] = claims

    return data


# 8. Run complete cleaning pipeline
def clean_data(data):
    """Execute all data-cleaning steps in sequence."""

    print("\nStarting data cleaning...")

    data = handle_missing_values(data)
    data = remove_duplicates(data)
    data = clean_text_columns(data)
    data = clean_date_columns(data)
    data = validate_numeric_columns(data)
    data = validate_business_rules(data)
    data = create_derived_columns(data)

    print("Data cleaning completed successfully.")

    return data


# 9. Save cleaned data
def save_cleaned_data(data, output_dir):
    """Save cleaned DataFrames as CSV files."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for table_name, df in data.items():
        file_path = output_path / f"{table_name}_cleaned.csv"

        df.to_csv(file_path, index=False)

        print(f"Saved: {file_path}")
