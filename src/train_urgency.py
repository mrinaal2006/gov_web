import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_predict, train_test_split
from features import add_repeat_7d, build_features
from preprocess import clean

df = pd.read_csv("data/complaints.csv", parse_dates=["received_at"])
df["text"] = df.text.map(clean)
df = add_repeat_7d(df)

clf = joblib.load("models/dept_clf.joblib")
# out-of-fold probabilities, so the urgency model never sees over-confident scores
proba = cross_val_predict(clf, df.text, df.department, cv=5, method="predict_proba")
X = build_features(df, proba, sorted(df.department.unique()))
y = df.escalated

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
model = LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31)
model.fit(X_tr, y_tr)
print("ROC-AUC:", roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]))
joblib.dump(model, "models/urgency.joblib")
