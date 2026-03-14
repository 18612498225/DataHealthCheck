"""API integration tests."""
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

# Use in-memory SQLite for tests (must set before app import)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_db
from seed_data import seed

client = TestClient(app)


def setup_module():
    init_db()
    seed()


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_list_datasources():
    r = client.get("/api/v1/datasources")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert "config" in data[0]


def test_list_rule_sets():
    r = client.get("/api/v1/rule-sets")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_run_task():
    ds = client.get("/api/v1/datasources").json()
    rs = client.get("/api/v1/rule-sets").json()
    assert len(ds) and len(rs)

    r = client.post(
        "/api/v1/tasks/run",
        json={
            "name": "测试任务",
            "datasource_ids": [ds[0]["id"]],
            "rule_set_id": rs[0]["id"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "task_id" in data
    assert data["status"] == "completed"
    assert "result" in data
    assert "summary" in data["result"]
    assert "details" in data["result"]


def test_get_report():
    ds = client.get("/api/v1/datasources").json()
    rs = client.get("/api/v1/rule-sets").json()
    run_r = client.post(
        "/api/v1/tasks/run",
        json={
            "name": "报告测试",
            "datasource_ids": [ds[0]["id"]],
            "rule_set_id": rs[0]["id"],
        },
    )
    task_id = run_r.json()["task_id"]

    r = client.get(f"/api/v1/reports/{task_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["task_id"] == task_id
    assert "summary" in data
    assert "details" in data


def test_report_download():
    ds = client.get("/api/v1/datasources").json()
    rs = client.get("/api/v1/rule-sets").json()
    run_r = client.post(
        "/api/v1/tasks/run",
        json={
            "name": "下载测试",
            "datasource_ids": [ds[0]["id"]],
            "rule_set_id": rs[0]["id"],
        },
    )
    task_id = run_r.json()["task_id"]

    r = client.get(f"/api/v1/reports/{task_id}/download?format=json")
    assert r.status_code == 200
    assert "application/json" in r.headers.get("content-type", "")

    r2 = client.get(f"/api/v1/reports/{task_id}/download?format=html")
    assert r2.status_code == 200


def test_profiling():
    ds = client.get("/api/v1/datasources").json()
    assert len(ds) >= 1

    r = client.post(
        "/api/v1/profiling",
        json={"datasource_id": ds[0]["id"], "sample_size": 1000},
    )
    assert r.status_code == 200
    data = r.json()
    assert "columns" in data
    assert "row_count" in data
    assert isinstance(data["columns"], list)


def test_auth_login():
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
