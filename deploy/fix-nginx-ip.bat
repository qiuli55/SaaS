@echo off
chcp 65001 >nul
title Lexi 莱希 - nginx IP 直访修复

echo.
echo ========================================
echo   Lexi 莱希 - nginx 修复（IP 直访版）
echo ========================================
echo.
echo 此脚本会:
echo   1. 把 dist/ 备份为 dist.bak.MMDDHHMM
echo   2. 同步本机新 build 的 dist 到服务器
echo   3. 覆盖 nginx.conf 为「IP 直访版」
echo   4. 重启 nginx 8001
echo.
echo 请在 **服务器上** 以 **管理员身份** 运行此 bat。
echo （假设服务器路径: C:\SaaS\frontend\dist 和 C:\SaaS\nginx\conf\）
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请右键此文件 - "以管理员身份运行"
    pause
    exit /b 1
)

:: ============== 1. 备份并准备新 dist ==============
set "DIST=C:\SaaS\frontend\dist"
set "NGINX=C:\SaaS\nginx"

if exist "%DIST%" (
    echo [1/5] 备份旧 dist...
    for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%a"
    set "STAMP=%DT:~4,4%%DT:~8,2%%DT:~10,2%%DT:~12,2%%DT:~14,2%"
    ren "%DIST%" "dist.bak.%STAMP%"
    echo       备份完成: dist.bak.%STAMP%
) else (
    echo [1/5] 旧 dist 不存在，跳过备份
)

echo [2/5] 创建 dist 目录...
mkdir "%DIST%" 2>nul

echo.
echo ================================
echo  请手动把新 dist 内容复制到:
echo    %DIST%\
echo  可以从 F:\文件\SaaS\frontend\dist\ 整个文件夹复制过去
echo  也可以用 scp / xcopy / 共享文件夹 / 远程桌面拖拽
echo ================================
echo.
pause

:: ============== 2. 备份并替换 nginx.conf ==============
echo.
if exist "%NGINX%\conf\nginx.conf" (
    echo [3/5] 备份旧 nginx.conf...
    for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%a"
    set "STAMP=%DT:~4,4%%DT:~8,2%%DT:~10,2%%DT:~12,2%%DT:~14,2%"
    copy /Y "%NGINX%\conf\nginx.conf" "%NGINX%\conf\nginx.conf.bak.%STAMP%" >nul
    echo       备份完成: nginx.conf.bak.%STAMP%
)

echo [4/5] 写入新的 nginx.conf (IP 直访版)...
> "%NGINX%\conf\nginx.conf" (
echo worker_processes 1;
echo events { worker_connections 1024; }
echo http {
echo     include       mime.types;
echo     default_type  application/octet-stream;
echo     sendfile        on;
echo     keepalive_timeout  65;
echo     client_max_body_size 50m;
echo.
echo     # ============== 80：主入口（IP / 域名都能访问） ==============
echo     server {
echo         listen      80;
echo         listen      [::]:80;
echo         server_name qiuli55.top www.qiuli55.top _;
echo.
echo         root  C:/SaaS/frontend/dist;
echo         index index.html;
echo.
echo         gzip on;
echo         gzip_min_length 1k;
echo         gzip_types text/plain text/css text/javascript application/javascript application/json application/xml image/svg+xml;
echo         gzip_vary on;
echo.
echo         # SPA history fallback
echo         location / {
echo             try_files $uri $uri/ /index.html;
echo         }
echo.
echo         # 静态资源缓存
echo         location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?|ttf|eot)$ {
echo             expires 30d;
echo             access_log off;
echo             add_header Cache-Control "public, max-age=2592000";
echo             try_files $uri =404;
echo         }
echo.
echo         # 后端 API 反代到 uvicorn 8001
echo         location /api/ {
echo             proxy_pass         http://127.0.0.1:8001/api/;
echo             proxy_http_version 1.1;
echo             proxy_set_header   Host              $host;
echo             proxy_set_header   X-Real-IP         $remote_addr;
echo             proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
echo             proxy_set_header   X-Forwarded-Proto $scheme;
echo             proxy_read_timeout  240s;
echo             proxy_send_timeout  240s;
echo             proxy_connect_timeout 60s;
echo         }
echo.
echo         # 上传文件目录
echo         location /uploads/ {
echo             alias C:/SaaS/backend/uploads/;
echo             autoindex off;
echo         }
echo.
echo         location = /healthz {
echo             return 200 "ok\n";
echo             add_header Content-Type text/plain;
echo         }
echo     }
echo.
echo     # ============== 443：HTTPS（正式 SSL 证书到位后再启用） ==============
echo     # 当前服务器用的是自签名证书或还没申请正式证书，
echo     # 直接走 80 端口可以立即访问。拿到正式证书后取消下面注释并配证书路径。
echo     # server {
echo     #     listen      443 ssl;
echo     #     listen      [::]:443 ssl;
echo     #     server_name qiuli55.top www.qiuli55.top;
echo     #     ssl_certificate     C:/SaaS/nginx/conf/ssl/qiuli55.top.crt;
echo     #     ssl_certificate_key C:/SaaS/nginx/conf/ssl/qiuli55.top.key;
echo     #     ssl_protocols       TLSv1.2 TLSv1.3;
echo     #     ssl_ciphers         HIGH:!aNULL:!MD5;
echo     #     root  C:/SaaS/frontend/dist;
echo     #     location / { try_files $uri $uri/ /index.html; }
echo     #     location /api/ { proxy_pass http://127.0.0.1:8001/api/; }
echo     # }
echo }
)
echo       写入完成

:: ============== 3. 重启 nginx ==============
echo.
echo [5/5] 重启 nginx...
cd /d "%NGINX%"
taskkill /F /IM nginx.exe 2>nul
timeout /t 2 /nobreak >nul

:: 校验配置
"%NGINX%\nginx.exe" -t
if %errorlevel% neq 0 (
    echo.
    echo [失败] nginx.conf 配置校验失败！
    echo        请检查 %NGINX%\conf\nginx.conf
    pause
    exit /b 1
)

:: 启动 nginx
start "法律AI前端(nginx)" "%NGINX%\nginx.exe"
timeout /t 2 /nobreak >nul

:: ============== 4. 验证 ==============
echo.
echo ========================================
echo   修复完成！
echo.
echo   访问测试 (服务器本机或外网):
echo     1. 健康检查: curl http://127.0.0.1/healthz
echo     2. 首页:     curl -I http://127.0.0.1/
echo     3. API:      curl http://127.0.0.1/api/
echo     4. 外网:     http://159.75.222.60/
echo.
echo   如果还卡在「一直刷新」，检查:
echo     - 浏览器禁用缓存后重试 (Ctrl+F5)
echo     - 服务器防火墙放行 80 端口 (腾讯云安全组)
echo     - 后端 uvicorn 8001 在跑: netstat -ano | findstr :8001
echo ========================================
echo.
pause
