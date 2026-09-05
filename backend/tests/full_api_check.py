# -*- coding: utf-8 -*-
"""
Lexi 莱希 后端全链路集成测试（standalone，零依赖，仅用标准库）。
直接对运行中的后端（默认 http://127.0.0.1:8001）发起真实 HTTP 请求，
覆盖：健康检查 / 登录鉴权 / 合同审查（核心） / 案件 / 客户 / 日程 / 文书。
用法：
    cd backend
    python tests/full_api_check.py            # 默认打 127.0.0.1:8001
    python tests/full_api_check.py http://host:port
测试数据会在末尾自动清理（删除创建的 case/client/schedule）。
"""
import sys
import json
import time
import urllib.request
import urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"

# 测试账号（本地环境用 User 模型直插绕过短信网关，见 .workbuddy/memory）
TEST_PHONE = "13800138000"
TEST_PASSWORD = "test123456"

# 一份简短的测试合同（用于验证 /api/contract/review 全链路）
SAMPLE_CONTRACT = """
《软件开发委托合同》
甲方：示例科技有限公司
乙方：示例网络工作室
第一条 甲方委托乙方开发"企业官网"一套，工期 30 天。
第二条 合同总价 5 万元，签约付 30%，上线付 70%。
第三条 乙方交付后，甲方应在 3 日内验收，逾期未提出书面异议视为验收合格。
第四条 任何一方违约，应向对方支付合同总额 20% 的违约金。
第五条 因本合同发生争议，提交甲方所在地法院诉讼解决。
第六条 本合同未尽事宜，双方另行协商。
"""

results = []  # (name, passed, detail)


def _req(method, path, data=None, token=None, timeout=300):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except Exception:
            payload = {"detail": e.reason}
        return e.code, payload
    except Exception as e:  # 连接失败等
        return -1, {"detail": str(e)}


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f"  -> {detail}" if detail else ""))


