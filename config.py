import json
import os
from typing import ClassVar

from flask import current_app
from tna_utilities import strtobool

DEFAULT_STATUS_PAGE_CACHE_DURATION = 15


class Features:
    pass


class Production(Features):
    CONTAINER_IMAGE: str = os.environ.get("CONTAINER_IMAGE", "")
    BUILD_VERSION: str = os.environ.get("BUILD_VERSION", "")
    TNA_FRONTEND_VERSION: str = ""
    try:
        package_lock_json_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            "package-lock.json",
        )
        with open(package_lock_json_path) as package_json:
            data = json.load(package_json)
            TNA_FRONTEND_VERSION: str = (
                data.get("packages", {})
                .get("node_modules/@nationalarchives/frontend", {})
                .get("version", "")
            )
    except Exception:
        current_app.logger.exception("Error reading the version of TNA Frontend")

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")

    DEBUG: bool = False
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_SAMPLE_RATE: float = float(os.getenv("SENTRY_SAMPLE_RATE", "0.1"))

    COOKIE_DOMAIN: str = os.environ.get("COOKIE_DOMAIN", ".nationalarchives.gov.uk")
    COOKIE_PREFERENCES_URL: str = os.environ.get("COOKIE_PREFERENCES_URL", "/cookies/")

    CSP_REPORT_URI: str = os.environ.get("CSP_REPORT_URI", "")
    if CSP_REPORT_URI and BUILD_VERSION:
        CSP_REPORT_URI += f"&sentry_release={BUILD_VERSION}" if BUILD_VERSION else ""
    CONTENT_SECURITY_POLICY: ClassVar[dict] = {
        "connect-src": os.environ.get("CSP_CONNECT_SRC", "").split(","),
        "font-src": os.environ.get("CSP_FONT_SRC", "").split(","),
        "frame-src": os.environ.get("CSP_FRAME_SRC", "").split(","),
        "frame-ancestors": os.environ.get("CSP_FRAME_ANCESTORS", "").split(","),
        "img-src": os.environ.get("CSP_IMG_SRC", "").split(","),
        "media-src": os.environ.get("CSP_MEDIA_SRC", "").split(","),
        "report-uri": CSP_REPORT_URI,
        "script-src": os.environ.get("CSP_SCRIPT_SRC", "").split(","),
        "style-src": os.environ.get("CSP_STYLE_SRC", "").split(","),
        "worker-src": os.environ.get("CSP_WORKER_SRC", "").split(","),
    }
    FORCE_HTTPS: bool = strtobool(os.getenv("FORCE_HTTPS", "False"))
    PREFERRED_URL_SCHEME: str = os.getenv("PREFERRED_URL_SCHEME", "https")

    CACHE_TYPE: str = "FileSystemCache"
    CACHE_DEFAULT_TIMEOUT: int = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "900"))
    STATUS_PAGE_REFRESH_SECONDS: int = int(
        os.environ.get("STATUS_PAGE_REFRESH_SECONDS", "60")
    )
    STATUS_PAGE_CACHE_DURATION: int = int(
        os.environ.get("STATUS_PAGE_CACHE_DURATION", DEFAULT_STATUS_PAGE_CACHE_DURATION)
    )
    CACHE_IGNORE_ERRORS: bool = True
    CACHE_DIR: str = os.environ.get("CACHE_DIR", "/tmp")
    CACHE_REDIS_URL: str = os.environ.get("CACHE_REDIS_URL", "")

    UPTIME_KUMA_URL: str = os.environ.get("UPTIME_KUMA_URL", "").rstrip("/")
    UPTIME_KUMA_JWT: str = os.environ.get("UPTIME_KUMA_JWT", "")
    UPTIME_KUMA_STATUS_PAGE_SLUG: str = os.environ.get(
        "UPTIME_KUMA_STATUS_PAGE_SLUG", ""
    )

    DETAILED_SERVICE_REPORT_HOURS: int = int(
        os.environ.get("DETAILED_SERVICE_REPORT_HOURS", "720")
    )  # 30 days


class Staging(Production):
    DEBUG: bool = strtobool(os.getenv("DEBUG", "False"))

    SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1"))

    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "120"))


class Develop(Production):
    DEBUG: bool = strtobool(os.getenv("DEBUG", "False"))

    SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0"))

    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "1"))


class Test(Production):
    ENVIRONMENT_NAME: str = "test"

    SECRET_KEY: str = "abc123"
    DEBUG: bool = True
    TESTING: bool = True
    EXPLAIN_TEMPLATE_LOADING: bool = True

    SENTRY_DSN = ""
    SENTRY_SAMPLE_RATE = 0

    CACHE_TYPE: str = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT: int = 1

    FORCE_HTTPS: bool = False
    PREFERRED_URL_SCHEME: str = "http"
