"""
全国律师事务所数据采集（从司法部官方平台）
运行: python fetch_all_firms.py

数据来源: credit.acla.org.cn（司法部全国律师执业诚信信息公示平台）
"""
import httpx, json, sqlite3, time, os

DB_PATH = "G:/律师SaaS/backend/legal_ai.db"
API_URL = "https://credit.acla.org.cn/api/lawfirm/search"

cities = [
    "北京","上海","广州","深圳","成都","重庆","杭州","南京","武汉","长沙",
    "郑州","合肥","福州","厦门","天津","济南","青岛","南昌","石家庄","太原",
    "呼和浩特","哈尔滨","长春","沈阳","大连","西安","兰州","西宁","银川",
    "乌鲁木齐","昆明","贵阳","南宁","海口","拉萨","珠海","东莞","中山",
    "佛山","惠州","宁波","温州","无锡","常州","苏州","南通","徐州","烟台",
    "潍坊","淄博","济宁","临沂","洛阳","南阳","襄阳","宜昌","荆州","岳阳",
    "株洲","湘潭","衡阳","柳州","桂林","三亚","金华","绍兴","嘉兴","湖州",
    "台州","漳州","泉州","芜湖","马鞍山","九江","赣州","秦皇岛","唐山",
    "保定","邯郸","廊坊","大同","运城","包头","鄂尔多斯","大庆","齐齐哈尔",
    "吉林","延边","锦州","鞍山","抚顺","宝鸡","咸阳","天水","石嘴山","克拉玛依",
    "曲靖","大理","遵义","六盘水","北海","防城港",
]

def fetch_city(city: str, conn: sqlite3.Connection, page_size: int = 50):
    """爬取一个城市的所有律所"""
    print(f"\n[{city}] 开始抓取...")
    total = 0
    page = 1
    session = httpx.Client(timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://credit.acla.org.cn/",
        "Accept": "application/json",
    })

    while True:
        try:
            resp = session.post(API_URL, json={
                "keyword": "",
                "city": city,
                "page": page,
                "pageSize": page_size,
            })
            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code} at page {page}, 跳过")
                break

            data = resp.json()
            items = data.get("data", {}).get("list", [])
            if not items:
                break

            for item in items:
                name = item.get("firmName", "") or item.get("name", "")
                if not name:
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO law_firms (name, city) VALUES (?, ?)",
                    (name.strip(), city)
                )

            count = len(items)
            total += count
            print(f"  第{page}页: {count}条, 累计{total}条", end="\r")

            if count < page_size:
                break
            page += 1
            time.sleep(0.3)  # 礼貌延迟

        except Exception as e:
            print(f"\n  错误: {e}, 跳过")
            break

    print(f"\n[{city}] 完成: 共 {total} 条")
    return total


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS law_firms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200),
        city VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    grand_total = 0
    for city in cities:
        try:
            count = fetch_city(city, conn)
            grand_total += count
            conn.commit()
        except Exception as e:
            print(f"\n[{city}] 失败: {e}")

    existing = conn.execute("SELECT COUNT(*) FROM law_firms").fetchone()[0]
    conn.close()
    print(f"\n\n=== 完成 ===\n本次新增: {grand_total}\n数据库总计: {existing}")
