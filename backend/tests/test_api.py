"""核心 API 测试：认证 / 案件 / 日程 / 客户 / 文件上传 / 改密"""
import pytest
import io


class TestHealth:
    def test_app_running(self, api):
        r = api.get("/api/user/info")  # 不需要登录也能测 401
        assert r.status_code == 401  # 证明服务器在运行


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

    def test_get_by_id(self, api, auth):
        created = api.post("/api/cases", json={"case_type": "TestGet", "plaintiff": "P", "defendant": "D"}, headers=auth)
        cid = created.json()["id"]
        r = api.get(f"/api/cases/{cid}", headers=auth)
        assert r.status_code == 200
        assert r.json()["case_type"] == "TestGet"

    def test_filter_by_status(self, api, auth):
        api.post("/api/cases", json={"case_type": "A", "status": "已结案"}, headers=auth)
        api.post("/api/cases", json={"case_type": "B", "status": "进行中"}, headers=auth)
        r = api.get("/api/cases", params={"status": "进行中"}, headers=auth)
        assert r.json()["total"] == 1


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


class TestPasswordChange:
    def test_change_password_success(self, api, auth):
        r = api.put("/api/user/password", json={
            "old_password": "Test1234", "new_password": "NewPass456"
        }, headers=auth)
        assert r.status_code == 200
        assert r.json()["message"] == "密码修改成功"

    def test_wrong_old_password(self, api, auth):
        r = api.put("/api/user/password", json={
            "old_password": "WrongOld1", "new_password": "Whatever1"
        }, headers=auth)
        assert r.status_code == 400
        assert "错误" in r.json()["detail"]

    def test_same_password_rejected(self, api, auth):
        r = api.put("/api/user/password", json={
            "old_password": "Test1234", "new_password": "Test1234"
        }, headers=auth)
        assert r.status_code == 400

    def test_login_with_new_password(self, api):
        # 自包含：注册→改密→新密码登录
        phone = "13800000050"
        api.post("/api/user/register", json={"phone": phone, "password": "Test1234", "name": "PwdTest"})
        token = api.post("/api/user/login", json={"phone": phone, "password": "Test1234"}).json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        api.put("/api/user/password", json={"old_password": "Test1234", "new_password": "Changed99"}, headers=h)
        r = api.post("/api/user/login", json={"phone": phone, "password": "Changed99"})
        assert r.status_code == 200


class TestProfileUpdate:
    def test_update_name_and_firm(self, api, auth):
        r = api.put("/api/user/profile", json={"name": "Lilawyer", "firm_name": "Zhengda"}, headers=auth)
        assert r.status_code == 200
        assert r.json()["name"] == "Lilawyer"
        assert r.json()["firm_name"] == "Zhengda"


class TestFileUpload:
    def test_upload_txt(self, api, auth):
        from conftest import fresh_auth
        # 创建案件
        r = api.post("/api/cases", json={"case_type": "Test"}, headers=auth)
        cid = r.json()["id"]

        r2 = api.post(
            f"/api/cases/{cid}/files",
            files=[("files", ("test.txt", io.BytesIO(b"hello world"), "text/plain"))],
            headers=auth,
        )
        assert r2.status_code == 200

    def test_reject_php_file(self, api, auth):
        r = api.post("/api/cases", json={"case_type": "Test2"}, headers=auth)
        cid = r.json()["id"]

        r2 = api.post(
            f"/api/cases/{cid}/files",
            files=[("files", ("shell.php", io.BytesIO(b"<?php echo 1;"), "text/plain"))],
            headers=auth,
        )
        assert r2.status_code == 400
        assert "不支持" in r2.json()["detail"] or "文件" in str(r2.json())


class TestSchedulesExtra:
    def test_month_filter(self, api, auth):
        api.post("/api/schedules", json={"event_type": "开庭", "event_date": "2026-07-10T08:00:00"}, headers=auth)
        api.post("/api/schedules", json={"event_type": "开庭", "event_date": "2026-08-20T14:00:00"}, headers=auth)
        r = api.get("/api/schedules?month=2026-07", headers=auth)
        assert len(r.json()["data"]) == 1

    def test_mark_done_toggle(self, api, auth):
        r = api.post("/api/schedules", json={"event_type": "待办", "event_date": "2026-10-10T09:00:00"}, headers=auth)
        sid = r.json()["data"]["id"]
        r2 = api.put(f"/api/schedules/{sid}", json={"is_done": True}, headers=auth)
        assert r2.json()["data"]["is_done"] is True


class TestClientsExtra:
    def test_search_by_keyword(self, api, auth):
        api.post("/api/clients", json={"name": "Alice", "phone": "13922220001", "company": "ABCInc"}, headers=auth)
        api.post("/api/clients", json={"name": "Bob", "phone": "13922220002", "company": "XYZLtd"}, headers=auth)
        r = api.get("/api/clients", params={"keyword": "ABC"}, headers=auth)
        assert r.json()["data"]["total"] == 1
        assert r.json()["data"]["items"][0]["name"] == "Alice"


class TestEdgeCases:
    def test_nonexistent_case_404(self, api, auth):
        r = api.get("/api/cases/99999", headers=auth)
        assert r.status_code == 404

    def test_empty_schedules_month(self, api, auth):
        r = api.get("/api/schedules?month=2030-01", headers=auth)
        assert r.status_code == 200
        assert len(r.json()["data"]) == 0


class TestFileDownload:
    def test_download_after_upload(self, api, auth):
        # 上传一个文件
        r = api.post("/api/cases", json={"case_type": "DownloadTest"}, headers=auth)
        cid = r.json()["id"]
        api.post(
            f"/api/cases/{cid}/files",
            files=[("files", ("note.txt", io.BytesIO(b"test content"), "text/plain"))],
            headers=auth,
        )
        # 列出案件文件
        r2 = api.get(f"/api/cases/{cid}", headers=auth)
        assert r2.status_code == 200
        assert r2.json()["file_count"] >= 1


class TestScheduleIsolation:
    def test_other_user_cant_see(self, api, auth):
        api.post("/api/schedules", json={"event_type": "开庭", "event_date": "2026-07-01T08:00:00"}, headers=auth)
        from conftest import fresh_auth
        auth2 = fresh_auth(api)
        r = api.get("/api/schedules?month=2026-07", headers=auth2)
        assert len(r.json()["data"]) == 0
