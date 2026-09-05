"""订阅计费与配额测试：套餐 / 订单 / 模拟支付 / 取消订阅权益保留 / 用量限额"""
import pytest

from conftest import TestSessionLocal


def _buy_and_pay(api, auth, plan_code, period="monthly"):
    """下单并模拟支付，返回订单号。"""
    r = api.post("/api/billing/orders", json={"plan_code": plan_code, "period": period}, headers=auth)
    assert r.status_code == 200, r.json()
    order_no = r.json()["order_no"]
    r2 = api.post(f"/api/billing/orders/{order_no}/pay", headers=auth)
    assert r2.status_code == 200, r2.json()
    assert r2.json()["status"] == "paid"
    return order_no


class TestPlans:
    def test_plans_listed(self, api, auth):
        r = api.get("/api/billing/plans", headers=auth)
        assert r.status_code == 200
        codes = [p["code"] for p in r.json()["plans"]]
        assert codes == ["free", "basic", "pro"]
        assert r.json()["pay_method"] == "mock"


class TestOrderFlow:
    def test_free_plan_cannot_buy(self, api, auth):
        r = api.post("/api/billing/orders", json={"plan_code": "free", "period": "monthly"}, headers=auth)
        assert r.status_code == 400

    def test_unknown_plan_404(self, api, auth):
        r = api.post("/api/billing/orders", json={"plan_code": "max", "period": "monthly"}, headers=auth)
        assert r.status_code == 404

    def test_buy_and_subscription_active(self, api, auth):
        order_no = _buy_and_pay(api, auth, "basic")
        sub = api.get("/api/billing/subscription/current", headers=auth).json()
        assert sub["is_paid"] is True
        assert sub["plan"]["code"] == "basic"
        assert sub["daily_limit"] == 500
        orders = api.get("/api/billing/orders", headers=auth).json()["orders"]
        assert any(o["order_no"] == order_no and o["status"] == "paid" for o in orders)

    def test_upgrade_replaces_old_subscription(self, api, auth):
        _buy_and_pay(api, auth, "basic")
        _buy_and_pay(api, auth, "pro", "yearly")
        sub = api.get("/api/billing/subscription/current", headers=auth).json()
        assert sub["plan"]["code"] == "pro"
        assert sub["daily_limit"] is None  # pro 不限量

    def test_invalid_period_rejected(self, api, auth):
        r = api.post("/api/billing/orders", json={"plan_code": "basic", "period": "weekly"}, headers=auth)
        assert r.status_code == 422


class TestCancel:
    def test_cancel_keeps_benefits_until_expiry(self, api, auth):
        """取消订阅后本周期内权益仍在（停续费语义），与前端提示一致。"""
        _buy_and_pay(api, auth, "basic")
        r = api.post("/api/billing/subscription/cancel", headers=auth)
        assert r.status_code == 200
        sub = api.get("/api/billing/subscription/current", headers=auth).json()
        assert sub["is_paid"] is True
        assert sub["plan"]["code"] == "basic"
        assert sub["daily_limit"] == 500
        # 重复取消幂等
        r2 = api.post("/api/billing/subscription/cancel", headers=auth)
        assert r2.status_code == 200

    def test_cancel_without_subscription_400(self, api, auth):
        r = api.post("/api/billing/subscription/cancel", headers=auth)
        assert r.status_code == 400


class TestQuota:
    def test_usage_endpoint_reports_real_limit(self, api, auth):
        """免费用户限额 50；买专业版后限额为不限（null）。"""
        r = api.get("/api/quota/usage", headers=auth)
        assert r.status_code == 200
        assert r.json()["daily_limit"] == 50
        assert r.json()["total"] == 0

        _buy_and_pay(api, auth, "pro")
        r2 = api.get("/api/quota/usage", headers=auth)
        assert r2.json()["daily_limit"] is None

    def test_free_quota_blocks_after_50(self, api, auth):
        from routers.quota import check_quota
        uid = api.get("/api/user/info", headers=auth).json()["id"]
        db = TestSessionLocal()
        try:
            for _ in range(50):
                assert check_quota(uid, "chat", db) is True
            assert check_quota(uid, "chat", db) is False
        finally:
            db.close()
