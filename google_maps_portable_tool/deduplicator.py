import pandas as pd

def deduplicate_data():
    df = pd.read_csv("output/cleaned_data.csv")

    # Remove duplicates using maps_link (unique place ID)
    df = df.drop_duplicates(subset=["maps_link"])
    
    df = df.drop_duplicates(subset=["name"])

    df.to_csv("output/cleaned_data.csv", index=False, encoding="utf-8-sig")

    print(f"Unique records after deduplication: {len(df)}")
