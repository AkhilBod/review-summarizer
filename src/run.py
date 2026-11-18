import json, os, sys, time, random
import pandas as pd
from prep import load, listing_reviews, review_set_hash
from summarize import summarize
from verify import check

def main(n=60, cutoff=None, seed=7, outdir="out", version="v1"):
    os.makedirs(f"{outdir}/listings", exist_ok=True)
    r, listings = load(cutoff)
    counts = r.groupby("listing_id").size()
    pool = sorted(counts[counts >= 30].index.tolist())
    random.Random(seed).shuffle(pool)
    picked = pool[:n]
    done = skipped = 0
    for i, lid in enumerate(picked):
        reviews = listing_reviews(r, listings, lid)
        h = review_set_hash(reviews)
        path = f"{outdir}/listings/{lid}.json"
        if os.path.exists(path) and json.load(open(path)).get("hash") == h:
            skipped += 1
            continue
        t = time.time()
        claims, stats = summarize(reviews, version=version)
        check(claims, reviews)
        stats["verify_seconds"] = round(time.time() - t - stats["seconds"], 1)
        json.dump({"listing_id": int(lid), "name": listings.loc[lid, "name"] if lid in listings.index else "",
                   "hash": h, "reviews": reviews, "claims": claims, "stats": stats},
                  open(path, "w"), indent=1)
        done += 1
        kept = sum(c["kept"] for c in claims)
        print(f"{i+1}/{len(picked)} {lid} claims={len(claims)} kept={kept} {stats['seconds']}s", flush=True)
    print(f"summarized={done} skipped_unchanged={skipped}")

if __name__ == "__main__":
    a = sys.argv[1:]
    main(n=int(a[0]) if a else 60, cutoff=(a[1] if len(a) > 1 and a[1] != "-" else None),
         outdir=a[2] if len(a) > 2 else "out", version=a[3] if len(a) > 3 else "v1")
