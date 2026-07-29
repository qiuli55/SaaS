## SSL 证书申请指南

### 方案一：腾讯云免费证书（推荐，最简单）

1. 登录 [腾讯云 SSL 证书控制台](https://console.cloud.tencent.com/ssl)
2. 点击「申请免费证书」→ 选择「亚洲诚信(DV)」→ 域名填 `qiuli55.top`
3. 验证方式选「DNS 验证」（域名在腾讯云的话会自动验证）
4. 审核通过后下载 nginx 格式证书
5. 把 `.crt` 文件放到 `deploy/nginx/conf/ssl/qiuli55.top.crt`
6. 把 `.key` 文件放到 `deploy/nginx/conf/ssl/qiuli55.top.key`
7. 重启 nginx：`nginx.exe -s reload`

### 方案二：Let's Encrypt（免费，90天自动续）

1. 下载 [win-acme](https://www.win-acme.com/) 到服务器
2. 运行 wacs.exe → 选择 N (新建证书) → 选择 2 (Manual input)
3. 输入域名 `qiuli55.top` 和 `www.qiuli55.top`
4. 验证方式选 `[http-01] SelfHosting`
5. 安装方式选 nginx 路径
6. 证书会自动生成并配置到 nginx

### DNS 解析确认

确保域名 DNS 已指向服务器 IP `159.75.222.60`：
- `qiuli55.top` → A 记录 → `159.75.222.60`
- `www.qiuli55.top` → CNAME → `qiuli55.top`

### 验证 SSL 是否生效

申请完成后访问 `https://qiuli55.top` 应看到锁图标。
