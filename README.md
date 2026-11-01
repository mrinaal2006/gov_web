# Samasya Radar

Sorts citizen complaints in Bengali, English and Banglish by department, finds the village,
scores urgency, and flags hotspots on a district dashboard.

## Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/generate_data.py
python src/train_classifier.py
python src/train_urgency.py
python src/build_db.py
streamlit run dashboard/app.py
```

- API: `uvicorn api.main:app --reload`, then open `http://127.0.0.1:8000/docs`
- Weekly PDF: `python src/report.py`
- MuRIL: run `src/train_muril.py` on Colab with a GPU, with `complaints.csv` and `real_test.csv` uploaded

On Windows, keep the project in a short path such as `C:\projects\samasya-radar`. Inside very
long paths, `pyarrow` and `fonttools` fail with "The filename or extension is too long".

## Data

`data/villages.csv` covers 42 villages in Birbhum district.

- Names, coordinates and blocks come from OpenStreetMap (place=village nodes inside block boundaries).
- Not yet checked against the LGD directory.
- `village_bn` comes from OpenStreetMap for Bimgarh, Purandapur, Ahmadpur, Beluti, Bipratikuri,
  Mayureswar, Kashtagra, Nalhati and Lohapur. The other 33 are hand transliterations and need
  checking by a Bengali reader.

`data/complaints.csv` is synthetic. `data/real_test.csv` must hold 300+ complaints written by real
people, with columns `text,department`, using these labels: Water, Electricity, Roads, Health,
Ration, Pension, Sanitation, Education. `train_classifier.py` reports on it when the file exists.
