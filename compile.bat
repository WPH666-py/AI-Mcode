@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   数学建模 AI 生成器 - C 扩展编译工具
echo ============================================================
echo.

echo [1/3] 检查 Python 环境...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo         Python 环境 OK

echo [2/3] 安装编译依赖...
py -m pip install cython numpy setuptools wheel -q 2>nul
if %errorlevel% neq 0 (
    echo [警告] pip 安装失败，请检查网络连接
    echo         如果已安装可忽略此警告
)

echo [3/3] 开始编译 C 扩展模块...
echo.
echo   编译目标:
echo     - apps/core/math_utils.pyx   (数学加速库)
echo     - apps/files/parsers_fast.pyx (文件解析加速)
echo     - apps/files/cleaners_fast.pyx(数据清洗加速)
echo.

py setup_cython.py build_ext --inplace

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   ✓ 编译成功！C 扩展模块 (.pyd) 已生成
    echo.
    echo   启动项目:
    echo     py manage.py runserver
    echo     cd frontend ^&^& npm run dev
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   ✗ 编译失败！
    echo   请检查:
    echo   1. 是否安装了 Visual Studio Build Tools (MSVC)
    echo      下载: https://visualstudio.microsoft.com/downloads/
    echo   2. pip install cython numpy
    echo   3. 项目将以纯 Python 模式继续运行
    echo ============================================================
)

pause
