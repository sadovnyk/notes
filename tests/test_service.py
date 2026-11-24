def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["version"] == "1.2.3"


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["environment"] == "test"
    assert body["version"] == "1.2.3"


def test_health_degraded_when_db_unavailable(client, monkeypatch):
    monkeypatch.setattr(client.app.state.storage, "ping", lambda: False)
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["status"] == "degraded"


def test_metrics_counts_requests(client):
    client.get("/health")
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.json()["requests_total"] >= 2
    assert r.json()["uptime_seconds"] >= 0
