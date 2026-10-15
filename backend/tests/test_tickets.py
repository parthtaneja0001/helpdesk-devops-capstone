def test_create_ticket_defaults(client, sample):
    r = client.post("/api/tickets", json=sample)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] >= 1
    assert body["status"] == "open"
    assert body["priority"] == "high"


def test_create_ticket_validation_error(client):
    r = client.post("/api/tickets", json={"title": "", "requester": "bob"})
    assert r.status_code == 422


def test_list_and_filter_tickets(client, sample):
    client.post("/api/tickets", json=sample)
    client.post("/api/tickets", json={**sample, "title": "Printer broken", "priority": "low"})
    assert len(client.get("/api/tickets").json()) == 2
    high = client.get("/api/tickets", params={"priority": "high"}).json()
    assert [t["title"] for t in high] == ["Cannot log in"]


def test_get_ticket_and_404(client, sample):
    tid = client.post("/api/tickets", json=sample).json()["id"]
    assert client.get(f"/api/tickets/{tid}").json()["title"] == "Cannot log in"
    assert client.get("/api/tickets/9999").status_code == 404


def test_update_ticket(client, sample):
    tid = client.post("/api/tickets", json=sample).json()["id"]
    r = client.put(f"/api/tickets/{tid}", json={"status": "in_progress", "assignee": "dave"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"
    assert r.json()["assignee"] == "dave"
    assert r.json()["title"] == "Cannot log in"  # untouched fields are preserved


def test_update_missing_ticket_returns_404(client):
    assert client.put("/api/tickets/42", json={"status": "closed"}).status_code == 404


def test_delete_ticket(client, sample):
    tid = client.post("/api/tickets", json=sample).json()["id"]
    assert client.delete(f"/api/tickets/{tid}").status_code == 204
    assert client.get(f"/api/tickets/{tid}").status_code == 404
    assert client.delete(f"/api/tickets/{tid}").status_code == 404


def test_stats(client, sample):
    client.post("/api/tickets", json={**sample, "priority": "urgent"})
    tid = client.post("/api/tickets", json=sample).json()["id"]
    client.put(f"/api/tickets/{tid}", json={"status": "resolved"})
    stats = client.get("/api/tickets/stats").json()
    assert stats == {"total": 2, "open": 1, "in_progress": 0, "resolved": 1, "closed": 0, "urgent": 1}
