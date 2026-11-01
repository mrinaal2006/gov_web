import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

def village_spikes(df, window="48h", min_count=8):
    alerts = []
    for (village, dept), g in df.groupby(["village", "department"]):
        counts = (g.set_index("received_at").sort_index()
                   .assign(one=1)["one"].rolling(window).sum())
        if counts.max() >= min_count:
            alerts.append({"village": village, "department": dept,
                           "peak_count": int(counts.max()), "peak_time": counts.idxmax(),
                           "lat": g.lat.iloc[0], "lon": g.lon.iloc[0]})
    return pd.DataFrame(alerts)

def area_clusters(df, hours=48, radius_km=3, min_samples=8):
    recent = df[df.received_at >= df.received_at.max() - pd.Timedelta(hours=hours)]
    out = []
    for dept, g in recent.dropna(subset=["lat", "lon"]).groupby("department"):
        if len(g) < min_samples:
            continue
        labels = DBSCAN(eps=radius_km / 6371, min_samples=min_samples,
                        metric="haversine").fit_predict(np.radians(g[["lat", "lon"]].values))
        for lab in set(labels) - {-1}:
            c = g[labels == lab]
            out.append({"department": dept, "count": len(c),
                        "villages": ", ".join(sorted(c.village.unique())),
                        "lat": c.lat.mean(), "lon": c.lon.mean()})
    return pd.DataFrame(out)
