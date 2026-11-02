import re
import smtplib
import uuid
from datetime import timedelta, timezone
from typing import Optional
from urllib.parse import quote

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from server import config, db, gemini, mailer, nlp, security
from server.db import iso, now

app = FastAPI(title="Samasya Radar Portal", docs_url=None, redoc_url=None, openapi_url=None)

STATUSES = {"received", "in_progress", "resolved", "rejected"}
PHONE = re.compile(r"^(\+91[\-\s]?)?[6-9]\d{9}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CODE_MINUTES = 30
CODE_ATTEMPTS = 5
REVIEW_BELOW = 0.6
HIGH_URGENCY = 70
HOTSPOT_MIN = 8
IST = timezone(timedelta(hours=5, minutes=30))
HEADERS = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "strict-origin-when-cross-origin",
           "Content-Security-Policy": "default-src 'self'; img-src 'self' data: https://tile.openstreetmap.org; "
                                      "style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'self'; "
                                      "form-action 'self'"}


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.update(HEADERS)
    # Pages may be kept, but the browser must check for a newer version before showing them again
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    return response


@app.exception_handler(db.NotConfigured)
def not_configured(request, exc):
    return JSONResponse({"detail": "The service database has not been set up yet."}, status_code=503)


def client_key(request: Request):
    ip = request.headers.get("x-real-ip") if config.ON_VERCEL else None
    return security.private_key(ip or (request.client.host if request.client else "unknown"))


def department_list():
    return nlp._load("department.json")["classes"]


