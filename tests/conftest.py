import pytest

from notes_service.app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def alice():
    return {"X-User": "alice", "X-Role": "editor"}