def main():
    print("=" * 60)
    print("Lexi 莱希 后端全链路测试")
    print("目标服务:", BASE)
    print("=" * 60)

    # ---- T1 健康检查 + 鉴权闸门 ----
    st, _ = _req("GET", "/api/user/info")
    check("T1 未带 token 访问受保护接口应 401", st == 401, f"status={st}")

    # ---- T2 登录 ----
    t0 = time.time()
    st, resp = _req("POST", "/api/user/login",
                    {"phone": TEST_PHONE, "password": TEST_PASSWORD})
    check("T2 测试账号登录成功(200+token)", st == 200 and "access_token" in resp,
          f"status={st}")
    if st != 200 or "access_token" not in resp:
        print("\n登录失败，无法继续依赖鉴权的测试。请确认后端已启动且测试账号已植入。")
        return summarize()
    token = resp["access_token"]
    print(f"      (登录耗时 {time.time()-t0:.2f}s)")

    # ---- T3 非法 token ----
    st, _ = _req("GET", "/api/user/info", token="bad.token.here")
    check("T3 非法 token 应 401", st == 401, f"status={st}")

    # ---- T4 用户信息 ----
    st, resp = _req("GET", "/api/user/info", token=token)
    ok = st == 200 and ("phone" in resp or "user" in resp)
    check("T4 获取用户信息成功", ok, f"status={st} keys={list(resp.keys()) if isinstance(resp,dict) else ''}")

    # ---- T5 密码错误应 401 ----
    st, _ = _req("POST", "/api/user/login",
                 {"phone": TEST_PHONE, "password": "WrongPass!!"})
    check("T5 错误密码登录应 401", st == 401, f"status={st}")

    # ---- T6 合同审查（核心功能）----
    t0 = time.time()
    st, resp = _req("POST", "/api/contract/review",
                    {"content": SAMPLE_CONTRACT, "review_type": "full"}, token=token)
    text = (resp.get("result") or "") if isinstance(resp, dict) else ""
    elapsed = time.time() - t0
    ok = st == 200 and len(text) > 800 and ("风险" in text or "审查" in text or "条款" in text)
    check("T6 合同审查返回完整报告", ok,
          f"status={st} len={len(text)} {elapsed:.1f}s")
    if not ok:
        check("T6-debug 审查响应预览", False, str(resp)[:300])

    # ---- T7 案件创建 ----
    st, resp = _req("POST", "/api/cases",
                    {"case_type": "自动化测试", "plaintiff": "测原告", "defendant": "测被告"},
                    token=token)
    ok = st == 200 and "id" in resp and str(resp.get("case_no", "")).startswith("LA-")
    check("T7 案件创建成功", ok, f"status={st} resp={resp if st!=200 else resp.get('case_no')}")
    case_id = resp.get("id") if st == 200 else None

    # ---- T8 案件列表 ----
    st, resp = _req("GET", "/api/cases", token=token)
    ok = st == 200 and isinstance(resp, dict) and resp.get("total", 0) >= 1
    check("T8 案件列表可查", ok, f"status={st} total={resp.get('total') if isinstance(resp,dict) else ''}")

    # ---- T9 案件详情 ----
    if case_id:
        st, resp = _req("GET", f"/api/cases/{case_id}", token=token)
        check("T9 案件详情可查", st == 200, f"status={st}")
    else:
        check("T9 案件详情可查", False, "无 case_id 可查")

    # ---- T10 案件更新 ----
    if case_id:
        st, resp = _req("PUT", f"/api/cases/{case_id}",
                         {"case_type": "自动化测试-已改", "status": "done"}, token=token)
        ok = st == 200 and resp.get("case_type") == "自动化测试-已改"
        check("T10 案件更新成功", ok, f"status={st}")
    else:
        check("T10 案件更新成功", False, "无 case_id 可更新")

    # ---- T11 不存在的案件 404 ----
    st, _ = _req("GET", "/api/cases/999999", token=token)
    check("T11 不存在案件应 404", st == 404, f"status={st}")

    # ---- T12 客户创建 + 列表 ----
    st, resp = _req("POST", "/api/clients",
                    {"name": "测试客户", "phone": "13900000099", "company": "测试公司"},
                    token=token)
    ok = st == 200 and (resp.get("data", {}).get("name") == "测试客户")
    check("T12 客户创建成功", ok, f"status={st}")
    client_id = (resp.get("data", {}).get("id")) if st == 200 else None

    st, resp = _req("GET", "/api/clients", token=token)
    ok = st == 200 and isinstance(resp, dict) and resp.get("data", {}).get("total", 0) >= 1
    check("T13 客户列表可查", ok, f"status={st}")

    # ---- T14 日程创建 + 列表 ----
    st, resp = _req("POST", "/api/schedules",
                    {"event_type": "开庭", "event_date": "2026-09-09T09:00:00"}, token=token)
    ok = st == 200 and "data" in resp and "id" in resp.get("data", {})
    check("T14 日程创建成功", ok, f"status={st}")
    sched_id = (resp.get("data", {}).get("id")) if st == 200 else None

    st, resp = _req("GET", "/api/schedules?month=2026-09", token=token)
    ok = st == 200 and isinstance(resp, dict) and len(resp.get("data", [])) >= 1
    check("T15 日程列表可查(按月)", ok, f"status={st}")

    # ---- T16 文书历史 ----
    st, resp = _req("GET", "/api/documents/history", token=token)
    ok = st == 200 and isinstance(resp, dict) and "items" in resp.get("data", {})
    check("T16 文书历史可查", ok, f"status={st}")

    # ---- 清理测试数据 ----
    print("-" * 60)
    print("清理测试数据...")
    if case_id:
        st, _ = _req("DELETE", f"/api/cases/{case_id}", token=token)
        print(f"     删除案件 case_id={case_id} -> {st}")
    if client_id:
        st, _ = _req("DELETE", f"/api/clients/{client_id}", token=token)
        print(f"     删除客户 client_id={client_id} -> {st}")
    if sched_id:
        st, _ = _req("DELETE", f"/api/schedules/{sched_id}", token=token)
        print(f"     删除日程 sched_id={sched_id} -> {st}")

    return summarize()


def summarize():
    print("=" * 60)
    passed = sum(1 for _, p, _ in results if p)
    failed = len(results) - passed
    print(f"测试结果: {passed} 通过 / {failed} 失败 / 共 {len(results)} 项")
    if failed:
        print("失败项:")
        for name, p, detail in results:
            if not p:
                print(f"  - {name}: {detail}")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