class NewComplaint(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    village: Optional[str] = Field(default=None, max_length=100)
    contact_name: Optional[str] = Field(default=None, max_length=100)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    consent: bool
    website: Optional[str] = None  # hidden field that only bots fill in


class Login(BaseModel):
    email: str = Field(max_length=200)
    password: str = Field(max_length=200)


class Update(BaseModel):
    status: Optional[str] = None
    department: Optional[str] = None
    public_message: Optional[str] = Field(default=None, max_length=2000)
    internal_note: Optional[str] = Field(default=None, max_length=2000)


class NewOfficer(BaseModel):
    email: str = Field(max_length=200)
    name: str = Field(min_length=2, max_length=100)
    role: str = "officer"


class Analyze(BaseModel):
    text: str = Field(min_length=3, max_length=2000)
    village: Optional[str] = Field(default=None, max_length=100)


class ChangePassword(BaseModel):
    current_password: str = Field(max_length=200)
    new_password: str = Field(max_length=200)


class Forgot(BaseModel):
    email: str = Field(max_length=200)


class Activation(BaseModel):
    email: str = Field(max_length=200)
    code: str = Field(max_length=10)
    password: str = Field(max_length=200)


def similar_count(con, department, village, moment):
    return con.one("select count(*) as n from complaints where village = ? and department = ? "
                   "and received_at >= ?", (village, department, iso(moment - timedelta(days=7))))["n"]


def assess_urgency(text, probabilities, department, village, repeat, moment):
    """Returns the score, where it came from, and Gemini's reason. Call outside a database connection: it can wait on Gemini."""
    answer = gemini.score(text, department, village, repeat)
    if answer:
        return answer["score"], "gemini", answer["reason"]
    return round(nlp.urgency_score(text, probabilities, repeat, moment.astimezone(IST).hour) * 100), "local", None


def check_code(con, table, email, code, moment):
    """Returns the row if the code is right. A wrong code uses up an attempt, and the last one deletes the row."""
    row = con.one(f"select * from {table} where email = ?", (email,))
    if not row:
        return None
    if row["expires_at"] >= iso(moment) and security.code_matches(email, code, row["code_hash"]):
        return row
    if row["attempts"] + 1 >= CODE_ATTEMPTS:
        con.run(f"delete from {table} where email = ?", (email,))
    else:
        con.run(f"update {table} set attempts = attempts + 1 where email = ?", (email,))
    return None


def add_event(con, complaint_id, kind, status=None, public_message=None, internal_note=None, officer=None):
    con.run("insert into events (id, complaint_id, created_at, kind, status, public_message, internal_note, "
            "officer_email) values (?, ?, ?, ?, ?, ?, ?, ?)",
            (uuid.uuid4().hex, complaint_id, iso(now()), kind, status, public_message, internal_note, officer))


@app.get("/api/health")
def health():
    if config.ON_VERCEL and not config.DATABASE_URL:
        return JSONResponse({"status": "database_url_missing", "officer_login_ready": security.configured()},
                            status_code=503)
    with db.connect() as con:
        con.one("select 1 as ok")
    return {"status": "ok", "officer_login_ready": security.configured()}


@app.get("/api/config")
def site_config():
    return {"service_name": config.SERVICE_NAME, "operator": config.OPERATOR_NAME or None,
            "contact": config.OPERATOR_CONTACT or None, "live": bool(config.OPERATOR_NAME),
            "response_days": config.RESPONSE_DAYS,
            "villages": [{"village": v["village"], "village_bn": v["village_bn"], "block": v["block"]}
                         for v in nlp.villages()]}


@app.post("/api/complaints", status_code=201)
def file_complaint(body: NewComplaint, request: Request):
    if not body.consent:
        raise HTTPException(400, "Please agree to the privacy notice before submitting.")
    if body.website:
        raise HTTPException(400, "This submission could not be accepted.")
    phone = (body.contact_phone or "").strip() or None
    if phone and not PHONE.match(phone):
        raise HTTPException(400, "Please enter a valid 10-digit mobile number, or leave it blank.")
    text = nlp.clean(body.text)
    if len(text) < 10:
        raise HTTPException(400, "Please describe the problem in a little more detail.")

    place = next((v for v in nlp.villages() if v["village"] == body.village), None)
    source = "citizen" if place else None
    if not place:
        place = nlp.find_place(text)
        source = "text" if place else None
    place = place or {}

    moment = now()
    probabilities = nlp.department_probabilities(text)
    department = max(probabilities, key=probabilities.get)
    confidence = probabilities[department]
    with db.connect() as con:
        if not db.allow(con, f"file:{client_key(request)}", config.COMPLAINTS_PER_HOUR, moment.strftime("%Y%m%d%H")):
            con.raw.commit()
            raise HTTPException(429, "Too many complaints from this connection. Please try again in an hour.")
        repeat = similar_count(con, department, place.get("village"), moment)
    urgency, source, reason = assess_urgency(text, probabilities, department, place.get("village"), repeat, moment)
    with db.connect() as con:
        complaint_id = security.tracking_id()
        due = moment + timedelta(days=config.RESPONSE_DAYS)
        con.run("insert into complaints (id, text, language, channel, received_at, due_at, district, block, village, "
                "lat, lon, village_source, department, department_confidence, urgency, needs_review, status, "
                "contact_name, contact_phone, consent_at) values (?, ?, ?, 'portal', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "?, 'received', ?, ?, ?)",
                (complaint_id, text, nlp.detect_language(text), iso(moment), iso(due), place.get("district"),
                 place.get("block"), place.get("village"), place.get("lat"), place.get("lon"), source, department,
                 confidence, urgency, int(confidence < REVIEW_BELOW or not place),
                 (body.contact_name or "").strip() or None, phone, iso(moment)))
        add_event(con, complaint_id, "created", status="received")
        if reason:
            add_event(con, complaint_id, "urgency", internal_note=reason)
    return {"id": complaint_id, "department": department, "village": place.get("village"),
            "received_at": iso(moment), "due_at": iso(due)}


