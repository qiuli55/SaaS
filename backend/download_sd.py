"""用 Playwright 加载山东政府开放数据页,自动下载 XLSX"""
import time, os
from playwright.sync_api import sync_playwright

DOWNLOAD_DIR = "G:/律师SaaS/backend"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

URL = "https://data.sd.gov.cn/portal/catalog/0ab73b80b2974b128ff9e9e6e857e963"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        accept_downloads=True,
        viewport={"width": 1366, "height": 900},
    )
    page = context.new_page()
    page.goto(URL, timeout=60000, wait_until="networkidle")
    time.sleep(5)

    # 提取所有文件链接
    files = page.evaluate("""() => {
        let results = [];
        document.querySelectorAll('a, button, .file-item').forEach(el => {
            let t = (el.innerText || '').trim();
            if (el.tagName === 'A' && el.href && /\\.(xls|xlsx|csv|json|rdf|xml)$/i.test(el.href)) {
                results.push({type: 'link', name: t || el.href, url: el.href});
            }
        });
        return results;
    }""")
    print(f"找到 {len(files)} 个下载链接")
    for f in files[:5]:
        print(f"  - {f['name'][:50]}")

    # 模拟点击 XLSX 下载按钮（如果按钮形式）
    if not files:
        print("尝试点击 XLSX 按钮下载...")
        # 全选多选框
        page.evaluate("""() => {
            document.querySelectorAll('input[type=checkbox]').forEach(c => c.click());
        }""")
        time.sleep(1)
        # 点批量下载
        btn = page.locator("button:has-text('批量下载')").first
        if btn.count():
            print("找到批量下载按钮")
        else:
            print("找不到批量下载按钮，尝试直接抓所有 download 链接")
            # 找 data-url 之类的属性
            more = page.evaluate("""() => {
                let r = [];
                document.querySelectorAll('[data-url], [data-href], [data-link], [data-id]').forEach(el => {
                    r.push({tag: el.tagName, data: el.dataset});
                });
                return r;
            }""")
            print(f"  找到 {len(more)} 个 data 属性")

    browser.close()