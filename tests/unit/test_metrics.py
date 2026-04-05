from __future__ import annotations


def test_metrics_endpoint_exposes_prometheus_format(client):
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "http_requests_total" in body
    assert "http_request_duration_seconds_bucket" in body
    assert 'endpoint="health"' in body


def test_request_counter_and_error_counter_increment(client):
    client.get("/health")
    client.get("/boom")
    response = client.get("/metrics")
    body = response.get_data(as_text=True)

    assert 'http_requests_total{endpoint="health",method="GET",status="200"}' in body
    assert 'http_errors_total{endpoint="boom",method="GET",status="500"}' in body
