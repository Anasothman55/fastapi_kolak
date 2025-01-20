import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Disable uvicorn access logs
logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.WARNING)  # Set to a level that prevents detailed logging


class CustomMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "App"
    return response

def register_middleware(app: FastAPI):

    # Register CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register TrustedHost middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["127.0.0.1", "localhost"],
    )

    app.add_middleware(CustomMiddleware)
