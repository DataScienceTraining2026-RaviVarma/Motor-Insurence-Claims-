
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Insure Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
CLEAN_DIR = ROOT_DIR / "data" / "cleaned"

TABLES = [
    "customers",
    "policies",
    "vehicles",
    "claims",
    "payments",
]

PALETTE = px.colors.qualitative.Bold


# ==================================================
# CUSTOM CSS
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background: #f4f7fb;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 2px;
    }

    .sub-title {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .metric-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e5eaf2;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
        min-height: 115px;
    }

    .metric-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 800;
        color: #111827;
        margin-top: 9px;
        overflow-wrap: anywhere;
    }

    .section-title {
        color: #111827;
        font-size: 22px;
        font-weight: 750;
        margin-top: 15px;
    }

    div[data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 12px;
        padding: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# LOAD CSV FILES
# ==================================================
@st.cache_data
def load_table(table_name, cleaned_exists, raw_exists):
    if cleaned_exists:
        return pd.read_csv(CLEAN_DIR / f"{table_name}_cleaned.csv")

    if raw_exists:
        return pd.read_csv(RAW_DIR / f"{table_name}.csv")

    return pd.DataFrame()


def load_all_tables():
    result = {}

    for name in TABLES:
        cleaned_file = CLEAN_DIR / f"{name}_cleaned.csv"
        raw_file = RAW_DIR / f"{name}.csv"

        result[name] = load_table(
            name,
            cleaned_file.exists(),
            raw_file.exists(),
        )

    return result


data = load_all_tables()


# ==================================================
# HELPER FUNCTIONS
# ==================================================
def find_column(df, candidates):
    """Find a matching existing column without renaming it."""
    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        actual = lookup.get(candidate.lower())

        if actual is not None:
            return actual

    return None


def numeric_series(df, column):
    if column is None or column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(df[column], errors="coerce")


def money(value):
    return f"₹{value:,.2f}"


def metric_card(label, value, accent):
    st.markdown(
        f"""
        <div class="metric-card"
             style="border-top: 4px solid {accent};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", color="#334155"),
        margin=dict(l=20, r=20, t=60, b=30),
        title_font_size=17,
        legend_title_text="Category",
    )
    st.plotly_chart(fig, use_container_width=True)


def category_bar(df, category, title, value_label="Records"):
    if df.empty or category is None:
        st.info(f"Data unavailable for {title}.")
        return

    chart = df[category].fillna("Unknown").astype(str)
    chart = chart.value_counts().head(15).reset_index()
    chart.columns = [category, value_label]

    fig = px.bar(
        chart,
        x=category,
        y=value_label,
        color=category,
        color_discrete_sequence=PALETTE,
        title=title,
        hover_data={value_label: True},
    )

    fig.update_layout(showlegend=False)
    show_chart(fig)


def numeric_by_category(df, category, amount, title, y_label):
    if (
        df.empty
        or category is None
        or amount is None
    ):
        st.info(f"Required columns unavailable for {title}.")
        return

    chart = df[[category, amount]].copy()
    chart[amount] = pd.to_numeric(
        chart[amount], errors="coerce"
    )
    chart[category] = chart[category].fillna("Unknown").astype(str)
    chart = chart.dropna(subset=[amount])

    if chart.empty:
        st.info(f"No numeric values available for {title}.")
        return

    chart = (
        chart.groupby(category, as_index=False)[amount]
        .sum()
        .sort_values(amount, ascending=False)
        .head(15)
    )

    fig = px.bar(
        chart,
        x=category,
        y=amount,
        color=category,
        title=title,
        labels={amount: y_label},
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(showlegend=False)
    show_chart(fig)


def show_pie(df, category, title):
    if df.empty or category is None:
        st.info(f"Data unavailable for {title}.")
        return

    chart = (
        df[category]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .reset_index()
    )
    chart.columns = [category, "Count"]

    fig = px.pie(
        chart,
        names=category,
        values="Count",
        title=title,
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    show_chart(fig)


def show_data_preview(df, table_name):
    st.subheader(f"{table_name.title()} data")

    if df.empty:
        st.warning("No data available for this table.")
        return

    st.caption(
        f"{len(df):,} rows | {len(df.columns)} columns"
    )
    st.dataframe(df.head(500), use_container_width=True)


# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("🚗 INSURE ANALYTICS")
st.sidebar.caption("Motor Insurance Intelligence")
st.sidebar.divider()

available_tables = [
    name for name, df in data.items()
    if not df.empty
]

if not available_tables:
    st.error(
        "No CSV datasets found. Check data/raw or data/cleaned."
    )
    st.stop()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Policy Analytics",
        "Claims Analytics",
        "Customer Analytics",
        "Vehicle Analytics",
        "Payments Analytics",
        "Data Explorer",
    ],
)

st.sidebar.divider()
st.sidebar.subheader("Dashboard Filters")

policies = data["policies"].copy()
claims = data["claims"].copy()
customers = data["customers"].copy()
vehicles = data["vehicles"].copy()
payments = data["payments"].copy()

policy_status_col = find_column(
    policies, ["policy_status", "status"]
)
policy_type_col = find_column(
    policies, ["policy_type", "insurance_type"]
)
claim_status_col = find_column(
    claims, ["claim_status", "status"]
)
claim_type_col = find_column(
    claims, ["claim_type"]
)

if policy_status_col:
    options = sorted(
        policies[policy_status_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    selected_status = st.sidebar.multiselect(
        "Policy Status",
        options,
        default=options,
    )
    policies = policies[
        policies[policy_status_col].fillna("").astype(str).isin(
            selected_status
        )
    ]

if policy_type_col:
    options = sorted(
        data["policies"][policy_type_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    selected_types = st.sidebar.multiselect(
        "Policy Type",
        options,
        default=options,
    )
    policies = policies[
        policies[policy_type_col].fillna("").astype(str).isin(
            selected_types
        )
    ]

if claim_status_col:
    options = sorted(
        claims[claim_status_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    selected_claim_status = st.sidebar.multiselect(
        "Claim Status",
        options,
        default=options,
    )
    claims = claims[
        claims[claim_status_col].fillna("").astype(str).isin(
            selected_claim_status
        )
    ]

if claim_type_col:
    options = sorted(
        claims[claim_type_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    selected_claim_types = st.sidebar.multiselect(
        "Claim Type",
        options,
        default=options,
    )
    claims = claims[
        claims[claim_type_col].fillna("").astype(str).isin(
            selected_claim_types
        )
    ]

if st.sidebar.button("Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# ==================================================
# HEADER
# ==================================================
st.markdown(
    '<div class="main-title">Motor Insurance Analytics</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">'
    'Policy performance • Claims intelligence • Customer insights'
    '</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Charts reflect available data and the selected filters. "
    "Premium and claim totals are calculated from the loaded CSVs."
)


# ==================================================
# EXECUTIVE OVERVIEW
# ==================================================
if page == "Executive Overview":
    premium_col = find_column(
        policies, ["premium_amount", "premium", "total_premium"]
    )
    claim_amount_col = find_column(
        claims, ["claim_amount", "claimed_amount", "amount"]
    )
    customer_id_col = find_column(
        customers, ["customer_id"]
    )
    policy_id_col = find_column(
        policies, ["policy_id"]
    )
    claim_id_col = find_column(
        claims, ["claim_id"]
    )

    total_customers = (
        customers[customer_id_col].nunique()
        if customer_id_col else len(customers)
    )
    total_policies = (
        policies[policy_id_col].nunique()
        if policy_id_col else len(policies)
    )
    total_claims = (
        claims[claim_id_col].nunique()
        if claim_id_col else len(claims)
    )
    total_premium = numeric_series(
        policies, premium_col
    ).sum()
    total_claim_amount = numeric_series(
        claims, claim_amount_col
    ).sum()

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        metric_card("Customers", f"{total_customers:,}", "#3B82F6")
    with k2:
        metric_card("Policies", f"{total_policies:,}", "#10B981")
    with k3:
        metric_card("Total Premium", money(total_premium), "#8B5CF6")
    with k4:
        metric_card("Claims", f"{total_claims:,}", "#F59E0B")
    with k5:
        metric_card(
            "Claim Amount",
            money(total_claim_amount),
            "#EF4444",
        )

    st.markdown(
        '<div class="section-title">Performance Overview</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        category_bar(
            policies,
            policy_status_col,
            "Policies by Status",
            "Number of Policies",
        )

    with right:
        numeric_by_category(
            policies,
            policy_type_col,
            premium_col,
            "Premium by Policy Type",
            "Premium Amount",
        )

    left, right = st.columns(2)

    with left:
        show_pie(
            claims,
            claim_status_col,
            "Claims Status Distribution",
        )

    with right:
        numeric_by_category(
            claims,
            claim_type_col,
            claim_amount_col,
            "Claim Amount by Type",
            "Claim Amount",
        )

    st.markdown("### Quick Data Summary")

    summary = pd.DataFrame({
        "Dataset": TABLES,
        "Rows": [len(data[name]) for name in TABLES],
        "Columns": [
            len(data[name].columns) for name in TABLES
        ],
    })

    st.dataframe(summary, use_container_width=True, hide_index=True)


# ==================================================
# POLICY ANALYTICS
# ==================================================
elif page == "Policy Analytics":
    premium_col = find_column(
        policies, ["premium_amount", "premium", "total_premium"]
    )
    coverage_col = find_column(
        policies, ["coverage_amount", "coverage", "sum_insured"]
    )

    k1, k2, k3 = st.columns(3)

    with k1:
        metric_card("Policies", f"{len(policies):,}", "#3B82F6")
    with k2:
        metric_card(
            "Premium",
            money(numeric_series(policies, premium_col).sum()),
            "#10B981",
        )
    with k3:
        metric_card(
            "Coverage",
            money(numeric_series(policies, coverage_col).sum()),
            "#8B5CF6",
        )

    left, right = st.columns(2)

    with left:
        category_bar(
            policies, policy_status_col, "Policy Status Distribution"
        )

    with right:
        numeric_by_category(
            policies,
            policy_type_col,
            premium_col,
            "Premium by Policy Type",
            "Premium Amount",
        )

    if premium_col and coverage_col:
        chart = policies[[premium_col, coverage_col]].copy()
        chart[premium_col] = pd.to_numeric(
            chart[premium_col], errors="coerce"
        )
        chart[coverage_col] = pd.to_numeric(
            chart[coverage_col], errors="coerce"
        )
        chart = chart.dropna()

        if not chart.empty:
            fig = px.scatter(
                chart,
                x=premium_col,
                y=coverage_col,
                title="Premium vs Coverage",
                color_discrete_sequence=PALETTE,
                opacity=0.7,
            )
            show_chart(fig)


# ==================================================
# CLAIMS ANALYTICS
# ==================================================
elif page == "Claims Analytics":
    claim_amount_col = find_column(
        claims, ["claim_amount", "claimed_amount", "amount"]
    )
    settlement_col = find_column(
        claims, ["settlement_date"]
    )
    claim_date_col = find_column(
        claims, ["claim_date"]
    )

    k1, k2, k3 = st.columns(3)

    with k1:
        metric_card("Claims", f"{len(claims):,}", "#F59E0B")

    with k2:
        metric_card(
            "Claim Amount",
            money(numeric_series(claims, claim_amount_col).sum()),
            "#EF4444",
        )

    with k3:
        settled = (
            claims[settlement_col].notna().sum()
            if settlement_col else 0
        )
        metric_card("With Settlement Date", f"{settled:,}", "#10B981")

    left, right = st.columns(2)

    with left:
        show_pie(claims, claim_status_col, "Claim Status")

    with right:
        numeric_by_category(
            claims,
            claim_type_col,
            claim_amount_col,
            "Claim Amount by Type",
            "Claim Amount",
        )

    if claim_date_col and claim_amount_col:
        trend = claims[[claim_date_col, claim_amount_col]].copy()
        trend[claim_date_col] = pd.to_datetime(
            trend[claim_date_col], errors="coerce"
        )
        trend[claim_amount_col] = pd.to_numeric(
            trend[claim_amount_col], errors="coerce"
        )
        trend = trend.dropna()

        if not trend.empty:
            trend["Month"] = (
                trend[claim_date_col]
                .dt.to_period("M")
                .astype(str)
            )
            trend = trend.groupby(
                "Month", as_index=False
            )[claim_amount_col].sum()

            fig = px.line(
                trend,
                x="Month",
                y=claim_amount_col,
                title="Monthly Claim Amount",
                markers=True,
                color_discrete_sequence=["#8B5CF6"],
            )
            show_chart(fig)


# ==================================================
# CUSTOMER ANALYTICS
# ==================================================
elif page == "Customer Analytics":
    customer_category = find_column(
        customers,
        ["city", "state", "occupation", "gender"],
    )
    age_col = find_column(customers, ["age"])

    k1, k2 = st.columns(2)

    with k1:
        metric_card(
            "Customers",
            f"{customers[find_column(customers, ['customer_id'])].nunique():,}"
            if find_column(customers, ["customer_id"])
            else f"{len(customers):,}",
            "#3B82F6",
        )

    with k2:
        metric_card(
            "Customer Columns",
            f"{len(customers.columns):,}",
            "#10B981",
        )

    category_bar(
        customers,
        customer_category,
        f"Customers by {customer_category}" if customer_category else
        "Customer Distribution",
        "Number of Customers",
    )

    if age_col:
        age_data = customers.copy()
        age_data[age_col] = pd.to_numeric(
            age_data[age_col], errors="coerce"
        )
        age_data = age_data.dropna(subset=[age_col])

        if not age_data.empty:
            fig = px.histogram(
                age_data,
                x=age_col,
                nbins=20,
                title="Customer Age Distribution",
                color_discrete_sequence=["#06B6D4"],
            )
            show_chart(fig)


# ==================================================
# VEHICLE ANALYTICS
# ==================================================
elif page == "Vehicle Analytics":
    vehicle_category = find_column(
        vehicles,
        ["vehicle_type", "vehicle_category", "vehicle_make", "fuel_type"],
    )
    vehicle_value_col = find_column(
        vehicles, ["vehicle_value", "market_value"]
    )

    k1, k2 = st.columns(2)

    with k1:
        metric_card("Vehicles", f"{len(vehicles):,}", "#3B82F6")

    with k2:
        metric_card(
            "Vehicle Value",
            money(numeric_series(vehicles, vehicle_value_col).sum()),
            "#10B981",
        )

    category_bar(
        vehicles,
        vehicle_category,
        "Vehicles by Category",
        "Vehicle Count",
    )

    year_col = find_column(vehicles, ["vehicle_year", "year"])

    if year_col:
        year_data = vehicles.copy()
        year_data[year_col] = pd.to_numeric(
            year_data[year_col], errors="coerce"
        )
        year_data = year_data.dropna(subset=[year_col])

        if not year_data.empty:
            year_counts = (
                year_data[year_col]
                .value_counts()
                .sort_index()
                .reset_index()
            )
            year_counts.columns = [year_col, "Vehicle Count"]

            fig = px.bar(
                year_counts,
                x=year_col,
                y="Vehicle Count",
                title="Vehicles by Manufacturing Year",
                color="Vehicle Count",
                color_continuous_scale="Viridis",
            )
            show_chart(fig)


# ==================================================
# PAYMENTS ANALYTICS
# ==================================================
elif page == "Payments Analytics":
    payment_amount_col = find_column(
        payments, ["payment_amount", "amount", "paid_amount"]
    )
    payment_status_col = find_column(
        payments, ["payment_status", "status"]
    )
    payment_method_col = find_column(
        payments, ["payment_method", "method"]
    )

    k1, k2 = st.columns(2)

    with k1:
        metric_card("Payment Records", f"{len(payments):,}", "#8B5CF6")

    with k2:
        metric_card(
            "Payment Amount",
            money(numeric_series(payments, payment_amount_col).sum()),
            "#10B981",
        )

    left, right = st.columns(2)

    with left:
        category_bar(
            payments, payment_status_col, "Payments by Status"
        )

    with right:
        numeric_by_category(
            payments,
            payment_method_col,
            payment_amount_col,
            "Payment Amount by Method",
            "Payment Amount",
        )


# ==================================================
# DATA EXPLORER
# ==================================================
elif page == "Data Explorer":
    selected_table = st.selectbox(
        "Select dataset",
        available_tables,
    )

    show_data_preview(
        data[selected_table],
        selected_table,
    )

    st.download_button(
        "Download displayed dataset",
        data=data[selected_table].to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_table}_export.csv",
        mime="text/csv",
    )


# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(
    "Motor Insurance Analytics | Built with Python, "
    "Pandas, Plotly and Streamlit"
)
