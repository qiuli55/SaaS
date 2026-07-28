"""核心 API 测试：认证 / 案件 / 日程 / 客户"""
import pytest


class TestHealth:
    def test_health(self, api):
        r = api.get("/api/health")
        assert r.status_code == 200


class TestAuth:
    def test_register_login(self, api):
        phone = "13800000001"
        r = api.post("/api/user/register", json={"phone": phone, "password": "Test1234", "name": "TestLawyer"})
        assert r.status_code == 200
        assert "access_token" in r.json()

        r2 = api.post("/api/user/login", json={"phone": phone, "password": "Test1234"})
        assert r2.status_code == 200
        assert "access_token" in r2.json()

    def test_duplicate_phone(self, api):
        api.post("/api/user/register", json={"phone": "13900000001", "password": "Test1234"})
        r = api.post("/api/user/register", json={"phone": "13900000001", "password": "OtherPass1"})
        assert r.status_code == 400

    def test_wrong_password(self, api):
        api.post("/api/user/register", json={"phone": "13900000002", "password": "RightPass1"})
        r = api.post("/api/user/login", json={"phone": "13900000002", "password": "WrongPass1"})
        assert r.status_code == 401

    def test_invalid_token(self, api):
        r = api.get("/api/user/info", headers={"Authorization": "Bearer bad.token.here"})
        assert r.status_code == 401

    def test_no_token(self, api):
        r = api.get("/api/user/info")
        assert r.status_code == 401


class TestCases:
    def test_create(self, api):
        from conftest import fresh_auth
        auth = fresh_auth(api)
        r = api.post("/api/cases", json={"case_type": "Contract", "plaintiff": "Zhang", "defendant": "Li Co"}, headers=auth)
        assert r.status_code == 200, f"create failed: {r.json()}"
        assert r.json()["case_no"].startswith("LA-")

    def test_list(self, api, auth):
        api.post("/api/cases", json={"case_type": "Test", "plaintiff": "A"}, headers=auth)
        r = api.get("/api/cases", headers=auth)
        assert r.json()["total"] == 1

    def test_pagination(self, api, auth):
        for i in range(5):
            api.post("/api/cases", json={"case_type": f"C{i}", "plaintiff": f"P{i}", "defendant": f"D{i}"}, headers=auth)
        r = api.get("/api/cases?page=1&page_size=2", headers=auth)
        assert r.json()["total"] == 5
        assert len(r.json()["items"]) == 2

    def test_update(self, api, auth):
        created = api.post("/api/cases", json={"case_type": "Old"}, headers=auth)
        cid = created.json()["id"]
        r = api.put(f"/api/cases/{cid}", json={"case_type": "New", "status": "done"}, headers=auth)
        assert r.status_code == 200
        assert r.json()["case_type"] == "New"

    def test_delete(self, api, auth):
        created = api.post("/api/cases", json={"case_type": "ToDelete"}, headers=auth)
        cid = created.json()["id"]
        r = api.delete(f"/api/cases/{cid}", headers=auth)
        assert r.json()["code"] == 0
        assert api.get(f"/api/cases/{cid}", headers=auth).status_code == 404

    def test_search(self, api, auth):
        api.post("/api/cases", json={"case_type": "Divorce", "plaintiff": "A", "defendant": "B"}, headers=auth)
        api.post("/api/cases", json={"case_type": "Contract", "plaintiff": "C", "defendant": "D"}, headers=auth)
        r = api.get("/api/cases", params={"keyword": "Contract"}, headers=auth)
        assert r.json()["total"] == 1

    def test_isolation(self, api, auth):
        api.post("/api/cases", json={"case_type": "User1Case"}, headers=auth)
        from conftest import fresh_auth
        auth2 = fresh_auth(api)
        r = api.get("/api/cases", headers=auth2)
        assert r.json()["total"] == 0


class TestSchedules:
    def test_create_and_list(self, api, auth):
        r = api.post("/api/schedules", json={"event_type": "\u5f00\u5ead", "event_date": "2026-08-15T09:00:00"}, headers=auth)
        assert r.status_code == 200
        r2 = api.get("/api/schedules?month=2026-08", headers=auth)
        assert len(r2.json()["data"]) == 1

    def test_invalid_type(self, api, auth):
        r = api.post("/api/schedules", json={"event_type": "InvalidType", "event_date": "2026-08-15T09:00:00"}, headers=auth)
        assert r.status_code == 400

    def test_update_delete(self, api, auth):
        created = api.post("/api/schedules", json={"event_type": "\u5f85\u529e", "event_date": "2026-09-01T10:00:00"}, headers=auth)
        sid = created.json()["data"]["id"]
        r = api.put(f"/api/schedules/{sid}", json={"event_type": "\u5f00\u5ead", "is_done": True}, headers=auth)
        assert r.json()["data"]["event_type"] == "\u5f00\u5ead"
        assert api.delete(f"/api/schedules/{sid}", headers=auth).status_code == 200


class TestClients:
    def test_create_and_list(self, api, auth):
        r = api.post("/api/clients", json={"name": "ClientA", "phone": "13911110001"}, headers=auth)
        assert r.json()["data"]["name"] == "ClientA"
        r2 = api.get("/api/clients", headers=auth)
        assert r2.json()["data"]["total"] == 1

    def test_update_delete(self, api, auth):
        created = api.post("/api/clients", json={"name": "OldName", "phone": "13911110002"}, headers=auth)
        cid = created.json()["data"]["id"]
        r = api.put(f"/api/clients/{cid}", json={"name": "NewName"}, headers=auth)
        assert r.json()["data"]["name"] == "NewName"
        api.delete(f"/api/clients/{cid}", headers=auth)
        assert api.get(f"/api/clients/{cid}", headers=auth).status_code == 404

    def test_export(self, api, auth):
        api.post("/api/clients", json={"name": "ExpClient", "phone": "13911110003"}, headers=auth)
        r = api.get("/api/clients/export", headers=auth)
        assert "spreadsheet" in r.headers.get("content-type", "")
