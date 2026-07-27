@echo off
chcp 65001 >nul
title 法律AI助手 - 一键部署

echo.
echo ========================================
echo   法律AI助手 - 服务器部署脚本
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
    echo [1/5] 安装 Python...
    curl -L -o python-installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo [完成] Python 安装完毕
) else (
    echo [1/5] Python 已安装
)

:: 刷新 PATH
set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311"

:: 安装依赖
echo.
echo [2/5] 安装 Python 依赖...
pip install fastapi uvicorn sqlalchemy python-jose bcrypt python-multipart python-docx httpx pydantic aiofiles python-dotenv fpdf2 openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 配置防火墙
echo.
echo [3/5] 配置防火墙...
netsh advfirewall firewall add rule name="法律AI后端" dir=in action=allow protocol=TCP localport=8000 2>nul
netsh advfirewall firewall add rule name="法律AI前端" dir=in action=allow protocol=TCP localport=80 2>nul

:: 启动后端服务
echo.
echo [4/5] 启动后端服务 (端口 8000)...
cd /d %~dp0backend
start "法律AI后端" python -m uvicorn main:app --host 0.0.0.0 --port 8000

:: 安装并启动 nginx
echo.
echo [5/5] 配置前端...

:: 下载 nginx
if not exist "%~dp0nginx" (
    echo   下载 nginx...
    curl -L -o nginx.zip https://nginx.org/download/nginx-1.26.1.zip
    C:\Windows\System32\tar.exe -xf nginx.zip 2>nul
    if %errorlevel% neq 0 (
        powershell -Command "Expand-Archive -Path nginx.zip -DestinationPath ."
    )
    del nginx.zip
    ren nginx-* nginx
)

:: 配置 nginx
> "%~dp0nginx\conf\nginx.conf" (
echo worker_processes 1;
echo events { worker_connections 1024; }
echo http {
echo     include mime.types;
echo     default_type application/octet-stream;
echo     sendfile on;
echo     keepalive_timeout 65;
echo     server {
echo         listen 80;
echo         server_name _;
echo         location / {
echo             root "%~dp0frontend\dist";
echo             try_files $uri $uri/ /index.html;
echo         }
echo         location /api/ {
echo             proxy_pass http://127.0.0.1:8000/api/;
echo             proxy_set_header Host $host;
echo             proxy_set_header X-Real-IP $remote_addr;
echo         }
echo     }
echo }
)

cd /d "%~dp0nginx"
start "法律AI前端" nginx.exe

echo.
echo ========================================
echo   部署完成！
echo   公网地址: http://159.75.222.60
echo   后端地址: http://159.75.222.60:8000
echo ========================================
echo.
echo 如果无法访问，请检查腾讯云安全组是否放行了 80 和 8000 端口
echo.
pause
