"""One small wrapper over Postgres (deployed) and SQLite (local). Times are UTC ISO-8601 text."""
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config, security

SCHEMA = [
    """create table if not exists complaints (
        id text primary key, text text not null, language text, channel text,
        received_at text not null, due_at text not null, resolved_at text,
        district text, block text, village text, lat real, lon real, village_source text,
        department text, department_confidence real, urgency integer, needs_review integer not null,
        status text not null, contact_name text, contact_phone text, consent_at text)""",
    "create index if not exists complaints_received on complaints (received_at)",
    "create index if not exists complaints_place on complaints (village, department, received_at)",
    """create table if not exists events (
        id text primary key, complaint_id text not null references complaints (id),
        created_at text not null, kind text not null, status text, public_message text,
        internal_note text, officer_email text)""",
    "create index if not exists events_complaint on events (complaint_id, created_at)",
    """create table if not exists officers (
        email text primary key, name text not null, password_hash text not null,
        role text not null, active integer not null, created_at text not null)""",
    """create table if not exists officer_invites (
        email text primary key, name text not null, role text not null, code_hash text not null,
        expires_at text not null, attempts integer not null, invited_by text not null, created_at text not null)""",
    """create table if not exists password_resets (
        email text primary key, code_hash text not null, expires_at text not null,
        attempts integer not null, created_at text not null)""",
    """create table if not exists rate_limits (
        rl_key text not null, bucket text not null, hits integer not null,
        primary key (rl_key, bucket))""",
]

_ready = False
_lock = threading.Lock()


class NotConfigured(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


class Connection:
    def __init__(self, raw, postgres):
        self.raw, self.postgres = raw, postgres

    def rows(self, sql, params=()):
        cursor = self.raw.execute(sql.replace("?", "%s") if self.postgres else sql, params)
        return [dict(r) for r in cursor.fetchall()] if cursor.description else []

    def one(self, sql, params=()):
        found = self.rows(sql, params)
        return found[0] if found else None

    def run(self, sql, params=()):
        self.raw.execute(sql.replace("?", "%s") if self.postgres else sql, params)


def _open():
    if config.DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row

        return Connection(psycopg.connect(config.DATABASE_URL, row_factory=dict_row, prepare_threshold=None,
                                          connect_timeout=10), True)
    if config.ON_VERCEL:
        raise NotConfigured("DATABASE_URL is not set")
    raw = sqlite3.connect(config.ROOT / "portal.db", timeout=20)
    raw.row_factory = sqlite3.Row
    raw.execute("pragma foreign_keys = on")
    return Connection(raw, False)


def _prepare(con):
    for statement in SCHEMA:
        con.run(statement)
    # Only for an empty table, so a removed admin is not recreated on the next start
    if config.ADMIN_EMAIL and len(config.ADMIN_PASSWORD) >= 8 and not con.one("select email from officers limit 1"):
        con.run("insert into officers (email, name, password_hash, role, active, created_at) "
                "values (?, ?, ?, 'admin', 1, ?) on conflict (email) do nothing",
                (config.ADMIN_EMAIL, "Administrator", security.hash_password(config.ADMIN_PASSWORD), iso(now())))


@contextmanager
def connect():
    global _ready
    con = _open()
    try:
        if not _ready:
            with _lock:
                if not _ready:
                    _prepare(con)
                    con.raw.commit()
                    _ready = True
        yield con
        con.raw.commit()
    except Exception:
        con.raw.rollback()
        raise
    finally:
        con.raw.close()


def allow(con, key, limit, bucket):
    """Counts one attempt for key in this time bucket. False once it is over the limit."""
    row = con.one("insert into rate_limits (rl_key, bucket, hits) values (?, ?, 1) "
                  "on conflict (rl_key, bucket) do update set hits = rate_limits.hits + 1 returning hits",
                  (key, bucket))
    return row["hits"] <= limit
