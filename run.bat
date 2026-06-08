@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   数学建模 AI 生成器 - 一键启动
echo ============================================================
echo.

echo [检查] Python 环境...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python 3.10+
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('py --version 2^>^&1') do echo         Python %%v

echo [检查] C 加速模块...
py -c "from apps.core import is_accelerated; info=is_accelerated(); print('cython:', info['cython'], 'numba:', info['numba'])" 2>nul
if %errorlevel% equ 0 (
    echo         C 加速已启用 ✓
) else (
    echo         纯 Python 模式运行（C 扩展未编译）
    echo         运行 compile.bat 可编译加速模块
)

echo [检查] 数据库...
if not exist "db.sqlite3" (
    echo         首次运行，初始化数据库...
    py manage.py makemigrations accounts projects --noinput 2>nul
    py manage.py migrate --noinput 2>nul
    echo         数据库初始化完成
) else (
    echo         数据库就绪
)

echo.
echo ============================================================
echo   启动 Django 服务...
echo   后端: http://127.0.0.1:3018
echo   管理: http://127.0.0.1:3018/admin
echo ============================================================
echo.

py manage.py runserver 127.0.0.1:8000

pause
