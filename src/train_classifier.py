from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from preprocess import clean

df = pd.read_csv("data/complaints.csv")
df["text"] = df.text.map(clean)
X_tr, X_te, y_tr, y_te = train_test_split(df.text, df.department, test_size=0.2,
                                          stratify=df.department, random_state=42)

clf = Pipeline([
    ("tfidf", FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2)),
    ])),
    ("lr", LogisticRegression(max_iter=2000, class_weight="balanced")),
])
clf.fit(X_tr, y_tr)
print(classification_report(y_te, clf.predict(X_te)))

if Path("data/real_test.csv").exists():
    real = pd.read_csv("data/real_test.csv")   # human-written test set
    print(classification_report(real.department, clf.predict(real.text.map(clean))))
else:
    print("data/real_test.csv not found: no real-world score yet. The numbers above are synthetic.")

joblib.dump(clf, "models/dept_clf.joblib")
