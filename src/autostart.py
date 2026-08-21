"""
Windows Startup / Autostart Manager for Desktop Cat (NyangBuddy)
Integrates natively with Windows Registry (HKCU Run) using pythonw.exe
for completely silent, windowless background launch on system startup.
Zero admin privileges required (operates safely in user space).
"""

import sys
import os

if sys.platform == "win32":
    import winreg

APP_NAME = "NyangBuddyDesktopCat"


def get_startup_command() -> str:
    """
    Constructs the command line to execute main.py with pythonw.exe (windowless).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_py = os.path.join(base_dir, "main.py")

    # Prefer virtual environment pythonw.exe
    venv_pythonw = os.path.join(base_dir, ".venv", "Scripts", "pythonw.exe")
    if os.path.exists(venv_pythonw):
        python_exe = venv_pythonw
    else:
        # Fallback to system pythonw.exe in python install directory
        sys_dir = os.path.dirname(sys.executable)
        sys_pythonw = os.path.join(sys_dir, "pythonw.exe")
        if os.path.exists(sys_pythonw):
            python_exe = sys_pythonw
        else:
            python_exe = sys.executable

    return f'"{python_exe}" "{main_py}" --startup'


def is_startup_enabled() -> bool:
    """Checks if NyangBuddy is registered in Windows CurrentVersion\\Run."""
    if sys.platform != "win32":
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        return False


def set_startup_enabled(enabled: bool) -> bool:
    """
    Enables or disables auto-start on Windows boot without requiring admin rights.
    """
    if sys.platform != "win32":
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
        )
        if enabled:
            cmd = get_startup_command()
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Autostart] Error updating registry: {e}")
        return False
