"""法条校验与法条检索测试：中文数字转换 / 条号核验 / 检索接口（离线部分）"""
from routers.citation import _cn2int, check_citations, render_citation_section


class TestCn2Int:
    def test_arabic_digits(self):
        assert _cn2int("496") == 496

    def test_chinese_numbers(self):
        assert _cn2int("十") == 10
        assert _cn2int("二十") == 20
        assert _cn2int("二百三十") == 230
        assert _cn2int("一千二百六十") == 1260


class TestCheckCitations:
    def test_valid_article_found(self):
        results, ok = check_citations("根据《民法典》第496条的规定……")
        assert ok
        assert results[0]["status"] == "FOUND"
        assert results[0]["id"] == 496

    def test_fake_article_not_found(self):
        results, ok = check_citations("依据《民法典》第9999条")
        assert ok
        assert results[0]["status"] == "NOT_FOUND"

    def test_chinese_numeral_citation(self):
        results, ok = check_citations("依照民法典第五百八十五条")
        assert ok
        assert results[0]["id"] == 585

    def test_no_citation(self):
        results, ok = check_citations("本合同自签订之日起生效。")
        assert ok
        assert results == []


class TestRenderSection:
    def test_section_rendered(self):
        section = render_citation_section("《民法典》第496条与《民法典》第9999条")
        assert section.startswith("## 七、法条引用核验")
        assert "✅" in section and "❌" in section


class TestCitationApi:
    def test_validate_endpoint(self, api, auth):
        r = api.post("/api/citation/validate", json={"text": "《民法典》第5条与《民法典》第8888条"}, headers=auth)
        assert r.status_code == 200
        data = r.json()
        assert data["available"] is True
        statuses = {x["status"] for x in data["results"]}
        assert "FOUND" in statuses and "NOT_FOUND" in statuses

    def test_validate_requires_auth(self, api):
        r = api.post("/api/citation/validate", json={"text": "《民法典》第5条"})
        assert r.status_code == 401


class TestLawSearch:
    def test_empty_query_400(self, api, auth):
        r = api.post("/api/law/search", json={"query": "  "}, headers=auth)
        assert r.status_code == 400

    def test_retrieve_offline(self, api, auth, monkeypatch):
        """检索部分走本地法条库，不依赖 AI Key；命中条款应包含违约金相关法条。"""
        from routers import law_search

        async def fake_ai_search(query, retrieved):
            return "（测试桩）基于 %s 条法条的回答" % len(retrieved)

        monkeypatch.setattr(law_search, "ai_search", fake_ai_search)
        r = api.post("/api/law/search", json={"query": "违约金过分高于造成的损失"}, headers=auth)
        assert r.status_code == 200
        data = r.json()
        assert data["retrieved_count"] > 0
        assert any(x["id"] == 585 for x in data["retrieved"])
        assert "测试桩" in data["answer"]
