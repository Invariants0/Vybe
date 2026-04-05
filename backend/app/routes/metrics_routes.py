import time
from flask import Blueprint, request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

metrics_bp = Blueprint("metrics", __name__)


# ── Prometheus metrics ────────────────────────────────────────── ///
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total number of HTTP errors (4xx + 5xx)",
    ["method", "endpoint", "status"],
)


def init_metrics(app):
    # Register before/after request hooks to track metrics

    @app.before_request
    def before_request_metrics():
        request._start_time = time.time()
        IN_PROGRESS.inc()

    @app.after_request
    def after_request_metrics(response):
        IN_PROGRESS.dec()
        elapsed = time.time() - getattr(request, "_start_time", time.time())
        endpoint = request.endpoint or request.path
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(elapsed)
        if response.status_code >= 400:
            ERROR_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code,
            ).inc()
        return response


@metrics_bp.route("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)
