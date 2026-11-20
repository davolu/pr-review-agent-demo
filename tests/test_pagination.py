def _make_notes(client, headers, count):
    for i in range(count):
        client.post("/notes", json={"title": f"note {i}"}, headers=headers)


def test_per_page_limits_results(client, alice):
    _make_notes(client, alice, 5)
    body = client.get("/notes?per_page=2", headers=alice).get_json()
    assert body["per_page"] == 2
    assert len(body["items"]) == 2


def test_rejects_bad_page_args(client, alice):
    assert client.get("/notes?page=0", headers=alice).status_code == 400
    assert client.get("/notes?per_page=500", headers=alice).status_code == 400
    assert client.get("/notes?page=abc", headers=alice).status_code == 400
