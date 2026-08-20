@echo off
title NyangBuddy - Windows Startup Setup
cd /d "%~dp0"

echo ===================================================
echo     NyangBuddy Desktop Cat - Windows Startup Setup
echo ===================================================
echo.
echo 1. Aktifkan Auto-Start saat Windows Nyala
echo 2. Nonaktifkan Auto-Start
echo 3. Keluar
echo.
set /p opt="Pilih opsi (1/2/3): "

if "%opt%"=="1" (
    .\.venv\Scripts\python.exe -c "from src.autostart import set_startup_enabled; set_startup_enabled(True); print('Auto-Start BERHASIL diaktifkan!')"
) else if "%opt%"=="2" (
    .\.venv\Scripts\python.exe -c "from src.autostart import set_startup_enabled; set_startup_enabled(False); print('Auto-Start BERHASIL dinonaktifkan!')"
) else (
    exit /b
)

echo.
pause
