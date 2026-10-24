import os
import stat
import time
import base64
import hashlib
import hmac
import json
import secrets
import logging
from collections import defaultdict
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import Candidate

logger = logging.getLogger("interview_trainer.security")

# Maximum allowed payload size: 512 KB
MAX_PAYLOAD_BYTES = 512 * 1024

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies security headers to prevent XSS, clickjacking, MIME-sniffing, and tampering.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Content Security Policy (allows Tailwind CDN, Mermaid CDN, and Google Fonts)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window IP rate limiter to defend against denial-of-service (DoS)
    and automated abuse of code execution sandboxes.
    """
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_history: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only rate-limit resource-intensive POST endpoints (sandboxes, turns)
        path = request.url.path
        if request.method == "POST" and (path.startswith("/api/v1/sandbox/") or path.startswith("/api/v1/interview/")):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            cutoff = now - self.window_seconds

            # Filter old requests
            history = self.request_history[client_ip]
            self.request_history[client_ip] = [ts for ts in history if ts > cutoff]

            if len(self.request_history[client_ip]) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {path}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down to prevent sandbox abuse."}
                )

            self.request_history[client_ip].append(now)

        return await call_next(request)


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    """
    Guards the server against memory exhaustion and buffer overflows by enforcing
    strict maximum payload size limits.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"Payload too large. Maximum allowed size is {MAX_PAYLOAD_BYTES // 1024} KB."}
                )
        return await call_next(request)


def secure_db_file_permissions(filepath: str):
    """
    Ensures the SQLite database file cannot be accessed or tampered with by other OS users.
    Restricts permissions to owner read/write only (0600).
    """
    if os.path.exists(filepath):
        try:
            os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)
            logger.info(f"Secured database file permissions (0600) on {filepath}")
        except Exception as e:
            logger.warning(f"Could not adjust permissions for {filepath}: {e}")


# ==========================================
# User Authentication & Token Cryptography
# ==========================================

http_bearer = HTTPBearer(auto_error=False)
SECRET_KEY = getattr(settings, "SECRET_KEY", "cogniprep-pro-mnc-technical-interviews-secret-key-2026")
PBKDF2_ITERATIONS = 100_000

def hash_password(plain_password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS
    )
    return f"pbkdf2:sha256:{PBKDF2_ITERATIONS}${salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored pbkdf2 hash."""
    if not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        meta, salt, stored_hash = parts
        iterations = int(meta.split(":")[-1])
        key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return hmac.compare_digest(key.hex(), stored_hash)
    except Exception:
        return False

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding and padding < 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s.encode("utf-8"))

def create_access_token(data: dict, expires_minutes: int = 10080) -> str:
    """Generates an RFC 7519 compliant HMAC-SHA256 JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + (expires_minutes * 60)
    payload["iat"] = int(time.time())

    hdr_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{hdr_b64}.{payload_b64}"

    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{signing_input}.{sig_b64}"

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT token signature and expiration."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        hdr_b64, payload_b64, sig_b64 = parts
        signing_input = f"{hdr_b64}.{payload_b64}"
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        provided_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload.get("exp", 0) < time.time():
            return None

        return payload
    except Exception:
        return None

def get_optional_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> Optional[Candidate]:
    """Resolves authenticated candidate if Bearer token is provided and valid; returns None for guest."""
    if not auth or not auth.credentials:
        return None
    payload = decode_access_token(auth.credentials)
    if not payload:
        return None
    candidate_id = payload.get("sub")
    if not candidate_id:
        return None
    try:
        return db.query(Candidate).filter(Candidate.id == int(candidate_id)).first()
    except Exception:
        return None

def get_current_user(
    user: Optional[Candidate] = Depends(get_optional_current_user)
) -> Candidate:
    """Requires authentication; raises 401 if unauthenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in or register to access your profile.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
