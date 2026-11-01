"""The department, place and urgency logic from src/, running on exported JSON with no ML packages."""
import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from rapidfuzz import fuzz, process

MODEL_DIR = Path(__file__).resolve().parent / "model"
PHONE = re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}")
AADHAAR = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
BENGALI = re.compile(r"[ঀ-৿]")
TOKEN = re.compile(r"[A-Za-zঀ-৿]+")
WORD = re.compile(r"(?u)\b\w\w+\b")
SPACES = re.compile(r"\s\s+")
SEVERE = ["sick", "hospital", "death", "died", "child", "fire", "electrocut", "flood",
          "osustho", "baccha", "morche", "অসুস্থ", "শিশু", "হাসপাতাল", "মৃত্যু"]


def clean(text):
    text = AADHAAR.sub("[ID]", str(text))
    return re.sub(r"\s+", " ", PHONE.sub("[PHONE]", text)).strip()


def detect_language(text):
    share = len(BENGALI.findall(text)) / max(len(text), 1)
    return "bn" if share > 0.3 else ("mixed" if share > 0 else "en")


@lru_cache
def _load(name):
    return json.loads((MODEL_DIR / name).read_text(encoding="utf-8"))


def villages():
    return _load("villages.json")


def _word_grams(text):
    tokens = WORD.findall(text.lower())
    return tokens + [" ".join(pair) for pair in zip(tokens, tokens[1:])]


def _char_grams(text):
    grams = []
    for word in SPACES.sub(" ", text.lower()).split():
        word = f" {word} "
        for n in range(2, 6):
            offset = 0
            grams.append(word[offset:offset + n])
            while offset + n < len(word):
                offset += 1
                grams.append(word[offset:offset + n])
            if offset == 0:
                break
    return grams


def department_probabilities(text):
    model = _load("department.json")
    start, features = 0, {}
    for part, grams in zip(model["parts"], (_word_grams(text), _char_grams(text))):
        vocabulary, idf = part["vocabulary"], part["idf"]
        weights = {vocabulary[g]: c * idf[vocabulary[g]] for g, c in Counter(grams).items() if g in vocabulary}
        norm = math.sqrt(sum(w * w for w in weights.values())) or 1.0
        features.update({start + i: w / norm for i, w in weights.items()})
        start += len(idf)
    scores = [b + sum(row[i] * w for i, w in features.items())
              for row, b in zip(model["coef"], model["intercept"])]
    top = max(scores)
    exps = [math.exp(s - top) for s in scores]
    total = sum(exps)
    return {c: e / total for c, e in zip(model["classes"], exps)}


def find_place(text):
    places = villages()
    names = [p["village"].lower() for p in places] + [p["village_bn"] for p in places]
    tokens = TOKEN.findall(text.lower())
    best = None
    for candidate in tokens + [" ".join(pair) for pair in zip(tokens, tokens[1:])]:
        if len(candidate) < 4:
            continue
        match = process.extractOne(candidate, names, scorer=fuzz.ratio, score_cutoff=85)
        if match and (best is None or match[1] > best[1]):
            best = match
    return None if best is None else places[best[2] % len(places)]


def severe_words(text):
    low = text.lower()
    return [k for k in SEVERE if k in low]


def urgency_score(text, probabilities, repeat_7d, hour, channel="portal"):
    model = _load("urgency.json")
    values = {f"p_{c}": p for c, p in probabilities.items()}
    values.update(severe_hits=len(severe_words(text)), length=len(text), repeat_7d=repeat_7d,
                  hour=hour, news_or_social=int(channel in ("news", "social")))
    row = [values[name] for name in model["features"]]
    raw = 0.0
    for node in model["trees"]:
        while isinstance(node, list):
            node = node[2] if row[node[0]] <= node[1] else node[3]
        raw += node
    return 1 / (1 + math.exp(-raw))
