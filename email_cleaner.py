import pandas as pd
import re

# patterns to remove (junk + system + test)
BAD_PATTERNS = [
    "png", "jpg", "jpeg", "gif", "webp", "svg",
    "noreply", "no-reply", "donotreply",
    "example.com", "test@"
]

# system domains to remove
BAD_DOMAINS = [
    "wixpress.com",
    "sentry.io",
    "cloudflare.com",
    "sentry-next.wixpress.com"
]

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def is_valid_email(email):
    if pd.isna(email):
        return False

    email = email.strip().lower()

    if not re.match(EMAIL_REGEX, email):
        return False

    for pattern in BAD_PATTERNS:
        if pattern in email:
            return False

    for domain in BAD_DOMAINS:
        if domain in email:
            return False

    return True


def clean_email_column(df):
    df = df.copy()

    if "email" not in df.columns:
        return pd.DataFrame()

    # ensure required columns exist (avoid KeyError)
    for col in ["city", "source_query"]:
        if col not in df.columns:
            df[col] = "Unknown"

    df["email"] = df["email"].astype(str)

    # keep only first email if multiple
    df["email"] = df["email"].apply(lambda x: x.split(";")[0].strip())

    # validate emails
    df["valid_email"] = df["email"].apply(is_valid_email)

    df_valid = df[df["valid_email"] == True].copy()

    # remove duplicate emails (unique campaign list)
    df_valid = df_valid.drop_duplicates(subset=["email"])

    # 🔥 keep city + source_query for filters
    columns_to_keep = [
        col for col in [
            "name",
            "email",
            "phone",
            "website",
            "rating",
            "address",
            "area",          # ✅ added for city filter
            "source_query"   # ✅ needed for query filter
        ] if col in df_valid.columns
    ]

    campaign_df = df_valid[columns_to_keep].copy()

    return campaign_df