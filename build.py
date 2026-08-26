import os
import sys
import subprocess


def build():
    print("=== NyangBuddy Desktop Pet — Standalone Packaging Build ===")

    # Ensure assets and icon
    icon_path = os.path.join("assets", "icon.ico")
    if not os.path.exists(icon_path):
        from PIL import Image
        from src.sprites import render_cat_frame
        img = render_cat_frame("boss_oyen", "idle", 0, look_dx=0, look_dy=0, accessory="wizard_hat")
        os.makedirs("assets", exist_ok=True)
        img.save(icon_path, format="ICO", sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256)])

    # PyInstaller optimized lightweight standalone command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "NyangBuddy",
        "--icon", icon_path,
        "--exclude-module", "PyQt6.QtQml",
        "--exclude-module", "PyQt6.QtQuick",
        "--exclude-module", "PyQt6.Qt3DCore",
        "--exclude-module", "PyQt6.Qt3DRender",
        "--exclude-module", "PyQt6.Qt3DInput",
        "--exclude-module", "PyQt6.Qt3DAnimation",
        "--exclude-module", "PyQt6.Qt3DExtras",
        "--exclude-module", "PyQt6.QtWebEngineCore",
        "--exclude-module", "PyQt6.QtWebEngineWidgets",
        "--exclude-module", "PyQt6.QtWebEngineQuick",
        "--exclude-module", "PyQt6.QtSql",
        "--exclude-module", "PyQt6.QtDesigner",
        "--exclude-module", "PyQt6.QtMultimedia",
        "--exclude-module", "PyQt6.QtMultimediaWidgets",
        "--exclude-module", "PyQt6.QtBluetooth",
        "--exclude-module", "PyQt6.QtNfc",
        "--exclude-module", "PyQt6.QtPositioning",
        "--exclude-module", "PyQt6.QtSensors",
        "--exclude-module", "PyQt6.QtSerialPort",
        "--exclude-module", "PyQt6.QtRemoteObjects",
        "--exclude-module", "PyQt6.QtTextToSpeech",
        "--exclude-module", "tkinter",
        "--exclude-module", "unittest",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "pynput._util._win32",
        "--hidden-import", "pynput._util",
        "--hidden-import", "pynput",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "ctypes.wintypes",
        "--hidden-import", "src.sprites",
        "--hidden-import", "src.pet_window",
        "--hidden-import", "src.global_hooks",
        "--hidden-import", "src.ai_watcher",
        "--hidden-import", "src.pomodoro",
        "--hidden-import", "src.sticky_note",
        "--hidden-import", "src.tray",
        "--hidden-import", "src.settings",
        "--hidden-import", "src.audio",
        "main.py"
    ]
    print(f"[Build] Executing optimized lightweight build...")
    subprocess.check_call(cmd)
    print("\n[Build] SUCCESS! Ultra-lightweight standalone executable created at: dist/NyangBuddy.exe")


if __name__ == "__main__":
    build()
