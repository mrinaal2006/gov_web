# Run on Google Colab with a GPU, after uploading complaints.csv and real_test.csv.
import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.metrics import f1_score
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          DataCollatorWithPadding, Trainer, TrainingArguments)

MODEL = "google/muril-base-cased"
df = pd.read_csv("complaints.csv")
labels = sorted(df.department.unique())
l2i = {l: i for i, l in enumerate(labels)}
df["label"] = df.department.map(l2i)

tok = AutoTokenizer.from_pretrained(MODEL)
ds = Dataset.from_pandas(df[["text", "label"]]).train_test_split(test_size=0.2, seed=42)
ds = ds.map(lambda b: tok(b["text"], truncation=True, max_length=128), batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL, num_labels=len(labels),
    id2label={i: l for l, i in l2i.items()}, label2id=l2i)

def metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    return {"f1": f1_score(p.label_ids, preds, average="macro")}

args = TrainingArguments("muril-out", num_train_epochs=3, learning_rate=2e-5,
                         per_device_train_batch_size=16, eval_strategy="epoch",
                         save_strategy="epoch", load_best_model_at_end=True,
                         metric_for_best_model="f1")
trainer = Trainer(model=model, args=args, train_dataset=ds["train"],
                  eval_dataset=ds["test"], data_collator=DataCollatorWithPadding(tok),
                  compute_metrics=metrics)
trainer.train()
trainer.save_model("models/muril_dept")
tok.save_pretrained("models/muril_dept")

# The number to compare with the baseline: macro F1 on the human-written test set
real = pd.read_csv("real_test.csv")
real["label"] = real.department.map(l2i)
real_ds = Dataset.from_pandas(real[["text", "label"]])
real_ds = real_ds.map(lambda b: tok(b["text"], truncation=True, max_length=128), batched=True)
print("real_test:", trainer.evaluate(real_ds))
