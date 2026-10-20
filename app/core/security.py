import os
import stat
import time
import logging
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

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
