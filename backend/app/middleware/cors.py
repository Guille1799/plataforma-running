"""
cors.py - Custom CORS middleware for Vercel domain validation
"""

from fastapi import Request, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
import re


class VercelCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware that validates Vercel preview URLs dynamically.
    
    Allows:
    - Specific production domain: https://plataforma-running.vercel.app
    - All Vercel preview URLs: *.vercel.app
    - Localhost for development
    """
    
    def __init__(
        self,
        app,
        allowed_origins: List[str],
        allow_credentials: bool = False,
        allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers: List[str] = ["*"],
        max_age: int = 600,
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.max_age = max_age
    
    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed.
        
        Args:
            origin: Request origin header value
            
        Returns:
            True if origin is allowed, False otherwise
        """
        # Check exact matches first
        if origin in self.allowed_origins:
            return True
        
        # Check if origin is localhost (for development)
        # Pattern: http://localhost:* or http://127.0.0.1:*
        localhost_pattern = r'^http://(localhost|127\.0\.0\.1)(:\d+)?$'
        if re.match(localhost_pattern, origin):
            return True
        
        # Check if origin is a Vercel preview URL (*.vercel.app)
        # Pattern: https://*.vercel.app or https://*-*.vercel.app
        vercel_pattern = r'^https://[a-zA-Z0-9-]+(-[a-zA-Z0-9]+)*\.vercel\.app$'
        if re.match(vercel_pattern, origin):
            return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Handle CORS headers in requests."""
        origin = request.headers.get("origin")
        
        # #region agent log
        import json
        import os
        from datetime import datetime
        DEBUG_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".cursor", "debug.log")
        try:
            log_dir = os.path.dirname(DEBUG_LOG_PATH)
            os.makedirs(log_dir, exist_ok=True)
            log_entry = {
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "location": "cors.py:dispatch",
                "message": "[CORS] Request received",
                "level": "info",
                "data": {"origin": origin, "method": request.method, "path": str(request.url.path), "step": "start"},
                "sessionId": "debug-session",
                "runId": "cors-debug",
                "hypothesisId": "H1"
            }
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                f.flush()
        except:
            pass
        # #endregion
        
        # Handle preflight OPTIONS request
        if request.method == "OPTIONS":
            is_allowed = origin and self.is_origin_allowed(origin)
            # #region agent log
            try:
                log_entry = {
                    "timestamp": int(datetime.utcnow().timestamp() * 1000),
                    "location": "cors.py:dispatch",
                    "message": "[CORS] OPTIONS preflight check",
                    "level": "info",
                    "data": {"origin": origin, "is_allowed": is_allowed, "step": "options_check"},
                    "sessionId": "debug-session",
                    "runId": "cors-debug",
                    "hypothesisId": "H1"
                }
                with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                    f.flush()
            except:
                pass
            # #endregion
            if is_allowed:
                headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                    "Access-Control-Allow-Headers": ", ".join(self.allow_headers) if isinstance(self.allow_headers, list) else "*",
                    "Access-Control-Max-Age": str(self.max_age),
                }
                if self.allow_credentials:
                    headers["Access-Control-Allow-Credentials"] = "true"
                return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
            else:
                return Response(status_code=status.HTTP_403_FORBIDDEN)
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to response if origin is allowed
        is_allowed = origin and self.is_origin_allowed(origin)
        # #region agent log
        try:
            log_entry = {
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "location": "cors.py:dispatch",
                "message": "[CORS] Adding headers to response",
                "level": "info",
                "data": {"origin": origin, "is_allowed": is_allowed, "status_code": response.status_code, "step": "add_headers"},
                "sessionId": "debug-session",
                "runId": "cors-debug",
                "hypothesisId": "H1"
            }
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                f.flush()
        except:
            pass
        # #endregion
        if is_allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "*"
        
        return response
