"""How many listings would need re-summarizing if we ran monthly? Compare review-set hashes across two cutoffs."""
import sys
from prep import load, listing_reviews, review_set_hash
old_cut, new_cut = sys.argv[1], sys.argv[2]
r_old, L = load(old_cut); r_new, _ = load(new_cut)
lids = sorted(set(r_old.listing_id))
changed = new = 0
for lid in lids:
    if review_set_hash(listing_reviews(r_old, L, lid)) != review_set_hash(listing_reviews(r_new, L, lid)):
        changed += 1
new = len(set(r_new.listing_id) - set(lids))
print(f"{old_cut} -> {new_cut}: listings={len(lids)} changed={changed} ({100*changed/len(lids):.1f}%) brand_new={new}")
