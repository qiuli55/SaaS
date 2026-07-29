"""自动访问各省数据开放平台并下载律所数据"""
import time, os, glob
from playwright.sync_api import sync_playwright

DOWNLOADS = "G:/律师SaaS/backend/downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

# 各省律所数据页面（搜"律师事务所"结果）
PORTS = {
    "山东": "https://data.sd.gov.cn/portal/catalog/0ab73b80b2974b128ff9e9e6e857e963",
    "浙江": "https://data.zj.gov.cn/",
    "广东": "https://gddata.gd.gov.cn/",
}


def try_shandong(page):
    """山东：已知目录页，直接下载"""
    print("[山东] 加载...")
    page.goto(PORTS["山东"], timeout=60000, wait_until="networkidle")
    time.sleep(8)

    # 勾选文件
    page.evaluate("""() => {
        document.querySelectorAll('input[type=checkbox]').forEach(cb => {
            try { if (!cb.checked) cb.click(); } catch(e) {}
        });
    }""")
    time.sleep(1)

    # 点批量下载
    page.evaluate("""() => {
        for (let b of document.querySelectorAll('button')) {
            if ((b.innerText||'').includes('批量下载')) { b.click(); return 'ok'; }
        }
    }""")
    time.sleep(5)
    return True


def try_generic(page, name, url):
    """通用：搜索-下载"""
    print(f"[{name}] 打开 {url}")
    page.goto(url, timeout=60000, wait_until="networkidle")
    time.sleep(5)

    # 找搜索框
    page.evaluate("""() => {
        for (let i of document.querySelectorAll('input[type=text], input[type=search], input:not([type])')) {
            i.value = '律师事务所';
            try { i.dispatchEvent(new Event('input', {bubbles:true})); } catch(e) {}
            try {
                let f = document.querySelector('form');
                if (f) { f.submit(); return 'submitted'; }
            } catch(e) {}
            let btns = document.querySelectorAll('button');
            for (let b of btns) {
                if ((b.innerText||'').includes('搜索')||(b.innerText||'').includes('查询')) {
                    b.click(); return 'clicked';
                }
            }
            return 'typed';
        }
        return 'no input';
    }""")
    time.sleep(5)

    # 截图看结果
    page.screenshot(path=f"G:/律师SaaS/backend/{name}_search.png")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1366, "height": 900},
        )
        page = context.new_page()

        # 先试山东（确定性最高）
        try:
            try_shandong(page)
        except Exception as e:
            print(f"  山东失败: {e}")
            page.screenshot(path="G:/律师SaaS/backend/shandong_error.png")

        # 等下载完成
        time.sleep(10)
        browser.close()

    # 导入下载的文件
    imported = False
    for ext in ["*.xls", "*.xlsx", "*.csv", "*.zip"]:
        files = glob.glob(os.path.join(DOWNLOADS, ext))
        if files:
            print(f"\n发现 {len(files)} 个文件")
            for f in files[:1]:
                print(f"导入: {f}")


if __name__ == "__main__":
    main()