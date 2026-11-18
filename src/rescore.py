"""Re-run only the checker over saved outputs, writing to a new folder."""
import json, glob, os, sys
from verify import check, check_sentences
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(f"{dst}/listings", exist_ok=True)
for p in sorted(glob.glob(f"{src}/listings/*.json")):
    d = json.load(open(p))
    mode = sys.argv[3] if len(sys.argv) > 3 else "template"
    if mode == "sentences": check_sentences(d["claims"], d["reviews"])
    elif mode == "raw": check(d["claims"], d["reviews"], template=None)
    else: check(d["claims"], d["reviews"])
    json.dump(d, open(f"{dst}/listings/{os.path.basename(p)}", "w"), indent=1)
print("rescored", len(glob.glob(f"{dst}/listings/*.json")))
