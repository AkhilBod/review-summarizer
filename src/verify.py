"""Drop claims that none of their cited reviews actually support, using an NLI model."""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

NAME = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
_dev = "mps" if torch.backends.mps.is_available() else "cpu"
_tok = AutoTokenizer.from_pretrained(NAME)
_model = AutoModelForSequenceClassification.from_pretrained(NAME).to(_dev).eval()
_ENT = _model.config.label2id.get("entailment", 0)

@torch.no_grad()
def entail(premises, hypothesis):
    if not premises:
        return []
    enc = _tok(premises, [hypothesis] * len(premises), truncation=True, max_length=512,
               padding=True, return_tensors="pt").to(_dev)
    probs = torch.softmax(_model(**enc).logits, -1)[:, _ENT]
    return probs.tolist()

def check(claims, reviews, threshold=0.5, template="The reviewer says: {}"):
    for c in claims:
        valid = [n for n in c["cited"] if 1 <= n <= len(reviews)]
        c["bad_citations"] = len(c["cited"]) - len(valid)
        hyp = template.format(c["claim"].rstrip(".")) + "." if template else c["claim"]
        scores = entail([reviews[n - 1]["text"] for n in valid], hyp)
        c["support"] = [round(s, 3) for s in scores]
        c["supported_by"] = [reviews[n - 1]["id"] for n, s in zip(valid, scores) if s >= threshold]
        c["kept"] = len(c["supported_by"]) > 0
    return claims

import re as _re

def sentences(text):
    parts = [p.strip() for p in _re.split(r"(?<=[.!?])\s+|\n+", text) if len(p.strip()) > 3]
    return parts or [text]

def check_sentences(claims, reviews, threshold=0.5):
    """Same as check(), but scores each sentence of a review and keeps the best one."""
    for c in claims:
        valid = [n for n in c["cited"] if 1 <= n <= len(reviews)]
        c["bad_citations"] = len(c["cited"]) - len(valid)
        scores = []
        for n in valid:
            sents = sentences(reviews[n - 1]["text"])
            scores.append(max(entail(sents, c["claim"])))
        c["support"] = [round(s, 3) for s in scores]
        c["supported_by"] = [reviews[n - 1]["id"] for n, s in zip(valid, scores) if s >= threshold]
        c["kept"] = len(c["supported_by"]) > 0
    return claims