@app.get("/api/complaints/{complaint_id}")
def track(complaint_id: str, request: Request):
    moment = now()
    with db.connect() as con:
        if not db.allow(con, f"track:{client_key(request)}", 60, moment.strftime("%Y%m%d%H")):
            con.raw.commit()
            raise HTTPException(429, "Too many lookups. Please try again in an hour.")
        row = con.one("select id, text, department, village, block, status, received_at, due_at, resolved_at "
                      "from complaints where id = ?", (complaint_id.strip().upper(),))
        if not row:
            raise HTTPException(404, "No complaint found with that tracking ID.")
        events = con.rows("select created_at, status, public_message from events where complaint_id = ? "
                          "and (public_message is not null or kind = 'created' or kind = 'status') "
                          "order by created_at, kind", (row["id"],))
    row["overdue"] = row["status"] in ("received", "in_progress") and row["due_at"] < iso(moment)
    row["timeline"] = events
    return row


def officer(sr_session: Optional[str] = Cookie(default=None)):
    session = security.read_token(sr_session) if sr_session else None
    if not session:
        raise HTTPException(401, "Please sign in.")
    with db.connect() as con:
        row = con.one("select email, name, role, password_hash from officers where email = ? and active = 1",
                      (session["email"],))
    if not row or security.password_stamp(row.pop("password_hash")) != session["pw"]:
        raise HTTPException(401, "Please sign in.")
    return row


@app.post("/api/officer/login")
def login(body: Login, request: Request, response: Response):
    if not security.configured():
        raise HTTPException(503, "Officer sign-in has not been set up yet.")
    email, moment = body.email.strip().lower(), now()
    window = f"{moment.strftime('%Y%m%d%H')}{moment.minute // 15}"
    key = f"login:{client_key(request)}:{email}"
    with db.connect() as con:
        allowed = db.allow(con, key, 5, window)
        row = con.one("select password_hash from officers where email = ? and active = 1", (email,))
    if not allowed:
        raise HTTPException(429, "Too many attempts. Please wait 15 minutes.")
    if not row or not security.check_password(body.password, row["password_hash"]):
        raise HTTPException(401, "Email or password is incorrect.")
    with db.connect() as con:  # only failed attempts count towards the limit
        con.run("delete from rate_limits where rl_key = ?", (key,))
    set_session(response, email, row["password_hash"])
    return {"ok": True}


def set_session(response, email, password_hash):
    response.set_cookie("sr_session", security.make_token(email, password_hash),
                        max_age=security.SESSION_HOURS * 3600,
                        httponly=True, samesite="strict", secure=config.ON_VERCEL, path="/")


@app.post("/api/officer/password")
def change_password(body: ChangePassword, response: Response, user=Depends(officer)):
    """Keeps this session going and ends every other one made with the old password."""
    if len(body.new_password) < 12:
        raise HTTPException(400, "Please choose a password of at least 12 characters.")
    if body.new_password == body.current_password:
        raise HTTPException(400, "Your new password must be different from your current one.")
    email, moment = user["email"], now()
    key = f"change:{security.private_key(email)}"
    window = f"{moment.strftime('%Y%m%d%H')}{moment.minute // 15}"
    with db.connect() as con:
        allowed = db.allow(con, key, 5, window)
        stored = con.one("select password_hash from officers where email = ?", (email,))["password_hash"]
    if not allowed:
        raise HTTPException(429, "Too many attempts. Please wait 15 minutes.")
    if not security.check_password(body.current_password, stored):
        raise HTTPException(400, "Your current password is incorrect.")
    new_hash = security.hash_password(body.new_password)
    with db.connect() as con:
        con.run("update officers set password_hash = ? where email = ?", (new_hash, email))
        con.run("delete from rate_limits where rl_key = ?", (key,))
    set_session(response, email, new_hash)
    return {"ok": True}


FORGOT_REPLY = "If that email belongs to an officer, a reset code has been sent to it."


