from __future__ import annotations

import json
import re
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / "logs" / "chaos"
NETWORK = "vybe-chaos-net"
APP_IMAGE = "vybe-chaos-app"
CONTAINERS = {
    "db": "vybe-chaos-db",
    "redis": "vybe-chaos-redis",
    "app1": "vybe-chaos-app1",
    "app2": "vybe-chaos-app2",
    "nginx": "vybe-chaos-nginx",
}


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=check)


def cleanup() -> None:
    run(["docker", "rm", "-f", *CONTAINERS.values()], check=False)
    run(["docker", "network", "rm", NETWORK], check=False)


def http_request(
    method: str,
    url: str,
    *,
    json_body: dict[str, Any] | None = None,
    follow_redirects: bool = True,
    timeout: float = 5.0,
) -> tuple[int, str, dict[str, str]]:
    data = None
    headers = {}
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    opener = build_opener(*( [] if follow_redirects else [NoRedirectHandler()] ))
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", "replace"), dict(response.headers.items())
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace"), dict(exc.headers.items())
    except URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc}") from exc


def wait_http(url: str, expected: int = 200, timeout_seconds: float = 120.0) -> float:
    start = time.perf_counter()
    while time.perf_counter() - start < timeout_seconds:
        try:
            status, _, _ = http_request("GET", url)
            if status == expected:
                return time.perf_counter() - start
        except Exception:
            pass
        time.sleep(1.0)
    raise TimeoutError(f"Timed out waiting for {url} -> {expected}")


