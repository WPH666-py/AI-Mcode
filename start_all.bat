@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   数学建模 AI 生成器 - 前后端同时启动
echo ============================================================
echo.

echo [1/4] 检查 Python 环境...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python 3.10+
    pause
    exit /b 1
)

echo [2/4] 检查 Node 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo [3/4] 初始化数据库...
if not exist "db.sqlite3" (
    py manage.py makemigrations accounts projects --noinput
    py manage.py migrate --noinput
) else (
    echo         数据库已存在，跳过初始化
)

echo [4/4] 启动服务...
echo         后端: http://127.0.0.1:3018
echo         前端: http://127.0.0.1:3020
echo.

start "MathModel Backend 3018" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%~dp0'; py manage.py runserver 127.0.0.1:3018"
start "MathModel Frontend 3020" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%~dp0frontend'; if (-not (Test-Path node_modules)) { npm install }; npm run dev"

echo ============================================================
echo   已启动两个窗口：后端 3018，前端 3020
echo   浏览器访问: http://127.0.0.1:3020
echo ============================================================
echo.
pause
