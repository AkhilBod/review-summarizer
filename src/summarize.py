import json, requests

MODEL = "qwen2.5:7b-instruct"
V2_EXTRA = """
- One fact per claim. Never join two things with "and" or "or". Split them into separate claims.
- Use the guests' own words where you can (say "close to OSU campus", not "great location")."""
PROMPT = """Below are guest reviews of one short-term rental, each with a number.
Write what guests consistently liked (pros) and disliked (cons).
Rules:
- Each item is one short, specific claim about the place or stay (max 15 words).{extra}
- Each item must cite the review numbers that say it. Cite only reviews that actually say it.
- At most 5 pros and 3 cons. If guests had no real complaints, return an empty cons list.
Return JSON only: {"pros":[{"claim":"...","reviews":[1,4]}],"cons":[{"claim":"...","reviews":[7]}]}

Reviews:
"""

def summarize(reviews, model=MODEL, temperature=0.2, version="v1"):
    body = "\n".join(f"[{i+1}] {r['text']}" for i, r in enumerate(reviews))
    resp = requests.post("http://localhost:11434/api/chat", json={
        "model": model, "stream": False, "format": "json",
        "options": {"temperature": temperature, "num_ctx": 8192},
        "messages": [{"role": "user", "content": PROMPT.replace("{extra}", V2_EXTRA if version == "v2" else "") + body}],
    }, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    try:
        parsed = json.loads(data["message"]["content"])
    except json.JSONDecodeError:
        parsed = {"pros": [], "cons": [], "parse_error": True}
    claims = []
    for kind in ("pros", "cons"):
        for item in parsed.get(kind, []) or []:
            if not isinstance(item, dict) or not item.get("claim"):
                continue
            nums = [n for n in item.get("reviews", []) if isinstance(n, int)]
            claims.append({"kind": kind[:-1], "claim": item["claim"].strip(), "cited": nums})
    stats = {"prompt_tokens": data.get("prompt_eval_count"), "gen_tokens": data.get("eval_count"),
             "seconds": round(data.get("total_duration", 0) / 1e9, 1)}
    return claims, stats
