import logging
import os
from datetime import UTC, datetime

import sentry_sdk
from flask import Flask
from jinja2 import ChoiceLoader, PackageLoader
from tna_utilities.datetime import get_date_from_string, pretty_date
from tna_utilities.datetime import pretty_datetime as tna_pretty_datetime
from tna_utilities.datetime import seconds_to_duration as tna_seconds_to_duration
from tna_utilities.string import slugify

from app.lib.cache import cache
from app.lib.context_processor import (
    cookie_preference,
    incident_calendar_count,
    incident_calendar_duration,
    incident_calendar_heartbeats,
    now_iso_8601,
    now_iso_8601_date,
    now_pretty,
)
from app.lib.talisman import talisman
from app.lib.template_filters import (
    average_incident_time,
    incident_count,
    longest_incident_time,
    markdown,
    pretty_percentage,
    pretty_uptime_kuma_status,
    previous_incidents,
    seconds_to_time,
    time_ago,
    total_incident_time,
    total_maintenance_time,
)


def create_app(config_class):
    app = Flask(__name__, static_url_path="/status/static")
    app.config.from_object(config_class)

    if app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=app.config.get("SENTRY_DSN"),
            environment=app.config.get("ENVIRONMENT_NAME"),
            release=(
                f"ds-service-status@{app.config.get('BUILD_VERSION')}"
                if app.config.get("BUILD_VERSION")
                else ""
            ),
            sample_rate=app.config.get("SENTRY_SAMPLE_RATE"),
            traces_sample_rate=app.config.get("SENTRY_SAMPLE_RATE"),
            profiles_sample_rate=app.config.get("SENTRY_SAMPLE_RATE"),
        )

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(
        gunicorn_error_logger.level or os.getenv("LOG_LEVEL", "warning").upper()
    )

    cache.init_app(
        app,
        config={
            "CACHE_TYPE": app.config.get("CACHE_TYPE"),
            "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT"),
            "CACHE_IGNORE_ERRORS": app.config.get("CACHE_IGNORE_ERRORS"),
            "CACHE_DIR": app.config.get("CACHE_DIR"),
            "CACHE_REDIS_URL": app.config.get("CACHE_REDIS_URL"),
        },
    )

    talisman.init_app(
        app,
        content_security_policy=app.config["CONTENT_SECURITY_POLICY"],
        allow_google_content_security_policy=True,
        force_https=app.config["FORCE_HTTPS"],
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("tna_frontend_jinja"),
        ]
    )

    def seconds_to_duration(value):
        return tna_seconds_to_duration(value, simplify=True)

    def pretty_datetime(value):
        return tna_pretty_datetime(value, show_seconds=True)

    def date_from_datetime_string(value):
        date_from_value = get_date_from_string(value)
        if not date_from_value:
            return None
        if date_from_value.tzinfo is None:
            date_from_value = date_from_value.replace(tzinfo=UTC)
        return date_from_value.date()

    def any_datetime_string_to_iso_8601_datetime(value):
        date_from_value = get_date_from_string(value)
        if not date_from_value:
            return None
        if date_from_value.tzinfo is None:
            date_from_value = date_from_value.replace(tzinfo=UTC)
        return date_from_value.isoformat()

    app.add_template_filter(average_incident_time)
    app.add_template_filter(any_datetime_string_to_iso_8601_datetime)
    app.add_template_filter(date_from_datetime_string)
    app.add_template_filter(incident_count)
    app.add_template_filter(longest_incident_time)
    app.add_template_filter(markdown)
    app.add_template_filter(pretty_date)
    app.add_template_filter(pretty_datetime)
    app.add_template_filter(pretty_percentage)
    app.add_template_filter(pretty_uptime_kuma_status)
    app.add_template_filter(previous_incidents)
    app.add_template_filter(seconds_to_time)
    app.add_template_filter(seconds_to_duration)
    app.add_template_filter(slugify)
    app.add_template_filter(time_ago)
    app.add_template_filter(total_incident_time)
    app.add_template_filter(total_maintenance_time)

    @app.context_processor
    def context_processor():
        return {
            "cookie_preference": cookie_preference,
            "now_iso_8601": now_iso_8601,
            "now_iso_8601_date": now_iso_8601_date,
            "now_pretty": now_pretty,
            "incident_calendar_heartbeats": incident_calendar_heartbeats,
            "incident_calendar_count": incident_calendar_count,
            "incident_calendar_duration": incident_calendar_duration,
            "app_config": {
                "ENVIRONMENT_NAME": app.config.get("ENVIRONMENT_NAME"),
                "CONTAINER_IMAGE": app.config.get("CONTAINER_IMAGE"),
                "BUILD_VERSION": app.config.get("BUILD_VERSION"),
                "TNA_FRONTEND_VERSION": app.config.get("TNA_FRONTEND_VERSION"),
                "COOKIE_DOMAIN": app.config.get("COOKIE_DOMAIN"),
                "STATUS_PAGE_REFRESH_SECONDS": app.config.get(
                    "STATUS_PAGE_REFRESH_SECONDS"
                ),
            },
            "feature": {},
        }

    from .healthcheck import bp as healthcheck_bp
    from .main import bp as site_bp
    from .status import bp as status_bp

    app.register_blueprint(healthcheck_bp, url_prefix="/healthcheck")
    app.register_blueprint(site_bp)
    app.register_blueprint(status_bp, url_prefix="/status")

    return app
