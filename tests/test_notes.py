import pytest


def create(client, title="Hello", content="World", headers=None):
    return client.post("/notes", json={"title": title, "content": content}, headers=headers or {})


def test_list_empty(client):
    r = client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []


def test_create_and_get(client):
    r = create(client)
    assert r.status_code == 201
    note = r.json()
    assert note["title"] == "Hello"
    assert note["id"] > 0

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["content"] == "World"


def test_get_missing_returns_404(client):
    assert client.get("/notes/9999").status_code == 404


@pytest.mark.parametrize("payload", [{"title": ""}, {"content": "no title"}, {"title": "x" * 201}])
def test_create_validation(client, payload):
    assert client.post("/notes", json=payload).status_code == 422


def test_put_replaces_whole_note(client):
    note_id = create(client).json()["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "New", "content": ""})
    assert r.status_code == 200
    assert r.json()["title"] == "New"
    assert r.json()["content"] == ""  # перезаписано, а не збережено старе


def test_put_requires_all_fields(client):
    note_id = create(client).json()["id"]
    assert client.put(f"/notes/{note_id}", json={"title": "Only title"}).status_code == 422


def test_patch_updates_only_given_fields(client):
    note_id = create(client).json()["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    assert r.json()["title"] == "Updated"
    assert r.json()["content"] == "World"  # не змінилось


def test_update_missing_returns_404(client):
    assert client.put("/notes/9999", json={"title": "x", "content": "y"}).status_code == 404
    assert client.patch("/notes/9999", json={"title": "x"}).status_code == 404


def test_delete(client):
    note_id = create(client).json()["id"]
    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404
    assert client.delete(f"/notes/{note_id}").status_code == 404


def test_search_and_pagination(client):
    create(client, title="Buy milk")
    create(client, title="Learn Docker", content="images and containers")
    create(client, title="Learn GitHub Actions")

    r = client.get("/notes", params={"search": "Learn"})
    assert len(r.json()) == 2

    r = client.get("/notes", params={"search": "containers"})
    assert [n["title"] for n in r.json()] == ["Learn Docker"]

    r = client.get("/notes", params={"limit": 1})
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Learn GitHub Actions"  # найновіша першою


def test_api_key_required_for_writes(secured_client):
    assert create(secured_client).status_code == 401
    assert create(secured_client, headers={"X-API-Key": "wrong"}).status_code == 401
    assert create(secured_client, headers={"X-API-Key": "secret"}).status_code == 201
    # читання відкрите
    assert secured_client.get("/notes").status_code == 200
