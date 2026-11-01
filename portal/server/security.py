import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from . import config

SESSION_HOURS = 8
# Local runs without .env.local still work, with sessions that end on restart
_secret = (config.SESSION_SECRET or ("" if config.ON_VERCEL else secrets.token_hex(32))).encode()


def configured():
    return len(_secret) >= 32


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"{salt.hex()}${digest.hex()}"


def check_password(password, stored):
    salt, digest = stored.split("$")
    found = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1, dklen=32)
    return hmac.compare_digest(found.hex(), digest)


def _sign(body):
    return hmac.new(_secret, body, hashlib.sha256).hexdigest()


def password_stamp(password_hash):
    """Goes in the session, so changing a password ends every session made with the old one."""
    return _sign(password_hash.encode())[:16]


def make_token(email, password_hash):
    body = base64.urlsafe_b64encode(json.dumps({"email": email, "pw": password_stamp(password_hash),
                                                "exp": time.time() + SESSION_HOURS * 3600}).encode())
    return f"{body.decode()}.{_sign(body)}"


def read_token(token):
    """Returns the session's contents, or None if it is forged or out of date."""
    try:
        body, signature = token.split(".")
        if not configured() or not hmac.compare_digest(_sign(body.encode()), signature):
            return None
        data = json.loads(base64.urlsafe_b64decode(body))
        return data if data["exp"] > time.time() and "email" in data and "pw" in data else None
    except (ValueError, KeyError, AttributeError):
        return None


def private_key(value):
    """Rate limits store this instead of the visitor's IP address."""
    return hmac.new(_secret or b"unset", value.encode(), hashlib.sha256).hexdigest()[:32]


def verification_code():
    return f"{secrets.randbelow(10**6):06d}"


def code_hash(email, code):
    return hmac.new(_secret, f"{email}:{code}".encode(), hashlib.sha256).hexdigest()


def code_matches(email, code, stored):
    return hmac.compare_digest(code_hash(email, code), stored)


def tracking_id():
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    return "SR-" + "".join(secrets.choice(alphabet) for _ in range(10))
