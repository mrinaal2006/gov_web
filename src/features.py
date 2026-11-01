import numpy as np
import pandas as pd

SEVERE = ["sick", "hospital", "death", "died", "child", "fire", "electrocut", "flood",
          "osustho", "baccha", "morche", "অসুস্থ", "শিশু", "হাসপাতাল", "মৃত্যু"]

def add_repeat_7d(df):
    """How many earlier complaints of the same type came from the same village in 7 days."""
    df = df.sort_values("received_at").reset_index(drop=True)
    df["repeat_7d"] = 0
    for _, g in df.groupby(["village", "department"]):
        t = g["received_at"].values
        start = np.searchsorted(t, t - np.timedelta64(7, "D"))
        df.loc[g.index, "repeat_7d"] = np.arange(len(g)) - start
    return df

def build_features(df, dept_proba, classes):
    X = pd.DataFrame(dept_proba, columns=[f"p_{c}" for c in classes], index=df.index)
    low = df.text.str.lower()
    X["severe_hits"] = low.apply(lambda t: sum(k in t for k in SEVERE))
    X["length"] = df.text.str.len()
    X["repeat_7d"] = df.repeat_7d
    X["hour"] = pd.to_datetime(df.received_at).dt.hour
    X["news_or_social"] = df.channel.isin(["news", "social"]).astype(int)
    return X
