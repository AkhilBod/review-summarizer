# review-summarizer

Summarizes Airbnb guest reviews into short pros and cons, where every claim has to cite the reviews it came from, and a second model throws out claims the cited reviews don't actually say.

Everything runs locally: Qwen 2.5 7B through Ollama writes the summaries, and a DeBERTa NLI model checks them. Data is the public [Inside Airbnb](https://insideairbnb.com/get-the-data/) dump for Columbus, Ohio (2,959 listings, 202K reviews, scraped Sept 2026).

## How it works

1. `prep.py` takes the 30 most recent reviews for a listing and scrubs reviewer names, host names, emails, and phone numbers before anything reaches a model.
2. `summarize.py` asks the model for at most 5 pros and 3 cons as JSON, each citing review numbers.
3. `verify.py` scores each (review, claim) pair with NLI. A citation counts if entailment is at least 0.5. A claim with no supporting citation gets dropped. The claim is wrapped as "The reviewer says: ..." before scoring, because NLI models score sentence fragments badly.
4. `run.py` hashes each listing's review set and skips listings that haven't changed since the last run.

## Run it

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
ollama pull qwen2.5:7b-instruct
# download listings.csv.gz and reviews.csv.gz for a city into data/raw/
.venv/bin/python src/run.py 60 - out/v2 v2       # 60 listings, prompt v2
.venv/bin/python src/rescore.py out/v2 out/v2t template
.venv/bin/python src/analyze.py out/v2t
.venv/bin/python src/snapshot.py 2026-08-25 2026-09-25
```

See the write-up for results.