@app.post("/api/officer/forgot")
def forgot_password(body: Forgot, request: Request):
    """Answers the same for any email, so this cannot be used to find out who is an officer."""
    if not security.configured():
        raise HTTPException(503, "Officer sign-in has not been set up yet.")
    email, moment, code = body.email.strip().lower(), now(), security.verification_code()
    hour = moment.strftime("%Y%m%d%H")
    sent = None
    with db.connect() as con:
        if not db.allow(con, f"forgot:{client_key(request)}", 10, hour):
            con.raw.commit()
            raise HTTPException(429, "Too many requests. Please try again in an hour.")
        row = con.one("select name from officers where email = ? and active = 1", (email,))
        if row and db.allow(con, f"forgot-email:{security.private_key(email)}", 3, hour):
            con.run("insert into password_resets (email, code_hash, expires_at, attempts, created_at) "
                    "values (?, ?, ?, 0, ?) on conflict (email) do update set code_hash = excluded.code_hash, "
                    "expires_at = excluded.expires_at, attempts = 0, created_at = excluded.created_at",
                    (email, security.code_hash(email, code), iso(moment + timedelta(minutes=CODE_MINUTES)), iso(moment)))
            sent = row
    result = {"message": FORGOT_REPLY}
    if sent and config.SMTP_HOST:
        try:
            link = f"{str(request.base_url)}reset.html?email={quote(email)}"
            mailer.send_reset_code(email, sent["name"], code, CODE_MINUTES, link)
        except (smtplib.SMTPException, OSError) as exc:
            print(f"Password reset email failed: {type(exc).__name__}")
    elif sent and not config.ON_VERCEL and request.client and request.client.host in ("127.0.0.1", "::1"):
        result["dev_code"] = code  # no email on this computer, and only this computer can see it
    elif sent:
        print("Password reset requested, but SMTP_HOST is not set, so no code was sent.")
    return result


@app.post("/api/officer/reset")
def reset_password(body: Activation, request: Request):
    if not security.configured():
        raise HTTPException(503, "Officer sign-in has not been set up yet.")
    if len(body.password) < 12:
        raise HTTPException(400, "Please choose a password of at least 12 characters.")
    email, moment = body.email.strip().lower(), now()
    window = f"{moment.strftime('%Y%m%d%H')}{moment.minute // 15}"
    with db.connect() as con:
        allowed = db.allow(con, f"reset:{client_key(request)}", 10, window)
        ok = allowed and check_code(con, "password_resets", email, body.code.strip(), moment) is not None
        if ok:
            con.run("update officers set password_hash = ? where email = ? and active = 1",
                    (security.hash_password(body.password), email))
            con.run("delete from password_resets where email = ?", (email,))
            con.run("delete from rate_limits where rl_key = ?", (f"login:{client_key(request)}:{email}",))
    if not allowed:
        raise HTTPException(429, "Too many attempts. Please wait 15 minutes.")
    if not ok:
        raise HTTPException(400, "That code is wrong or has expired. Please ask for a new one.")
    return {"ok": True}


@app.post("/api/officer/logout")
def logout(response: Response):
    response.delete_cookie("sr_session", path="/")
    return {"ok": True}


@app.get("/api/officer/me")
def me(user=Depends(officer)):
    return user


@app.post("/api/officer/analyze")
def analyze(body: Analyze, user=Depends(officer)):
    """Scores a piece of text the way a real complaint would be scored, without saving anything."""
    text = nlp.clean(body.text)
    probabilities = nlp.department_probabilities(text)
    department = max(probabilities, key=probabilities.get)
    chosen = next((v for v in nlp.villages() if v["village"] == body.village), None)
    place = chosen or nlp.find_place(text) or {}
    moment = now()
    with db.connect() as con:
        repeat = similar_count(con, department, place.get("village"), moment)
    urgency, source, why = assess_urgency(text, probabilities, department, place.get("village"), repeat, moment)
    reasons = []
    if not place:
        reasons.append("no listed village was recognised")
    if probabilities[department] < REVIEW_BELOW:
        reasons.append("the department suggestion is below 60% confidence")
    ranked = sorted(probabilities.items(), key=lambda item: -item[1])[:3]
    return {"text": text, "urgency": urgency, "urgency_source": source, "urgency_reason": why,
            "high": urgency >= HIGH_URGENCY, "department": department,
            "confidence": probabilities[department], "needs_review": bool(reasons), "review_reasons": reasons,
            "departments": [{"name": n, "probability": p} for n, p in ranked],
            "village": place.get("village"), "block": place.get("block"), "language": nlp.detect_language(text),
            "serious_words": nlp.severe_words(text), "similar_7d": repeat}


