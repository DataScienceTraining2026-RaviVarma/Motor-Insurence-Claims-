
from pathlib import Path
import pandas as pd


def check_file_exists(file_path):
    """Check whether the given file exists."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return True


def load_table(file_path):
    """Load a CSV file into a pandas DataFrame."""
    check_file_exists(file_path)
    return pd.read_csv(file_path)


def load_all_data(data_dir):
    """Load all five motor insurance CSV tables."""
    data_path = Path(data_dir)

    filenames = {
        "customers": "customers.csv",
        "vehicles": "vehicles.csv",
        "policies": "policies.csv",
        "claims": "claims.csv",
        "payments": "payments.csv",
    }

    data = {}

    for table_name, filename in filenames.items():
        file_path = data_path / filename
        data[table_name] = load_table(file_path)

    return data
