import pandas as pd
import os


def deduplicate_data():

    input_path = "output/cleaned_data.csv"

    if not os.path.exists(input_path):
        print("cleaned_data.csv not found.")
        return

    df = pd.read_csv(input_path)

    if df.empty:
        print("No data to deduplicate.")
        return

    # Remove duplicates using maps link
    if "maps_link" in df.columns:
        df = df.drop_duplicates(subset=["maps_link"])

    # Remove duplicates by name
    if "name" in df.columns:
        df = df.drop_duplicates(subset=["name"])

    df.to_csv(input_path, index=False, encoding="utf-8-sig")

    print(f"Unique records after deduplication: {len(df)}")