@app.get("/api/officer/summary")
def summary(days: int = 30, user=Depends(officer)):
    moment = now()
    since = iso(moment - timedelta(days=max(1, min(days, 365))))
    text_now = iso(moment)
    open_states = "('received', 'in_progress')"
    with db.connect() as con:
        totals = con.one(
            f"""select count(*) as complaints,
                sum(case when status in {open_states} then 1 else 0 end) as pending,
                sum(case when status in {open_states} and due_at < ? then 1 else 0 end) as overdue,
                sum(case when status in {open_states} and urgency >= 70 then 1 else 0 end) as high_urgency,
                sum(case when status in {open_states} and needs_review = 1 then 1 else 0 end) as needs_review
                from complaints where received_at >= ?""", (text_now, since))
        hotspots = con.rows(
            "select village, block, department, count(*) as complaints, max(received_at) as latest, "
            "max(lat) as lat, max(lon) as lon from complaints where received_at >= ? and village is not null "
            f"group by village, block, department having count(*) >= {HOTSPOT_MIN} order by complaints desc",
            (iso(moment - timedelta(hours=48)),))
        points = con.rows("select lat, lon, urgency from complaints where received_at >= ? and lat is not null "
                          "order by received_at desc limit 3000", (since,))
        finished = con.rows("select block, department, received_at, resolved_at, status, urgency, due_at "
                            "from complaints where received_at >= ? and block is not null", (since,))
    card = {}
    for row in finished:
        entry = card.setdefault((row["block"], row["department"]),
                                {"block": row["block"], "department": row["department"], "complaints": 0,
                                 "pending": 0, "overdue": 0, "days": []})
        entry["complaints"] += 1
        if row["resolved_at"]:
            start = db.datetime.fromisoformat(row["received_at"].replace("Z", "+00:00"))
            end = db.datetime.fromisoformat(row["resolved_at"].replace("Z", "+00:00"))
            entry["days"].append((end - start).total_seconds() / 86400)
        elif row["status"] in ("received", "in_progress"):
            entry["pending"] += 1
            entry["overdue"] += int(row["due_at"] < text_now)
    scorecard = []
    for entry in card.values():
        taken = entry.pop("days")
        entry["avg_days"] = round(sum(taken) / len(taken), 1) if taken else None
        scorecard.append(entry)
    scorecard.sort(key=lambda e: (-e["overdue"], -e["pending"], e["block"]))
    return {"totals": {k: v or 0 for k, v in totals.items()}, "hotspots": hotspots, "points": points,
            "scorecard": scorecard, "departments": department_list(), "server_time": text_now}


@app.get("/api/officer/complaints")
def complaints(view: str = "pending", department: Optional[str] = None, sort: str = "newest", limit: int = 300,
               user=Depends(officer)):
    filters, params = [], []
    if view == "pending":
        filters.append("status in ('received', 'in_progress')")
    elif view == "overdue":
        filters.append("status in ('received', 'in_progress') and due_at < ?")
        params.append(iso(now()))
    elif view == "review":
        filters.append("status in ('received', 'in_progress') and needs_review = 1")
    elif view == "closed":
        filters.append("status in ('resolved', 'rejected')")
    if department:
        filters.append("department = ?")
        params.append(department)
    where = f"where {' and '.join(filters)}" if filters else ""
    order = "urgency desc, received_at desc" if sort == "urgency" else "received_at desc"
    params.append(max(1, min(limit, 300)))
    with db.connect() as con:
        return con.rows("select id, text, department, department_confidence, village, block, urgency, status, "
                        f"needs_review, received_at, due_at from complaints {where} "
                        f"order by {order} limit ?", params)