def wait_db_ready(timeout_seconds: float = 120.0) -> None:
    start = time.perf_counter()
    while time.perf_counter() - start < timeout_seconds:
        result = run(
            [
                "docker",
                "exec",
                CONTAINERS["db"],
                "pg_isready",
                "-U",
                "postgres",
                "-d",
                "hackathon_db",
            ],
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(1.0)
    raise TimeoutError("PostgreSQL did not become ready in time")


def write_nginx_config(tmpdir: Path) -> Path:
    config = f"""
events {{}}
http {{
  upstream vybe_backend {{
    least_conn;
    server {CONTAINERS["app1"]}:5000 max_fails=3 fail_timeout=5s;
    server {CONTAINERS["app2"]}:5000 max_fails=3 fail_timeout=5s;
  }}

  server {{
    listen 80;

    location /health {{
      proxy_pass http://vybe_backend;
    }}

    location /ready {{
      proxy_pass http://vybe_backend;
    }}

    location /metrics {{
      proxy_pass http://vybe_backend;
    }}

    location ~ ^/(users|urls|events) {{
      proxy_pass http://vybe_backend;
    }}

    location ~ ^/[A-Za-z0-9_-]+$ {{
      proxy_pass http://vybe_backend;
    }}

    location / {{
      return 404;
    }}
  }}
}}
""".strip()
    path = tmpdir / "nginx.conf"
    path.write_text(config, encoding="utf-8")
    return path


def docker_logs(name: str, tail: int = 80) -> str:
    result = run(["docker", "logs", "--tail", str(tail), name], check=False)
    return (result.stdout + result.stderr).strip()


def extract_metric(body: str, metric_name: str) -> float:
    matches = re.findall(rf"^{re.escape(metric_name)}(?:\{{.*\}})?\s+([0-9.]+)$", body, flags=re.MULTILINE)
    return sum(float(value) for value in matches)


def start_stack(tmpdir: Path) -> None:
    cleanup()
    run(["docker", "network", "create", NETWORK])
    run(["docker", "build", "-f", "infra/docker/backend.dockerfile", "-t", APP_IMAGE, "."])
    run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINERS["db"],
            "--network",
            NETWORK,
            "-e",
            "POSTGRES_DB=hackathon_db",
            "-e",
            "POSTGRES_USER=postgres",
            "-e",
            "POSTGRES_PASSWORD=postgres",
            "postgres:16-alpine",
        ]
    )
    wait_db_ready()
    run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINERS["redis"],
            "--network",
            NETWORK,
            "redis:7-alpine",
            "redis-server",
            "--save",
            "",
            "--appendonly",
            "no",
        ]
    )
    app_env = [
        "-e",
        "DATABASE_HOST=vybe-chaos-db",
        "-e",
        "DATABASE_PORT=5432",
        "-e",
        "DATABASE_NAME=hackathon_db",
        "-e",
        "DATABASE_USER=postgres",
        "-e",
        "DATABASE_PASSWORD=postgres",
        "-e",
        "AUTO_CREATE_TABLES=true",
        "-e",
        "REDIS_ENABLED=true",
        "-e",
        "REDIS_URL=redis://vybe-chaos-redis:6379/0",
        "-e",
        "SENTRY_DSN=",
        "-e",
        "DISCORD_WEBHOOK_URL=",
        "-e",
        "AUTH_ENABLED=false",
    ]
    app_args = [
        "--bind",
        "0.0.0.0:5000",
        "--workers",
        "2",
        "--threads",
        "4",
        "--timeout",
        "120",
        "--keep-alive",
        "5",
        "run:app",
    ]
    run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINERS["app1"],
            "--network",
            NETWORK,
            "-p",
            "5001:5000",
            "--entrypoint",
            "gunicorn",
            *app_env,
            APP_IMAGE,
            *app_args,
        ]
    )
    run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINERS["app2"],
            "--network",
            NETWORK,
            "-p",
            "5002:5000",
            "--entrypoint",
            "gunicorn",
            *app_env,
            APP_IMAGE,
            *app_args,
        ]
    )
    wait_http("http://localhost:5001/ready")
    wait_http("http://localhost:5002/ready")
    nginx_path = write_nginx_config(tmpdir)
    run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINERS["nginx"],
            "--network",
            NETWORK,
            "-p",
            "8080:80",
            "-v",
            f"{nginx_path}:/etc/nginx/nginx.conf:ro",
            "nginx:1.27-alpine",
        ]
    )
    wait_http("http://localhost:8080/health")


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    results: dict[str, Any] = {"generated_at": generated_at, "scenarios": []}

    with tempfile.TemporaryDirectory() as temp_dir:
        tmpdir = Path(temp_dir)
        try:
            start_stack(tmpdir)

            # Scenario 1
            scenario_start = time.perf_counter()
            run(["docker", "kill", CONTAINERS["app1"]])
            health_statuses: list[Any] = []
            recovery = None
            for _ in range(20):
                try:
                    status, _, _ = http_request("GET", "http://localhost:8080/health")
                    health_statuses.append(status)
                    if status == 200:
                        recovery = time.perf_counter() - scenario_start
                        break
                except Exception as exc:
                    health_statuses.append(str(exc))
                time.sleep(0.5)
            wait_http("http://localhost:8080/health")
            results["scenarios"].append(
                {
                    "name": "Kill one app container",
                    "outcome": "pass" if recovery is not None else "fail",
                    "recovery_time_seconds": round(recovery or 0.0, 2),
                    "summary": f"Health via nginx stayed available with samples {health_statuses}",
                    "evidence": "\n".join(
                        [
                            run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"], check=False).stdout,
                            docker_logs(CONTAINERS["app1"]),
                            docker_logs(CONTAINERS["app2"]),
                            docker_logs(CONTAINERS["nginx"]),
                        ]
                    ),
                }
            )

            # Scenario 2
            run(["docker", "restart", CONTAINERS["db"]])
            scenario_start = time.perf_counter()
            readiness_statuses: list[str] = []
            saw_503 = False
            recovery = None
            for _ in range(60):
                result = run(
                    [
                        "docker",
                        "exec",
                        CONTAINERS["app2"],
                        "curl",
                        "-s",
                        "-o",
                        "/dev/null",
                        "-w",
                        "%{http_code}",
                        "http://localhost:5000/ready",
                    ],
                    check=False,
                )
                status = result.stdout.strip() or "exec-error"
                readiness_statuses.append(status)
                if status == "503":
                    saw_503 = True
                if saw_503 and status == "200":
                    recovery = time.perf_counter() - scenario_start
                    break
                time.sleep(0.5)
            results["scenarios"].append(
                {
                    "name": "Restart database",
                    "outcome": "pass" if recovery is not None else "fail",
                    "recovery_time_seconds": round(recovery or 0.0, 2),
                    "summary": f"Readiness moved through {readiness_statuses[:20]}",
                    "evidence": "\n".join(
                        [
                            docker_logs(CONTAINERS["db"]),
                            docker_logs(CONTAINERS["app2"]),
                        ]
                    ),
                }
            )
            wait_http("http://localhost:5002/ready")
            wait_http("http://localhost:8080/health")

            # Scenario 3
            status, body, _ = http_request("POST", "http://localhost:5002/users", json_body={"username": "chaos-user", "email": "chaos@example.com"})
            user_id = json.loads(body)["id"]
            status, body, _ = http_request(
                "POST",
                "http://localhost:5002/urls",
                json_body={"user_id": user_id, "original_url": "https://example.com/chaos", "title": "Chaos"},
            )
            short_code = json.loads(body)["short_code"]
            run(["docker", "stop", CONTAINERS["redis"]])
            time.sleep(1.0)
            scenario_start = time.perf_counter()
            redirect_status, _, redirect_headers = http_request(
                "GET",
                f"http://localhost:5002/{short_code}",
                follow_redirects=False,
                timeout=30.0,
            )
            recovery = time.perf_counter() - scenario_start
            run(["docker", "start", CONTAINERS["redis"]])
            wait_http("http://localhost:5002/ready")
            results["scenarios"].append(
                {
                    "name": "Simulate cache failure",
                    "outcome": "pass" if redirect_status == 302 else "fail",
                    "recovery_time_seconds": round(recovery, 2),
                    "summary": f"Redirect returned {redirect_status} with location {redirect_headers.get('Location')}",
                    "evidence": "\n".join(
                        [
                            f"redirect_status={redirect_status}",
                            f"location={redirect_headers.get('Location', '')}",
                            docker_logs(CONTAINERS["app1"]),
                            docker_logs(CONTAINERS["app2"]),
                        ]
                    ),
                }
            )

            # Scenario 4
            def hit_bad_route(index: int) -> int:
                status, _, _ = http_request("GET", f"http://localhost:5002/chaos-invalid-{index}")
                return status

            scenario_start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=16) as pool:
                statuses = list(pool.map(hit_bad_route, range(60)))
            health_status, _, _ = http_request("GET", "http://localhost:5002/health")
            _, metrics_body, _ = http_request("GET", "http://localhost:5002/metrics")
            error_metric_total = extract_metric(metrics_body, "http_errors_total")
            recovery = time.perf_counter() - scenario_start
            results["scenarios"].append(
                {
                    "name": "High error rate simulation",
                    "outcome": "pass" if health_status == 200 and error_metric_total >= 60 else "fail",
                    "recovery_time_seconds": round(recovery, 2),
                    "summary": f"60 invalid requests completed; health={health_status}; http_errors_total={error_metric_total}",
                    "evidence": "\n".join(
                        [
                            f"statuses={statuses}",
                            "\n".join(line for line in metrics_body.splitlines() if "http_errors_total" in line),
                            docker_logs(CONTAINERS["app1"]),
                            docker_logs(CONTAINERS["app2"]),
                        ]
                    ),
                }
            )

        finally:
            cleanup()

    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = LOG_ROOT / f"chaos-results-{stamp}.json"
    md_path = LOG_ROOT / f"chaos-results-{stamp}.md"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    lines = [f"# Chaos Results ({stamp})", "", f"- Generated: {generated_at}", ""]
    for scenario in results["scenarios"]:
        lines.extend(
            [
                f"## {scenario['name']}",
                f"- Outcome: {scenario['outcome']}",
                f"- Recovery time seconds: {scenario['recovery_time_seconds']}",
                f"- Summary: {scenario['summary']}",
                "",
                "```text",
                scenario["evidence"].strip(),
                "```",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"artifact": str(md_path), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
