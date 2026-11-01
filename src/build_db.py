import sqlite3
import joblib
import pandas as pd
from features import add_repeat_7d, build_features
from preprocess import clean

df = pd.read_csv("data/complaints.csv", parse_dates=["received_at", "resolved_at"])
df["text"] = df.text.map(clean)
df = add_repeat_7d(df)
clf = joblib.load("models/dept_clf.joblib")
urg = joblib.load("models/urgency.joblib")
X = build_features(df, clf.predict_proba(df.text), clf.classes_)
df["urgency"] = (urg.predict_proba(X)[:, 1] * 100).round().astype(int)
with sqlite3.connect("data/radar.db") as con:
    df.drop(columns=["repeat_7d"]).to_sql("complaints", con, if_exists="replace", index=False)
