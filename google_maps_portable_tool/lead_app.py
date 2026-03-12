import streamlit as st
import pandas as pd
import os

from scraper import run_scraper
from cleaner import clean_data
from deduplicator import deduplicate_data
from scorer import score_leads
from email_cleaner import clean_email_column

st.set_page_config(page_title="Maps Data Miner", layout="wide")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# ---------------- SESSION STATE ----------------
if "final_df" not in st.session_state:
    st.session_state.final_df = None
if "email_df" not in st.session_state:
    st.session_state.email_df = None

# ---------------- AREA EXTRACTOR ----------------
def extract_area(address):
    if pd.isna(address):
        return "Unknown"
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 2:
        return parts[-3] if len(parts) >= 3 else parts[-2]
    return "Unknown"

# ---------------- UI STYLES ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 3rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.header {
    font-size: 32px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 6px;
}
.subheader {
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 24px;
}
.card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 22px;
}
.kpi {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    text-align: center;
}
.kpi h3 { margin: 0; color: #111827; }
.kpi p { margin: 0; color: #6b7280; font-size: 13px; }

.stDownloadButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}
.stDownloadButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="header">Maps Data Miner</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Lead generation interface for sales outreach</div>', unsafe_allow_html=True)

# ---------------- QUERY INPUT ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

query_input = st.text_area(
    "Enter Queries (one per line)",
    placeholder="software company in Dublin Ireland\nsoftware company in Limerick Ireland",
    height=140
)

run_button = st.button("Generate Leads")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RUN PIPELINE ----------------
if run_button:

    queries = [q.strip() for q in query_input.split("\n") if q.strip()]

    if not queries:
        st.warning("Please enter at least one query.")
    else:

        all_data = []

        with st.spinner("Extracting leads from Google Maps..."):

            for q in queries:
                df = run_scraper(q)
                df["source_query"] = q
                all_data.append(df)

            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df.to_csv("output/raw_data.csv", index=False)

            clean_data()
            deduplicate_data()
            score_leads()

            final_df = pd.read_csv("output/final_leads.csv")

            if "source_query" not in final_df.columns and "source_query" in combined_df.columns:
                final_df["source_query"] = combined_df["source_query"]

            if "address" in final_df.columns:
                final_df["area"] = final_df["address"].apply(extract_area)
            else:
                final_df["area"] = "Unknown"

            email_df = clean_email_column(final_df)

            st.session_state.final_df = final_df
            st.session_state.email_df = email_df

# ---------------- SHOW RESULTS ----------------
if st.session_state.final_df is not None:

    final_df = st.session_state.final_df.copy()
    email_df = st.session_state.email_df.copy()

    # ---------------- QUERY FILTER ----------------
    query_options = ["All Queries"]
    if "source_query" in final_df.columns:
        query_options += sorted(final_df["source_query"].dropna().unique().tolist())

    selected_query = st.selectbox("Filter by Query", query_options)

    if selected_query != "All Queries":
        final_df = final_df[final_df["source_query"] == selected_query]
        email_df = email_df[email_df["source_query"] == selected_query]

    # ---------------- AREA FILTER ----------------
    area_options = ["All Areas"] + sorted(final_df["area"].dropna().unique().tolist())
    selected_area = st.selectbox("Filter by Area", area_options)

    if selected_area != "All Areas":
        final_df = final_df[final_df["area"] == selected_area]
        email_df = email_df[email_df["area"] == selected_area]

    # ---------------- NO WEBSITE DATASET ----------------
    no_website_df = final_df[
        (final_df["website"].isna()) |
        (final_df["website"] == "") |
        (final_df["website"] == "Not Available")
    ]

    # ---------------- DETECT LEAD COLUMN ----------------
    lead_col = None
    for col in final_df.columns:
        if "lead" in col.lower():
            lead_col = col
            break

    total_leads = len(final_df)

    if lead_col:
        high_leads = len(final_df[final_df[lead_col] == "High"])
        medium_leads = len(final_df[final_df[lead_col] == "Medium"])
    else:
        high_leads = 0
        medium_leads = 0

    emails = len(email_df)
    no_website = len(no_website_df)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f'<div class="kpi"><h3>{total_leads}</h3><p>Total Leads</p></div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="kpi"><h3>{high_leads}</h3><p>High Quality</p></div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="kpi"><h3>{medium_leads}</h3><p>Medium Quality</p></div>', unsafe_allow_html=True)

    with c4:
        st.markdown(f'<div class="kpi"><h3>{emails}</h3><p>Campaign Emails</p></div>', unsafe_allow_html=True)

    with c5:
        st.markdown(f'<div class="kpi"><h3>{no_website}</h3><p>No Website Leads</p></div>', unsafe_allow_html=True)

    # ---------------- FINAL LEADS TABLE ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Final Leads Dataset")

    st.dataframe(final_df, use_container_width=True)

    st.download_button(
        label="Download Final Leads",
        data=final_df.to_csv(index=False).encode("utf-8"),
        file_name="final_leads.csv",
        mime="text/csv"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- EMAIL TABLE ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Campaign Email List")

    st.dataframe(email_df, use_container_width=True)

    st.download_button(
        label="Download Campaign Emails",
        data=email_df.to_csv(index=False).encode("utf-8"),
        file_name="campaign_emails.csv",
        mime="text/csv"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- NO WEBSITE TABLE ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Businesses Without Website")

    st.dataframe(no_website_df, use_container_width=True)

    st.download_button(
        label="Download No Website Leads",
        data=no_website_df.to_csv(index=False).encode("utf-8"),
        file_name="no_website_leads.csv",
        mime="text/csv"
    )

    st.markdown('</div>', unsafe_allow_html=True)