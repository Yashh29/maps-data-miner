import pandas as pd

def score_leads():
    df = pd.read_csv("output/cleaned_data.csv")

    def lead_score(row):
        try:
            rating = float(row["rating"])
        except:
            rating = 0

        phone_available = row["phone"] != "Not Available"
        website_available = row["website"] != "Not Available"

        if rating >= 4.2 and phone_available and website_available:
            return "High"
        elif rating >= 4.0 and phone_available:
            return "Medium"
        else:
            return "Low"

    df["lead_score"] = df.apply(lead_score, axis=1)

    df.to_csv("output/final_leads.csv", index=False, encoding="utf-8-sig")

    high = (df["lead_score"] == "High").sum()
    medium = (df["lead_score"] == "Medium").sum()
    low = (df["lead_score"] == "Low").sum()

    print("Lead scoring completed.")
    print(f"High leads: {high}")
    print(f"Medium leads: {medium}")
    print(f"Low leads: {low}")
    print(f"Total leads: {len(df)}")
