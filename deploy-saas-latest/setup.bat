@echo off
chcp 65001 >nul
title 法律AI助手 - 一键部署

echo.
echo ========================================
echo   法律AI助手 - 服务器部署脚本
echo   域名: qiuli55.top
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请右键此文件 - "以管理员身份运行"
    pause
    exit /b 1
)

:: 安装 Python（如果未安装）
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/6] 安装 Python...
    curl -L -o python-installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo [完成] Python 安装完毕
) else (
    echo [1/6] Python 已安装
)

:: 刷新 PATH
set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311"

:: 安装依赖
echo.
echo [2/6] 安装 Python 依赖...
pip install fastapi uvicorn sqlalchemy python-jose bcrypt python-multipart python-docx httpx pydantic aiofiles python-dotenv fpdf2 openpyxl requests -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 配置防火墙
echo.
echo [3/6] 配置防火墙...
netsh advfirewall firewall add rule name="法律AI后端(8001)" dir=in action=allow protocol=TCP localport=8001 2>nul
netsh advfirewall firewall add rule name="法律AI-HTTP(80)" dir=in action=allow protocol=TCP localport=80 2>nul
netsh advfirewall firewall add rule name="法律AI-HTTPS(443)" dir=in action=allow protocol=TCP localport=443 2>nul

:: 启动后端服务 (必须先停掉旧进程)
echo.
echo [4/6] 启动后端服务 (端口 8001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001.*LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul
cd /d %~dp0backend
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
start "法律AI后端" cmd /c "set PYTHONIOENCODING=utf-8 && set PYTHONUTF8=1 && python -m uvicorn main:app --host 0.0.0.0 --port 8001"

:: 安装并配置 nginx
echo.
echo [5/6] 配置 nginx...

:: 下载 nginx（首次）
if not exist "%~dp0nginx" (
    echo   下载 nginx...
    curl -L -o nginx.zip https://nginx.org/download/nginx-1.26.1.zip
    powershell -Command "Expand-Archive -Path nginx.zip -DestinationPath . -Force"
    del nginx.zip
    for /d %%i in (nginx-*) do ren "%%i" nginx
)

:: 创建 SSL 证书目录
if not exist "%~dp0nginx\conf\ssl" mkdir "%~dp0nginx\conf\ssl"

:: 生成自签名临时证书（正式上线换成 Let's Encrypt 证书）
if not exist "%~dp0nginx\conf\ssl\qiuli55.top.crt" (
    echo   生成自签名证书（临时），正式上线请替换为 Let's Encrypt 证书...
    powershell -Command ^
      "$cert = New-SelfSignedCertificate -DnsName qiuli55.top -CertStoreLocation Cert:\LocalMachine\My; ^
       Export-Certificate -Cert $cert -FilePath '%~dp0nginx\conf\ssl\qiuli55.top.crt' -Type CERT; ^
       $pwd = ConvertTo-SecureString -String 'temp123' -Force -AsPlainText; ^
       Export-PfxCertificate -Cert $cert -FilePath '%~dp0nginx\conf\ssl\qiuli55.top.pfx' -Password $pwd"
    :: 自签名证书需要提取私钥，暂时跳过，用 HTTP-only 配置
    echo   自签名证书已生成，SSL 配置待手动完成
)

:: 配置 nginx（HTTP + HTTPS）
> "%~dp0nginx\conf\nginx.conf" (
echo worker_processes 1;
echo events { worker_connections 1024; }
echo http {
echo     include mime.types;
echo     default_type application/octet-stream;
echo     sendfile on;
echo     keepalive_timeout 65;
echo     client_max_body_size 50m;
echo     
echo     # HTTP - 重定向到 HTTPS
echo     server {
echo         listen 80;
echo         server_name qiuli55.top www.qiuli55.top;
echo         return 301 https://$host$request_uri;
echo     }
echo     
echo     # HTTPS
echo     server {
echo         listen 443 ssl;
echo         server_name qiuli55.top www.qiuli55.top;
echo         
echo         ssl_certificate     conf/ssl/qiuli55.top.crt;
echo         ssl_certificate_key conf/ssl/qiuli55.top.key;
echo         ssl_protocols TLSv1.2 TLSv1.3;
echo         ssl_ciphers HIGH:!aNULL:!MD5;
echo         
echo         root "%~dp0frontend\dist";
echo         
echo         location / {
echo             try_files $uri $uri/ /index.html;
echo         }
echo         
echo         location /api/ {
echo             proxy_pass http://127.0.0.1:8001/api/;
echo             proxy_set_header Host $host;
echo             proxy_set_header X-Real-IP $remote_addr;
echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo             proxy_set_header X-Forwarded-Proto $scheme;
echo         }
echo         
echo         location /uploads/ {
echo             alias "%~dp0backend\uploads\";
echo         }
echo     }
echo }
)

:: 启动 nginx
cd /d "%~dp0nginx"
taskkill /F /IM nginx.exe 2>nul
timeout /t 2 /nobreak >nul
start "法律AI前端" nginx.exe

:: 完成
echo.
echo [6/6] 配置数据库自动备份...
:: 每天凌晨3点备份数据库
schtasks /create /tn "法律AI-数据库备份" /tr "copy /Y %~dp0backend\legal_ai.db %~dp0backend\backup\legal_ai_%%date:~0,4%%%%date:~5,2%%%%date:~8,2%%.db" /sc daily /st 03:00 /f 2>nul
if not exist "%~dp0backend\backup" mkdir "%~dp0backend\backup"

echo.
echo ========================================
echo   部署完成！
echo.
echo   访问地址: https://qiuli55.top
echo   后端 API: http://localhost:8001
echo ========================================
echo.
echo ⚠️  下一步:
echo    1. 腾讯云安全组放行 80、443 端口
echo    2. DNS 解析 qiuli55.top 指向服务器 IP
echo    3. 申请正式 SSL 证书（见 SSL-SETUP.md）
echo.
pause
