import re
import pandas as pd
from rapidfuzz import fuzz, process

places = pd.read_csv("data/villages.csv")
NAMES = places.village.str.lower().tolist() + places.village_bn.tolist()
ROWS = list(range(len(places))) * 2
TOKEN = re.compile(r"[A-Za-zঀ-৿]+")

def find_place(text: str):
    toks = TOKEN.findall(text.lower())
    candidates = toks + [" ".join(p) for p in zip(toks, toks[1:])]
    best = None
    for c in candidates:
        if len(c) < 4:
            continue
        m = process.extractOne(c, NAMES, scorer=fuzz.ratio, score_cutoff=85)
        if m and (best is None or m[1] > best[1]):
            best = m
    return None if best is None else places.iloc[ROWS[best[2]]].to_dict()
