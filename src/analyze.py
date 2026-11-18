import json, glob, sys, random, re

def stats(d):
    L = [json.load(open(p)) for p in sorted(glob.glob(f"{d}/listings/*.json"))]
    C = [c for x in L for c in x["claims"]]
    valid = sum(len(c["support"]) for c in C)
    sup = sum(len(c["supported_by"]) for c in C)
    bad = sum(c["bad_citations"] for c in C)
    comp = [c for c in C if re.search(r"\b(and|or)\b", c["claim"], re.I)]
    return {
        "listings": len(L), "claims": len(C),
        "claims_per_listing": round(len(C) / max(len(L), 1), 2),
        "dropped_pct": round(100 * sum(not c["kept"] for c in C) / max(len(C), 1), 1),
        "citation_precision_pct": round(100 * sup / max(valid, 1), 1),
        "citations_per_claim": round(valid / max(len(C), 1), 2),
        "out_of_range_citations": bad,
        "compound_claims_pct": round(100 * len(comp) / max(len(C), 1), 1),
        "compound_dropped_pct": round(100 * sum(not c["kept"] for c in comp) / max(len(comp), 1), 1),
        "single_dropped_pct": round(100 * sum(not c["kept"] for c in C if c not in comp) / max(len(C) - len(comp), 1), 1),
        "cons_share_pct": round(100 * sum(c["kind"] == "con" for c in C) / max(len(C), 1), 1),
        "mean_llm_seconds": round(sum(x["stats"]["seconds"] for x in L) / max(len(L), 1), 1),
        "mean_verify_seconds": round(sum(x["stats"]["verify_seconds"] for x in L) / max(len(L), 1), 2),
    }

def sample_dropped(d, k=25, seed=1):
    L = [json.load(open(p)) for p in sorted(glob.glob(f"{d}/listings/*.json"))]
    rows = [(x, c) for x in L for c in x["claims"] if not c["kept"]]
    random.Random(seed).shuffle(rows)
    for x, c in rows[:k]:
        print(f"\n### [{c['kind']}] {c['claim']}  (listing {x['listing_id']})")
        for n, s in zip([n for n in c["cited"] if 1 <= n <= len(x["reviews"])], c["support"]):
            print(f"  ({s:.2f}) {x['reviews'][n-1]['text'][:300]}")

if __name__ == "__main__":
    if sys.argv[1] == "sample":
        sample_dropped(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 25)
    else:
        for d in sys.argv[1:]:
            print(d, json.dumps(stats(d), indent=1))
