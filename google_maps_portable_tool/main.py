from scraper import run_scraper
from cleaner import clean_data
from deduplicator import deduplicate_data
from scorer import score_leads
from email_cleaner import clean_email_column

import pandas as pd
import os


def main():

    print("Enter multiple queries (type 'done' to finish):")

    queries = []
    while True:
        q = input("Enter query: ")
        if q.lower() == "done":
            break
        queries.append(q)

    if not queries:
        print("No queries provided.")
        return

    all_raw_data = []

    for query in queries:
        print(f"\nRunning scraper for: {query}")
        df = run_scraper(query)
        all_raw_data.append(df)

    # Combine all raw data
    combined_df = pd.concat(all_raw_data, ignore_index=True)

    os.makedirs("output", exist_ok=True)
    combined_df.to_csv("output/raw_data.csv", index=False, encoding="utf-8-sig")

    print(f"\nTotal extracted rows (before cleaning): {len(combined_df)}")

    print("Cleaning data...")
    clean_data()

    print("Removing duplicates globally...")
    deduplicate_data()

    print("Scoring leads...")
    score_leads()

    #  NEW STEP – EMAIL VALIDATION FOR MARKETING
    print("Filtering valid mailable emails...")

    final_df = pd.read_csv("output/final_leads.csv")

    email_ready_df = clean_email_column(final_df)

    email_ready_df.to_csv(
        "output/final_leads_emails_only.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Valid emails for campaign: {len(email_ready_df)}")

    print("\nMulti-query tool completed.")
    print("All leads → output/final_leads.csv")
    print("Mailable emails → output/final_leads_emails_only.csv")


if __name__ == "__main__":
    main()