def test_create_and_list(client, alice):
    r = client.post("/notes", json={"title": "hello", "body": "world"}, headers=alice)
    assert r.status_code == 201
    notes = client.get("/notes", headers=alice).get_json()
    assert [n["title"] for n in notes] == ["hello"]


def test_title_required(client, alice):
    assert client.post("/notes", json={}, headers=alice).status_code == 400


def test_only_owner_or_admin_can_delete(client, alice):
    note_id = client.post("/notes", json={"title": "x"}, headers=alice).get_json()["id"]
    bob = {"X-User": "bob", "X-Role": "editor"}
    assert client.delete(f"/notes/{note_id}", headers=bob).status_code == 403
    admin = {"X-User": "root", "X-Role": "admin"}
    assert client.delete(f"/notes/{note_id}", headers=admin).status_code == 204


def test_missing_user_is_401(client):
    assert client.get("/notes").status_code == 401
