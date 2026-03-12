import pandas as pd

def clean_data():
    df = pd.read_csv("output/raw_data.csv")

    # Keep rows with a name
    df = df[df["name"].notna()]

    # Standardize missing values
    df["address"] = df["address"].fillna("Not Available")
    df["phone"] = df["phone"].fillna("Not Available")
    df["website"] = df["website"].fillna("Not Available")
    df["rating"] = df["rating"].fillna("0")

    df.to_csv("output/cleaned_data.csv", index=False, encoding="utf-8-sig")

    print(f"Cleaned records: {len(df)}")
