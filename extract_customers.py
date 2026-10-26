"""
Day 1 - API Data Extraction and Transformation
Squad Python Specialization - Data Engineering

Fill in every function. Keep the signatures; you may add helpers of your own.
"""
import csv
import json
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
OUTPUT_PATH = Path("output") / "customers_clean.csv"


def fetch_users(url: str = API_URL, timeout: float = 10.0) -> list[dict]:
    """Retrieve users from the API and report request failures clearly."""
    try:
        response = requests.get(url, timeout=timeout)

    except requests.Timeout as exc:
        raise RuntimeError(
            f"API request timed out after {timeout} seconds."
        ) from exc

    except requests.ConnectionError as exc:
        raise RuntimeError(
            f"Could not connect to the API at {url}. "
            "Check the URL and your internet connection."
        ) from exc

    except requests.RequestException as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc

    # Check the HTTP status before reading the response body.
    if response.status_code != 200:
        raise RuntimeError(
            f"API returned HTTP {response.status_code}; expected HTTP 200."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "API response body is not valid JSON."
        ) from exc

    return payload


def describe_structure(payload) -> None:
    """Print the types of the payload and all values in one record."""

    print("Top-level payload type:", type(payload).__name__)

    if not isinstance(payload, list):
        print("Expected a list of user records.")
        return

    if not payload:
        print("The payload contains no user records.")
        return

    first_user = payload[0]
    print("One user record type:", type(first_user).__name__)

    def inspect_values(value, path="user"):
        if isinstance(value, dict):
            for key, nested_value in value.items():
                current_path = f"{path}.{key}"
                print(
                    f"{current_path}: "
                    f"{type(nested_value).__name__}"
                )
                if isinstance(nested_value, (dict, list)):
                    inspect_values(nested_value, current_path)

        elif isinstance(value, list):
            for index, nested_value in enumerate(value):
                current_path = f"{path}[{index}]"
                print(
                    f"{current_path}: "
                    f"{type(nested_value).__name__}"
                )
                if isinstance(nested_value, (dict, list)):
                    inspect_values(nested_value, current_path)

    inspect_values(first_user)


def extract_core_fields(users: list[dict]) -> list[dict]:
    """Extract core customer fields, using safe defaults for missing values."""
    core_users = []

    for user in users:
        address = user.get("address") or {}
        company = user.get("company") or {}

        if not isinstance(address, dict):
            address = {}

        if not isinstance(company, dict):
            company = {}

        core_user = {
            "id": user.get("id"),
            "name": user.get("name") or "",
            "email": user.get("email") or "",
            "city": address.get("city") or "",
            "company": company.get("name") or "",
        }

        core_users.append(core_user)

    return core_users


def build_structures(users: list[dict]) -> tuple[list, list[tuple], dict]:
    """Build lists, tuples and a dictionary from user records."""

    # List comprehension: extract customer names.
    list_of_names = [user.get("name", "") or "" for user in users]

    # List comprehension: build (id, email) tuples.
    list_of_id_email_tuples = [
        (user.get("id"), user.get("email", "") or "")
        for user in users
    ]

    # Dictionary comprehension: map each customer ID to their city.
    dict_of_id_to_city = {
        user.get("id"): ((user.get("address") or {}).get("city") or "")
        for user in users
        if isinstance(user.get("address") or {}, dict)
    }

    # Plain for loop: demonstrate processing the records.
    for user in users:
        if "id" not in user:
            continue

    return list_of_names, list_of_id_email_tuples, dict_of_id_to_city


def flatten_user(user: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Flatten nested dictionaries into a single-level dictionary."""
    flattened = {}

    for key, value in user.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            flattened.update(flatten_user(value, new_key, sep))
        else:
            flattened[new_key] = value

    return flattened


def to_dataframe(flat_users: list[dict]) -> pd.DataFrame:
    """Create a clean DataFrame with the required columns and data types."""

    expected_columns = [
        "customer_id",
        "name",
        "username",
        "email",
        "phone",
        "website",
        "address_street",
        "address_suite",
        "address_city",
        "address_zipcode",
        "address_geo_lat",
        "address_geo_lng",
        "company_name",
        "company_catchphrase",
        "company_bs",
    ]

    df = pd.DataFrame(flat_users)

    # Rename fields to match the expected CSV specification.
    df = df.rename(columns={
        "id": "customer_id",
        "company_catchPhrase": "company_catchphrase",
    })

    # Ensure every required column exists, even if the API omits it.
    for column in expected_columns:
        if column not in df.columns:
            df[column] = pd.NA

    # Convert numeric fields safely.
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df["address_geo_lat"] = pd.to_numeric(
        df["address_geo_lat"], errors="coerce"
    )
    df["address_geo_lng"] = pd.to_numeric(
        df["address_geo_lng"], errors="coerce"
    )

    # Keep only the required columns, in the exact expected order.
    df = df[expected_columns]

    print("DataFrame shape:", df.shape)
    print("\nDataFrame dtypes:")
    print(df.dtypes)

    return df


def export_csv(df: pd.DataFrame, path: Path = OUTPUT_PATH) -> Path:
    """Export the DataFrame to CSV without an index."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)

    return path


def main() -> None:
    """Run the complete customer extraction pipeline."""
    try:
        users = fetch_users(API_URL)

        print(f"Successfully fetched {len(users)} users.")

        describe_structure(users)

        core_users = extract_core_fields(users)
        print(f"\nExtracted core fields for {len(core_users)} users.")

        names, id_emails, cities = build_structures(users)
        print(f"Built {len(names)} names, {len(id_emails)} email tuples, "
              f"and {len(cities)} city mappings.")

        flat_users = [flatten_user(user) for user in users]

        df = to_dataframe(flat_users)
        output_path = export_csv(df, OUTPUT_PATH)

        print(f"\nCSV exported successfully to: {output_path.resolve()}")
        print(f"Rows exported: {len(df)}")
        print("Pipeline completed successfully.")

    except (RuntimeError, ValueError) as exc:
        import sys
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
