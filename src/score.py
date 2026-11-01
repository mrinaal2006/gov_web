import sqlite3
from datetime import datetime, timedelta
import joblib
import pandas as pd
from features import build_features
from location import find_place
from preprocess import clean, detect_language

CLF = joblib.load("models/dept_clf.joblib")
URG = joblib.load("models/urgency.joblib")
DB = "data/radar.db"

def score_complaint(raw_text, channel="portal", save=True):
    text = clean(raw_text)
    now = datetime.now().replace(microsecond=0)
    proba = CLF.predict_proba([text])
    dept = str(CLF.classes_[proba.argmax()])
    place = find_place(text) or {}
    with sqlite3.connect(DB) as con:
        repeat = con.execute(
            "select count(*) from complaints where village = ? and department = ? "
            "and received_at >= ?",
            (place.get("village"), dept, str(now - timedelta(days=7)))).fetchone()[0]
    one = pd.DataFrame([{"text": text, "channel": channel,
                         "received_at": now, "repeat_7d": repeat}])
    urgency = int(round(URG.predict_proba(build_features(one, proba, CLF.classes_))[0, 1] * 100))
    row = {"complaint_id": f"W-{datetime.now():%Y%m%d%H%M%S%f}", "text": text,
           "language": detect_language(text), "channel": channel, "received_at": now,
           "district": place.get("district"), "block": place.get("block"),
           "village": place.get("village"), "lat": place.get("lat"), "lon": place.get("lon"),
           "department": dept, "urgency": urgency}
    if save:
        with sqlite3.connect(DB) as con:
            pd.DataFrame([row]).to_sql("complaints", con, if_exists="append", index=False)
    return {**row, "received_at": now.isoformat(), "confidence": float(proba.max())}
