"""Playwright DOM直抓：开浏览器→点查询→等结果→从表格提取→翻页"""
import time, sqlite3
from playwright.sync_api import sync_playwright

DB = "G:/律师SaaS/backend/legal_ai.db"


def main():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS law_firms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200), city VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    from_count = conn.execute("SELECT COUNT(*) FROM law_firms").fetchone()[0]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 显示窗口
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = browser.new_page(
            viewport={"width": 1366, "height": 900}, locale="zh-CN"
        )

        page.goto("https://credit.acla.org.cn/credit/lawFirm", wait_until="load", timeout=60000)
        print("页面加载完成，等待渲染...")
        time.sleep(8)

        # 直接点查询
        clicked = page.evaluate("""() => {
            let btns = document.querySelectorAll('button, a.btn, input[type=button]');
            for (let b of btns) {
                let t = (b.innerText || b.value || '').trim();
                if (t === '查询' || t === '检索' || t === '搜索') {
                    b.click(); return 'clicked:' + t;
                }
            }
            return 'no button';
        }""")
        print(f"点击结果: {clicked}")
        time.sleep(8)

        total = 0
        for pg in range(1, 500):
            # 从 DOM 表格提取律所名
            items = page.evaluate("""() => {
                let results = [];
                // 尝试多种选择器
                let links = document.querySelectorAll('a');
                for (let a of links) {
                    let t = (a.innerText || a.textContent || '').trim();
                    if (t.includes('律师事务所') && t.length > 6 && t.length < 80) {
                        results.push(t);
                    }
                }
                // 也搜 td
                let tds = document.querySelectorAll('td');
                for (let td of tds) {
                    let t = td.innerText.trim();
                    if (t.includes('律师事务所') && !t.includes('class=') && t.length < 80) {
                        results.push(t);
                    }
                }
                return [...new Set(results)];
            }""")

            if not items:
                print(f"  页{pg}: 0条")
                page.screenshot(path=f"G:/律师SaaS/backend/page{pg}_empty.png")
                if pg == 1:
                    print("  首页无数据，尝试保存原始HTML...")
                    html = page.content()
                    with open(f"G:/律师SaaS/backend/page_source.html", "w", encoding="utf-8") as f:
                        f.write(html[:50000])
                    print(f"  HTML已保存({len(html)}字符)")
                break

            for name in items:
                name = name.strip()
                if len(name) > 6 and len(name) < 80:
                    conn.execute("INSERT OR IGNORE INTO law_firms (name, city) VALUES (?,?)", (name, ""))
            total += len(items)
            conn.commit()
            print(f"  页{pg}: {len(items)}条, 累计{total}")

            if len(items) < 5:
                break

            # 点下一页
            found_next = page.evaluate("""() => {
                for (let el of document.querySelectorAll('a, button, li')) {
                    let t = (el.innerText || '').trim();
                    if (t === '下一页' || t === '\u4e0b\u4e00\u9875' || t === '>') {
                        el.click(); return 'clicked';
                    }
                }
                // 试试 class
                let nextBtn = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled), .page-next:not(.disabled), li.next a');
                if (nextBtn) { nextBtn.click(); return 'found by class'; }
                return 'no next';
            }""")
            if found_next == 'no next':
                print("  无下一页")
                break

            time.sleep(3)

        browser.close()

    final = conn.execute("SELECT COUNT(*) FROM law_firms").fetchone()[0]
    conn.close()
    print(f"\n=== 完成 === 新增 {final - from_count} 条, 总计 {final}")


if __name__ == "__main__":
    main()