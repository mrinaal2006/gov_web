"""Loads the simulated complaints into the local SQLite database, for trying the officer desk.

Run from portal/: python scripts/seed_demo.py
It refuses to run against a real database.
"""
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import config, db  # noqa: E402

if config.DATABASE_URL or config.ON_VERCEL:
    raise SystemExit("Demo data is for local SQLite only.")

source = sqlite3.connect(config.ROOT.parent / "data" / "radar.db")
source.row_factory = sqlite3.Row
since = (datetime.now() - timedelta(days=90)).isoformat(" ")
rows = source.execute("select * from complaints where received_at >= ?", (since,)).fetchall()
current = datetime.now()


def utc(value):
    # radar.db holds naive local times
    return db.iso(datetime.fromisoformat(value).astimezone(timezone.utc))


with db.connect() as con:
    for r in rows:
        identifier = f"DEMO-{r['complaint_id']}"
        received = datetime.fromisoformat(r["received_at"])
        resolved = r["resolved_at"]
        closed = bool(resolved) and datetime.fromisoformat(resolved) <= current
        con.run("insert into complaints (id, text, language, channel, received_at, due_at, resolved_at, district, block, "
                "village, lat, lon, village_source, department, department_confidence, urgency, needs_review, status) "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'demo', ?, 1, ?, 0, ?) on conflict (id) do nothing",
                (identifier, r["text"], r["language"], r["channel"], utc(r["received_at"]),
                 db.iso((received + timedelta(days=config.RESPONSE_DAYS)).astimezone(timezone.utc)),
                 utc(resolved) if closed else None, r["district"], r["block"], r["village"], r["lat"], r["lon"],
                 r["department"], r["urgency"], "resolved" if closed else "received"))
print("loaded", len(rows), "simulated complaints")
