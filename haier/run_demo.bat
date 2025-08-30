@echo off
title 海康 Demo 一键启动
color 0A

:: 设置控制台编码为 UTF-8
chcp 65001 > nul

:: 获取当前目录
set ROOT=%~dp0
set PYTHON=python

echo 🚀 正在启动海康 Demo …
echo.

:: 1. 启动 Flask 后端
start "Flask-Backend" cmd /k "%PYTHON% "%ROOT%backend\flask_backend.py""

:: 稍等 1 秒，让后端先起来
timeout /t 1 /nobreak > nul

:: 2. 启动 pygame 前端
start "PyQt6-Viewer" cmd /k "%PYTHON% "%ROOT%frontend\qt_viewer.py""

:: 再等 1 秒
timeout /t 1 /nobreak > nul

:: 3. 启动 Streamlit 控制面板
start "Streamlit-Control" cmd /k "%PYTHON% -m streamlit run "%ROOT%streamlit_control.py" --server.headless true"

echo.
echo ✅ 全部窗口已启动！
echo 关闭本窗口即可一键结束全部子进程。
pause