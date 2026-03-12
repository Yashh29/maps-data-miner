# Maps Data Miner – Google Maps Lead Generation Tool

##  Overview
Maps Data Miner is a portable lead generation tool that extracts business data from Google Maps, cleans and deduplicates it, enriches it with emails (from company websites), and produces a sales-ready dataset.

The tool also includes a Streamlit dashboard that allows users to:
- Run multi-query lead extraction
- Filter leads by query and city
- View high/medium quality leads
- Download final leads and campaign email lists

---

##  Key Features

✔ Multi-query Google Maps scraping  
✔ Portable WebDriver (no manual ChromeDriver setup required)  
✔ Automatic scrolling – extracts all available listings  
✔ Email extraction from company website + contact page  
✔ Email validation (removes system/junk emails)  
✔ Global deduplication using Maps links  
✔ Lead scoring (High / Medium / Low)  
✔ City extraction from address for filtering  
✔ Query & City filters in dashboard  
✔ Downloadable CSV outputs for sales outreach  

---

##  Output Files

After running the tool, the following files are generated:

### `output/raw_data.csv`
All scraped listings (uncleaned)

### `output/final_leads.csv`
Cleaned, deduplicated, and lead-scored dataset

### `output/campaign_emails_final.csv`
Valid, unique, mail-ready emails for marketing campaigns

---

##  Installation (Run on Any Laptop)

### 1️ Install Python
Install **Python 3.10 or 3.11** from:  
https://www.python.org/downloads/


---

### 2️ Install Dependencies
Open terminal inside the project folder and run:

```bash
pip install -r requirements.txt

If pip is not recognized:

python -m pip install -r requirements.txt



3 Run the Dashboard 

python -m streamlit run lead_app.py




How to Use

Enter queries (one per line), for example:

software company in London UK
software company in Toronto Canada

Click Generate Leads

Use filters:

Filter by Query

Filter by City

Download:

Final Leads CSV

Campaign Email List CSV



 Lead Scoring Logic

Leads are classified based on:

Rating

Website availability

Phone availability

Email availability

Lead quality categories:

High

Medium

Low

 Notes

Email extraction depends on availability on the company website

Not all businesses publish emails publicly

Tool extracts publicly available data only

Large queries may take several minutes to process



👤 Author Role

Built end-to-end data pipeline

Implemented scraping, cleaning, and deduplication logic

Developed email validation and filtering system

Designed lead scoring model

Created Streamlit sales dashboard



 Business Use Case

Sales and marketing teams use the final email list for:

Targeted outreach campaigns

Premium service promotion

High-conversion lead targeting




ONE LINE SETUP COMMAND

python -m pip install -r requirements.txt && python -m streamlit run lead_app.py

IF PYTHON DOESN'T WORKS:
py -m pip install -r requirements.txt && py -m streamlit run lead_app.py