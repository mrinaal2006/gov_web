"""Builds the officer PDF report. It uses counts, IDs and place names only: no complaint text, names or phone numbers."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fpdf import FPDF
from fpdf.fonts import FontFace

IST = timezone(timedelta(hours=5, minutes=30))
OPEN = ("received", "in_progress")
HOTSPOT_MIN = 8
HOTSPOT_WINDOW = timedelta(hours=48)
HIGH_URGENCY = 70
BRAND = (11, 92, 85)
SOFT = (228, 240, 237)
MUTED = (87, 99, 95)


def parse(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def safe(text):
    """The built-in PDF font covers Latin characters only."""
    return str(text).encode("latin-1", "replace").decode("latin-1")


def day(moment):
    return moment.astimezone(IST).strftime("%d %b %Y")


def find_hotspots(rows):
    """Finds each village and department with 8 or more complaints in any 48 hours of the period."""
    groups = defaultdict(list)
    for row in rows:
        if row["village"]:
            groups[(row["village"], row["block"], row["department"])].append(parse(row["received_at"]))
    found = []
    for (village, block, department), times in groups.items():
        times.sort()
        start = peak = 0
        peak_end = None
        for end, moment in enumerate(times):
            while moment - times[start] > HOTSPOT_WINDOW:
                start += 1
            if end - start + 1 > peak:
                peak, peak_end = end - start + 1, moment
        if peak >= HOTSPOT_MIN:
            found.append({"village": village, "block": block, "department": department, "complaints": peak, "date": peak_end})
    return sorted(found, key=lambda h: -h["complaints"])


def _average(values):
    return f"{sum(values) / len(values):.1f}" if values else "-"


def summarise(rows, now):
    def blank():
        return {"complaints": 0, "pending": 0, "overdue": 0, "days": []}

    total, departments, cards = blank(), defaultdict(blank), defaultdict(blank)
    high = closed = 0
    for row in rows:
        targets = [total, departments[row["department"]]]
        if row["block"]:
            targets.append(cards[(row["block"], row["department"])])
        is_open = row["status"] in OPEN
        late = is_open and parse(row["due_at"]) < now
        taken = (parse(row["resolved_at"]) - parse(row["received_at"])).total_seconds() / 86400 if row["resolved_at"] else None
        high += int(is_open and (row["urgency"] or 0) >= HIGH_URGENCY)
        closed += int(not is_open)
        for target in targets:
            target["complaints"] += 1
            target["pending"] += int(is_open)
            target["overdue"] += int(late)
            if taken is not None:
                target["days"].append(taken)
    return total, departments, cards, high, closed


class ReportPDF(FPDF):
    service = ""

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", size=8)
        self.set_text_color(*MUTED)
        self.cell(0, 5, safe(f"{self.service} report"), align="L")
        self.set_x(self.l_margin)
        self.cell(0, 5, f"Page {self.page_no()} of {{nb}}", align="R")


def build(rows, period, now, service="Samasya Radar", operator=None):
    total, departments, cards, high, closed = summarise(rows, now)
    pdf = ReportPDF(format="A4")
    pdf.service = service
    pdf.set_title(f"{service} report: {period}")
    pdf.set_auto_page_break(True, margin=18)
    pdf.set_margins(16, 16, 16)
    pdf.add_page()

    width = pdf.w - 32
    pdf.set_fill_color(*BRAND)
    pdf.rect(16, 16, width, 30, style="F")
    pdf.set_fill_color(255, 255, 255)  # table rows use the current fill colour
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(22, 21)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, safe(f"{service} report"))
    pdf.set_xy(22, 32)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, safe(period))
    pdf.set_text_color(24, 33, 31)
    pdf.set_xy(16, 50)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(*MUTED)
    stamp = now.astimezone(IST).strftime("%d %b %Y, %I:%M %p IST")
    pdf.cell(0, 5, safe(f"Generated {stamp}" + (f". Operated by {operator}." if operator else ".")))
    pdf.ln(9)

    def heading(text):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*BRAND)
        pdf.cell(0, 8, safe(text), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(24, 33, 31)
        pdf.set_font("Helvetica", size=9.5)

    def table(columns, body, widths, numeric_from):
        align = tuple("L" if i < numeric_from else "R" for i in range(len(columns)))
        style = FontFace(emphasis="BOLD", color=BRAND, fill_color=SOFT)
        pdf.set_draw_color(217, 223, 219)
        with pdf.table(col_widths=widths, text_align=align, headings_style=style, line_height=6.2,
                       borders_layout="HORIZONTAL_LINES", repeat_headings=1) as grid:
            grid.row([safe(c) for c in columns])
            for line in body:
                grid.row([safe(c) for c in line])
        pdf.ln(2)

    def note(text):
        pdf.set_font("Helvetica", size=9.5)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 5, safe(text), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(24, 33, 31)
        pdf.ln(1)

    heading("Summary")
    if not rows:
        note("No complaints were received in this period.")
    else:
        table(["Measure", "Number"], [
            ["Complaints received", total["complaints"]], ["Still pending", total["pending"]],
            ["Past response target", total["overdue"]], ["Pending with a high urgency score (70+)", high],
            ["Closed", closed], ["Average days to close", _average(total["days"])]], (75, 25), 1)

        heading("By department")
        table(["Department", "Complaints", "Pending", "Past target", "Avg days to close"],
              [[name, d["complaints"], d["pending"], d["overdue"], _average(d["days"])]
               for name, d in sorted(departments.items(), key=lambda item: -item[1]["complaints"])],
              (34, 22, 20, 22, 30), 1)

        heading("Hotspots in this period")
        spots = find_hotspots(rows)
        if spots:
            note(f"Places with {HOTSPOT_MIN} or more complaints about one department within any 48 hours. "
                 "These may have ended, so they can differ from the live alerts.")
            table(["Village", "Block", "Department", "Peak complaints", "Peak date"],
                  [[h["village"], h["block"], h["department"], h["complaints"], day(h["date"])] for h in spots],
                  (32, 36, 28, 26, 26), 3)
        else:
            note("No hotspots in this period.")

        urgent = sorted((r for r in rows if r["status"] in OPEN), key=lambda r: (-(r["urgency"] or 0), r["received_at"]))[:10]
        if urgent:
            heading("Highest urgency scores still pending")
            table(["Tracking ID", "Department", "Village", "Received", "Score"],
                  [[r["id"], r["department"], r["village"] or "Unknown", day(parse(r["received_at"])), r["urgency"]] for r in urgent],
                  (42, 28, 34, 28, 16), 4)

        if cards:
            heading("Scorecard by block and department")
            ordered = sorted(cards.items(), key=lambda item: (-item[1]["overdue"], -item[1]["pending"], item[0]))
            table(["Block", "Department", "Complaints", "Pending", "Past target", "Avg days"],
                  [[block, department, c["complaints"], c["pending"], c["overdue"], _average(c["days"])]
                   for (block, department), c in ordered], (42, 30, 20, 18, 20, 18), 2)

    note("Urgency scores are suggestions from software and need an officer's judgement. Pending and past-target counts "
         "show each complaint's status when this report was generated. This report contains no complaint text, names or phone numbers. "
         "Tracking IDs can open a complaint's text and replies, so share this report only with people who need it.")
    return bytes(pdf.output())
