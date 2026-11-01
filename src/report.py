import sqlite3
import pandas as pd
from fpdf import FPDF
from hotspots import village_spikes

with sqlite3.connect("data/radar.db") as con:
    df = pd.read_sql("select * from complaints", con, parse_dates=["received_at"])
end = pd.Timestamp.now()
week = df[df.received_at >= end - pd.Timedelta(days=7)]

lines = [f"Total complaints: {len(week)}",
         f"High urgency (70+): {int((week.urgency >= 70).sum())}", "", "Top departments:"]
lines += [f"  {d}: {n}" for d, n in week.department.value_counts().head(5).items()]
lines += ["", "Hotspots:"]
lines += [f"  {r.department} in {r.village}: {r.peak_count} complaints in 48 hours"
          for r in village_spikes(week).itertuples()] or ["  None"]

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, f"Samasya Radar weekly report, {end:%d %b %Y}", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=11)
for line in lines:
    pdf.cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")
pdf.output("weekly_report.pdf")
