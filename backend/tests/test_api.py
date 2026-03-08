import pytest


@pytest.mark.anyio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_stats_initially_zero(client):
    response = await client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["people_inside"] == 0
    assert data["entries_today"] == 0
    assert data["exits_today"] == 0


@pytest.mark.anyio
async def test_alert_in(client):
    response = await client.post(
        "/api/alert",
        json={"device_id": "gate_1", "direction": "in", "timestamp": 1710000000},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["people_inside"] == 1
    assert data["entries_today"] == 1
    assert data["exits_today"] == 0


@pytest.mark.anyio
async def test_alert_out(client):
    # First put someone in
    await client.post(
        "/api/alert",
        json={"device_id": "gate_1", "direction": "in", "timestamp": 1710000001},
    )
    response = await client.post(
        "/api/alert",
        json={"device_id": "gate_1", "direction": "out", "timestamp": 1710000002},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exits_today"] >= 1


@pytest.mark.anyio
async def test_alert_out_never_negative(client):
    """people_inside should never go below 0."""
    # Force a fresh state by using new session (handled by fixture)
    # Just send lots of out events
    for i in range(5):
        resp = await client.post(
            "/api/alert",
            json={"device_id": "gate_x", "direction": "out", "timestamp": 1710000100 + i},
        )
        assert resp.status_code == 200
        assert resp.json()["people_inside"] >= 0


@pytest.mark.anyio
async def test_alert_invalid_direction(client):
    response = await client.post(
        "/api/alert",
        json={"device_id": "gate_1", "direction": "sideways", "timestamp": 1710000000},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_alert_missing_field(client):
    response = await client.post(
        "/api/alert",
        json={"device_id": "gate_1", "direction": "in"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_history(client):
    response = await client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