@app.get("/api/officer/complaints/{complaint_id}")
def complaint_detail(complaint_id: str, user=Depends(officer)):
    with db.connect() as con:
        row = con.one("select * from complaints where id = ?", (complaint_id,))
        if not row:
            raise HTTPException(404, "Complaint not found.")
        row["events"] = con.rows("select created_at, kind, status, public_message, internal_note, officer_email "
                                 "from events where complaint_id = ? order by created_at, kind", (complaint_id,))
    return row


@app.post("/api/officer/complaints/{complaint_id}")
def update_complaint(complaint_id: str, body: Update, user=Depends(officer)):
    message = (body.public_message or "").strip() or None
    note = (body.internal_note or "").strip() or None
    if body.status and body.status not in STATUSES:
        raise HTTPException(400, "Unknown status.")
    if body.department and body.department not in department_list():
        raise HTTPException(400, "Unknown department.")
    if body.status in ("resolved", "rejected") and not message:
        raise HTTPException(400, "Write the response the citizen will see before closing this complaint.")
    with db.connect() as con:
        row = con.one("select status, department from complaints where id = ?", (complaint_id,))
        if not row:
            raise HTTPException(404, "Complaint not found.")
        email = user["email"]
        if body.department and body.department != row["department"]:
            con.run("update complaints set department = ?, department_confidence = 1, needs_review = 0 where id = ?",
                    (body.department, complaint_id))
            add_event(con, complaint_id, "department", internal_note=f"{row['department']} to {body.department}",
                      officer=email)
        if body.status and body.status != row["status"]:
            closed = body.status in ("resolved", "rejected")
            con.run("update complaints set status = ?, resolved_at = ?, needs_review = 0 where id = ?",
                    (body.status, iso(now()) if closed else None, complaint_id))
            add_event(con, complaint_id, "status", status=body.status, public_message=message, officer=email)
            message = None
        if message:
            add_event(con, complaint_id, "message", public_message=message, officer=email)
        if note:
            add_event(con, complaint_id, "note", internal_note=note, officer=email)
    return complaint_detail(complaint_id, user)


@app.get("/api/officer/officers")
def list_officers(user=Depends(officer)):
    if user["role"] != "admin":
        raise HTTPException(403, "Only an administrator can do this.")
    with db.connect() as con:
        return con.rows("select email, name, role, active from officers order by name")


@app.post("/api/officer/officers", status_code=201)
def add_officer(body: NewOfficer, request: Request, user=Depends(officer)):
    """Creates an invitation and emails its code. The account only exists once the officer enters the code."""
    if user["role"] != "admin":
        raise HTTPException(403, "Only an administrator can do this.")
    if body.role not in ("officer", "admin"):
        raise HTTPException(400, "Unknown role.")
    email = body.email.strip().lower()
    if not EMAIL.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    if config.ON_VERCEL and not config.SMTP_HOST:
        raise HTTPException(503, "Email sending has not been set up, so no code can be sent.")
    moment, code = now(), security.verification_code()
    name = body.name.strip()
    with db.connect() as con:
        if con.one("select email from officers where email = ?", (email,)):
            raise HTTPException(409, "That officer already exists.")
        if not db.allow(con, f"invite:{security.private_key(email)}", 5, moment.strftime("%Y%m%d%H")):
            con.raw.commit()
            raise HTTPException(429, "Too many codes sent to this email. Please try again in an hour.")
        con.run("insert into officer_invites (email, name, role, code_hash, expires_at, attempts, invited_by, created_at) "
                "values (?, ?, ?, ?, ?, 0, ?, ?) on conflict (email) do update set name = excluded.name, "
                "role = excluded.role, code_hash = excluded.code_hash, expires_at = excluded.expires_at, attempts = 0, "
                "invited_by = excluded.invited_by, created_at = excluded.created_at",
                (email, name, body.role, security.code_hash(email, code),
                 iso(moment + timedelta(minutes=CODE_MINUTES)), user["email"], iso(moment)))
        if config.SMTP_HOST:
            link = f"{str(request.base_url)}activate.html?email={quote(email)}"
            try:
                mailer.send_code(email, name, code, CODE_MINUTES, link)
            except (smtplib.SMTPException, OSError) as exc:
                # Leaving the block with an error also undoes the invitation
                raise HTTPException(502, "The email could not be sent. Check the email settings and try again.") from exc
    if config.SMTP_HOST:
        return {"email": email, "sent": True}
    return {"email": email, "sent": False, "dev_code": code}  # local testing only; refused on Vercel above


