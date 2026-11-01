import json
import sqlite3
import sys
from pathlib import Path
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from hotspots import village_spikes
from score import DB, score_complaint

app = FastAPI(title="Samasya Radar API")

class ComplaintIn(BaseModel):
    text: str
    channel: str = "portal"

def load_recent(hours):
    with sqlite3.connect(DB) as con:
        df = pd.read_sql("select * from complaints", con, parse_dates=["received_at"])
    return df[df.received_at >= pd.Timestamp.now() - pd.Timedelta(hours=hours)]

def records(df):
    return json.loads(df.to_json(orient="records", date_format="iso"))

@app.post("/complaints")
def add_complaint(c: ComplaintIn):
    return score_complaint(c.text, c.channel)

@app.get("/hotspots")
def hotspots(hours: int = 48):
    return records(village_spikes(load_recent(hours)))

@app.get("/priority")
def priority(limit: int = 20):
    df = load_recent(24 * 7)
    return records(df.sort_values("urgency", ascending=False).head(limit))
