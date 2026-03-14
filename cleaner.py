import pandas as pd
import os


def clean_data():

    input_path = "output/raw_data.csv"
    output_path = "output/cleaned_data.csv"

    if not os.path.exists(input_path):
        print("raw_data.csv not found.")
        return

    df = pd.read_csv(input_path)

    if df.empty:
        print("No data to clean.")
        return

    # Keep rows with business name
    if "name" in df.columns:
        df = df[df["name"].notna()]

    # Standardize missing values
    df["address"] = df.get("address", "").fillna("Not Available")
    df["phone"] = df.get("phone", "").fillna("Not Available")
    df["website"] = df.get("website", "").fillna("Not Available")
    df["rating"] = df.get("rating", "").fillna("0")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Cleaned records: {len(df)}")