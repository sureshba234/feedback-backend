
import json, os, re
from typing import Tuple

_model = None

def load_model():
    global _model
    if _model is None:
        here = os.path.dirname(__file__)
        path = os.path.join(here, "model.json")
        if not os.path.exists(path):
            raise FileNotFoundError("model.json not found. Run train_model.py to generate it.")
        with open(path, "r", encoding="utf-8") as f:
            _model = json.load(f)
    return _model

def _tokenize(text: str):
    return re.findall(r"[a-z']+", text.lower())

def analyze_sentiment(text: str) -> Tuple[str, float]:
    m = load_model()
    weights = m.get("weights", {})
    bias = m.get("bias", 0.0)
    tpos = float(m.get("threshold_pos", 0.05))
    tneg = float(m.get("threshold_neg", -0.05))

    words = _tokenize(text)
    score = bias + sum(weights.get(w, 0.0) for w in words) / (len(words) + 1e-9)

    if score >= tpos:
        return "positive", float(score)
    elif score <= tneg:
        return "negative", float(score)
    else:
        return "neutral", float(score)