@app.get("/api/officer/invites")
def list_invites(user=Depends(officer)):
    if user["role"] != "admin":
        raise HTTPException(403, "Only an administrator can do this.")
    with db.connect() as con:
        rows = con.rows("select email, name, role, expires_at from officer_invites order by created_at desc")
    current = iso(now())
    return [{**r, "expired": r["expires_at"] < current} for r in rows]


@app.delete("/api/officer/invites/{email}")
def cancel_invite(email: str, user=Depends(officer)):
    if user["role"] != "admin":
        raise HTTPException(403, "Only an administrator can do this.")
    with db.connect() as con:
        con.run("delete from officer_invites where email = ?", (email.strip().lower(),))
    return {"ok": True}


@app.post("/api/officer/activate")
def activate(body: Activation, request: Request):
    if not security.configured():
        raise HTTPException(503, "Officer sign-in has not been set up yet.")
    if len(body.password) < 12:
        raise HTTPException(400, "Please choose a password of at least 12 characters.")
    email, code, moment = body.email.strip().lower(), body.code.strip(), now()
    # Every failure reads the same, so this cannot be used to find out who was invited
    wrong = "That code is wrong or has expired. Ask your administrator for a new one."
    with db.connect() as con:
        window = f"{moment.strftime('%Y%m%d%H')}{moment.minute // 15}"
        allowed = db.allow(con, f"activate:{client_key(request)}", 10, window)
        row = check_code(con, "officer_invites", email, code, moment) if allowed else None
        ok = row is not None
        if ok:
            con.run("insert into officers (email, name, password_hash, role, active, created_at) "
                    "values (?, ?, ?, ?, 1, ?) on conflict (email) do nothing",
                    (email, row["name"], security.hash_password(body.password), row["role"], iso(moment)))
            con.run("delete from officer_invites where email = ?", (email,))
    if not allowed:
        raise HTTPException(429, "Too many attempts. Please wait 15 minutes.")
    if not ok:
        raise HTTPException(400, wrong)
    return {"ok": True}


@app.delete("/api/officer/officers/{email}")
def remove_officer(email: str, user=Depends(officer)):
    if user["role"] != "admin":
        raise HTTPException(403, "Only an administrator can do this.")
    email = email.strip().lower()
    if email == user["email"]:
        raise HTTPException(400, "You cannot remove your own account.")
    with db.connect() as con:
        if not con.one("select email from officers where email = ?", (email,)):
            raise HTTPException(404, "Officer not found.")
        # Complaint history keeps the officer's email as plain text, so the record of their actions stays
        con.run("delete from officers where email = ?", (email,))
    return {"ok": True}


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse("/index.html", status_code=307)


# Vercel serves public/ from its CDN by itself, so this is for local runs only
if not config.ON_VERCEL:
    app.mount("/", StaticFiles(directory=config.ROOT / "public", html=True), name="public")
