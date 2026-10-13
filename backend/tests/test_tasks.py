from fastapi.testclient import TestClient
import pytest
from app import create_app


@pytest.fixture
def database(tmp_path):
    return tmp_path / "tasks.sqlite3"


def test_seed_and_list(database):
    with TestClient(create_app(database)) as client:
        response = client.get("/api/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert set(tasks[0]) == {"id", "title", "description", "completed"}
        assert tasks[0]["completed"] is False


def test_toggle_and_persistence(database):
    with TestClient(create_app(database)) as client:
        assert client.patch("/api/tasks/1", json={"completed": True}).json()["completed"] is True
    with TestClient(create_app(database)) as client:
        assert client.get("/api/tasks").json()[0]["completed"] is True
        assert client.patch("/api/tasks/1", json={"completed": False}).json()["completed"] is False


def test_delete_and_no_reseed(database):
    with TestClient(create_app(database)) as client:
        for task in client.get("/api/tasks").json():
            assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
        assert client.get("/api/tasks").json() == []
    with TestClient(create_app(database)) as client:
        assert client.get("/api/tasks").json() == []


def test_missing_task(database):
    with TestClient(create_app(database)) as client:
        assert client.patch("/api/tasks/999", json={"completed": True}).status_code == 404
        assert client.delete("/api/tasks/999").status_code == 404


@pytest.mark.parametrize("body", [{}, {"completed": "yes"}, {"completed": None}])
def test_invalid_update(database, body):
    with TestClient(create_app(database)) as client:
        assert client.patch("/api/tasks/1", json=body).status_code == 422
