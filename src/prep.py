"""Pick listings and their most recent reviews, with names scrubbed."""
import re, sys, json, hashlib
import pandas as pd

def load(cutoff=None):
    r = pd.read_csv("data/raw/reviews.csv.gz")
    l = pd.read_csv("data/raw/listings.csv.gz", usecols=["id", "name", "host_name"])
    r = r.dropna(subset=["comments"])
    if cutoff:
        r = r[r.date <= cutoff]
    return r, l.set_index("id")

def scrub(text, names):
    text = re.sub(r"<br\s*/?>", " ", str(text))
    for n in names:
        if isinstance(n, str) and len(n) > 1:
            text = re.sub(rf"\b{re.escape(n)}\b", "the person", text, flags=re.I)
    text = re.sub(r"\S+@\S+", "[email]", text)
    text = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[phone]", text)
    return text.strip()

def listing_reviews(r, listings, lid, k=30, maxlen=400):
    sub = r[r.listing_id == lid].sort_values("date").tail(k)
    host = listings.loc[lid, "host_name"] if lid in listings.index else None
    out = []
    for _, row in sub.iterrows():
        t = scrub(row.comments, [row.reviewer_name, host])
        if len(t) < 15:
            continue
        out.append({"id": int(row.id), "date": row.date, "text": t[:maxlen]})
    return out

def review_set_hash(reviews):
    return hashlib.sha256(",".join(str(x["id"]) for x in reviews).encode()).hexdigest()[:16]
