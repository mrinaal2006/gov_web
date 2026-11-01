import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ON_VERCEL = bool(os.environ.get("VERCEL"))

# Local settings only; on Vercel these come from the project's environment variables
env_file = ROOT / ".env.local"
if not ON_VERCEL and env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

DATABASE_URL = os.environ.get("DATABASE_URL", "")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Sends officer verification codes
SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "").strip()

SERVICE_NAME = os.environ.get("SERVICE_NAME", "Samasya Radar")
# Whoever runs the site, shown in the footer
OPERATOR_NAME = os.environ.get("OPERATOR_NAME", "").strip()
OPERATOR_CONTACT = os.environ.get("OPERATOR_CONTACT", "").strip()
RESPONSE_DAYS = int(os.environ.get("RESPONSE_DAYS", "7"))
# Per connection. Many people can share one connection, such as a Wi-Fi network or a helpline office.
COMPLAINTS_PER_HOUR = int(os.environ.get("COMPLAINTS_PER_HOUR", "20"))
