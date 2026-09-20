"""路径与字体可移植性测试：防止脚本再次写死 Windows 盘符、字体候选漏掉 Linux 路径"""
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent

# 曾经的写法：数据库/输出目录写死在 G: 盘，Linux 部署时直接打不开
BAD_MARKER = "G:/律师SaaS"

SCRIPTS = [
    "scrape_firms.py",
    "fetch_all_firms.py",
    "seed_firms.py",
    "auto_download.py",
    "download_sd.py",
]


def test_no_hardcoded_windows_drive_in_code():
    """代码里不得再出现写死的 G: 盘路径（注释里说明历史问题不算）"""
    hits = []
    for py in BACKEND.glob("*.py"):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if BAD_MARKER in line and not line.lstrip().startswith("#"):
                hits.append(f"{py.name}:{i}")
    assert hits == [], f"发现写死的盘符路径: {hits}"


def test_scripts_anchor_paths_to_file_location():
    """爬虫脚本应以 __file__ 锚定路径，换工作目录运行也能找到数据库"""
    for name in SCRIPTS:
        src = (BACKEND / name).read_text(encoding="utf-8")
        assert "__file__" in src, f"{name} 未用 __file__ 锚定路径"


def test_chinese_font_candidates_cover_linux():
    """PDF 中文字体候选必须含 Linux 路径，否则服务器导出文书中文乱码"""
    from routers.documents import CN_FONT_CANDIDATES

    assert any(p.startswith("/usr/share/fonts") for p in CN_FONT_CANDIDATES)
