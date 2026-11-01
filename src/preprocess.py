import re

PHONE = re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}")
AADHAAR = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
BENGALI = re.compile(r"[ঀ-৿]")

def mask_pii(text: str) -> str:
    text = AADHAAR.sub("[ID]", text)
    return PHONE.sub("[PHONE]", text)

def detect_language(text: str) -> str:
    share = len(BENGALI.findall(text)) / max(len(text), 1)
    return "bn" if share > 0.3 else ("mixed" if share > 0 else "en")

def clean(text: str) -> str:
    text = mask_pii(str(text))
    return re.sub(r"\s+", " ", text).strip()
