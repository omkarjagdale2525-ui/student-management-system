import pytest

import app as app_module
import database as db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


VALID = {
    "roll_no": "IT001", "name": "Asha Patil", "email": "asha@example.com",
    "phone": "9876543210", "course": "B.Sc. IT", "year": "3",
}


def test_add_and_view(client):
    r = client.post("/add", data=VALID, follow_redirects=True)
    assert b"Student added successfully" in r.data
    assert b"Asha Patil" in r.data


def test_validation_rejects_bad_email(client):
    r = client.post("/add", data={**VALID, "email": "nope"}, follow_redirects=True)
    assert b"valid email" in r.data
    assert db.list_students() == []


def test_duplicate_roll_no(client):
    client.post("/add", data=VALID)
    r = client.post("/add", data={**VALID, "email": "other@example.com"}, follow_redirects=True)
    assert b"already exists" in r.data
    assert len(db.list_students()) == 1


def test_update(client):
    client.post("/add", data=VALID)
    sid = db.list_students()[0]["id"]
    client.post(f"/edit/{sid}", data={**VALID, "name": "Asha P."})
    assert db.get_student(sid)["name"] == "Asha P."


def test_delete(client):
    client.post("/add", data=VALID)
    sid = db.list_students()[0]["id"]
    client.post(f"/delete/{sid}")
    assert db.get_student(sid) is None


def test_search(client):
    client.post("/add", data=VALID)
    client.post("/add", data={**VALID, "roll_no": "CS002", "name": "Ravi Shah",
                              "email": "ravi@example.com", "course": "B.Sc. CS"})
    r = client.get("/?q=Ravi")
    assert b"Ravi Shah" in r.data and b"Asha Patil" not in r.data


def test_view_detail_page(client):
    client.post("/add", data=VALID)
    sid = db.list_students()[0]["id"]
    r = client.get(f"/student/{sid}")
    assert r.status_code == 200
    assert b"Asha Patil" in r.data


def test_stats_on_home(client):
    client.post("/add", data=VALID)
    r = client.get("/")
    assert b"Total Students" in r.data