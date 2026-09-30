"""
Application configuration.

Loads settings from environment variables. Never hard-code secrets here.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'scanner.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI provider
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "anthropic")  # anthropic | openai | none
    AI_API_KEY = os.environ.get("AI_API_KEY", "")
    AI_MODEL = os.environ.get("AI_MODEL", "claude-sonnet-4-6")

    # Scanner / SSRF protection
    REQUEST_TIMEOUT_SECONDS = float(os.environ.get("REQUEST_TIMEOUT_SECONDS", "8"))
    MAX_REDIRECTS = int(os.environ.get("MAX_REDIRECTS", "5"))
    MAX_RESPONSE_BYTES = int(os.environ.get("MAX_RESPONSE_BYTES", str(2 * 1024 * 1024)))  # 2 MB
    ALLOWED_SCHEMES = {"http", "https"}
    ALLOWED_PORTS = {80, 443, 8080, 8443}  # common web ports only

    # Rate limiting (simple in-memory limiter)
    RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))
    RATE_LIMIT_MAX_SCANS = int(os.environ.get("RATE_LIMIT_MAX_SCANS", "5"))
