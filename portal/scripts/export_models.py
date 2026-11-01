"""Converts the trained models in ../models into plain JSON for the portal.

Run from samasya-radar/ after retraining: python portal/scripts/export_models.py
Needs joblib, scikit-learn and lightgbm. The deployed portal does not.
"""
import json
from pathlib import Path

import joblib
import pandas as pd

OUT = Path("portal/server/model")
OUT.mkdir(parents=True, exist_ok=True)


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(name, (OUT / name).stat().st_size // 1024, "KB")


clf = joblib.load("models/dept_clf.joblib")
union, lr = clf.named_steps["tfidf"], clf.named_steps["lr"]
parts = []
for name, vec in union.transformer_list:
    parts.append({"name": name, "vocabulary": {k: int(v) for k, v in vec.vocabulary_.items()},
                  "idf": [round(float(x), 7) for x in vec.idf_]})
dump("department.json", {"classes": [str(c) for c in lr.classes_], "parts": parts,
                         "coef": [[round(float(x), 7) for x in row] for row in lr.coef_],
                         "intercept": [round(float(x), 7) for x in lr.intercept_]})


def tree(node):
    if "leaf_value" in node:
        return node["leaf_value"]
    return [node["split_feature"], node["threshold"], tree(node["left_child"]), tree(node["right_child"])]


booster = joblib.load("models/urgency.joblib").booster_.dump_model()
dump("urgency.json", {"features": booster["feature_names"],
                      "trees": [tree(t["tree_structure"]) for t in booster["tree_info"]]})

villages = pd.read_csv("data/villages.csv")
dump("villages.json", villages.to_dict(orient="records"))
