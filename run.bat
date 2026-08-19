@echo off
title NyangBuddy Desktop Pet
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment tidak ditemukan.
    echo Membuat .venv dan menginstall dependensi...
    python -m venv .venv
    .\.venv\Scripts\pip install PyQt6 Pillow
)

start "" ".\.venv\Scripts\pythonw.exe" main.py
