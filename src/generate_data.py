import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)
villages = pd.read_csv("data/villages.csv")

T = {
    "Water": [
        ("en", "Tubewell water in {v} has been dirty for {n} days"),
        ("en", "No drinking water supply in {v} for {n} days"),
        ("mixed", "{v} gram-e {n} din dhore jol ashche na"),
        ("bn", "{v} গ্রামে {n} দিন ধরে টিউবওয়েলের জল নোংরা"),
    ],
    "Electricity": [
        ("en", "No electricity in {v} for {n} days, transformer burnt"),
        ("mixed", "{v}-te {n} din current nei"),
        ("bn", "{v} এলাকায় {n} দিন ধরে বিদ্যুৎ নেই"),
    ],
    "Roads": [
        ("en", "Road to {v} is broken, vehicles cannot pass for {n} days"),
        ("mixed", "{v} jabar rasta bhenge geche"),
        ("bn", "{v} যাওয়ার রাস্তা ভেঙে গেছে, চলাচল করা যাচ্ছে না"),
    ],
    "Health": [
        ("en", "No doctor at {v} health centre for {n} days"),
        ("mixed", "{v} swasthya kendre doctor ashchen na"),
        ("bn", "{v} স্বাস্থ্যকেন্দ্রে {n} দিন ডাক্তার আসছেন না"),
    ],
    "Ration": [
        ("en", "Ration shop in {v} has not given rice for {n} weeks"),
        ("bn", "{v} রেশন দোকানে {n} সপ্তাহ চাল দেওয়া হয়নি"),
    ],
    "Pension": [
        ("en", "Old age pension not received for {n} months, {v}"),
        ("bn", "বার্ধক্য ভাতা {n} মাস ধরে পাচ্ছি না, {v}"),
    ],
    "Sanitation": [
        ("en", "Drain blocked in {v}, dirty water on the road"),
        ("bn", "{v} এ ড্রেন বন্ধ, নোংরা জল রাস্তায়"),
    ],
    "Education": [
        ("en", "Mid-day meal stopped at {v} primary school for {n} days"),
        ("bn", "{v} প্রাথমিক বিদ্যালয়ে {n} দিন মিড ডে মিল বন্ধ"),
    ],
}
SEVERE = {
    "en": "children are falling sick",
    "mixed": "baccha-ra osustho hocche",
    "bn": "শিশুরা অসুস্থ হয়ে পড়ছে",
}
CHANNELS = ["helpline", "portal", "news", "social"]
START = (datetime.now() - timedelta(days=90)).replace(second=0, microsecond=0)  # data ends today

def make(dept, row, when, severe=False):
    lang, tpl = random.choice(T[dept])
    n = random.randint(1, 10)
    name = row.village_bn if lang == "bn" else row.village
    text = tpl.format(v=name, n=n)
    if severe:
        text += ", " + SEVERE[lang]
    urgency = "high" if severe or n >= 7 else ("medium" if n >= 3 else "low")
    escalated = int(random.random() < {"high": 0.6, "medium": 0.25, "low": 0.08}[urgency])
    resolved = when + timedelta(days=random.randint(1, 20 if escalated else 7))
    return dict(text=text, language=lang, channel=random.choice(CHANNELS),
                received_at=when, district=row.district, block=row.block,
                village=row.village, lat=row.lat, lon=row.lon, department=dept,
                urgency_label=urgency, escalated=escalated, resolved_at=resolved)

rows = []
for _ in range(4000):
    row = villages.sample(1).iloc[0]
    when = START + timedelta(minutes=random.randint(0, 90 * 24 * 60))
    rows.append(make(random.choice(list(T)), row, when, severe=random.random() < 0.1))

# Plant 3 hotspot events: 15 complaints in one village within 48 hours
for dept in ["Water", "Electricity", "Health"]:
    row = villages.sample(1).iloc[0]
    t0 = START + timedelta(days=random.randint(20, 80))
    for _ in range(15):
        rows.append(make(dept, row, t0 + timedelta(hours=random.randint(0, 48)), severe=True))

df = pd.DataFrame(rows).sort_values("received_at").reset_index(drop=True)
df.insert(0, "complaint_id", [f"C-{i:06d}" for i in range(len(df))])
df.to_csv("data/complaints.csv", index=False)
print(df.department.value_counts())
