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

    # Command for clean, robust zero-dependency build
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "NyangBuddy",
        "--icon", icon_path,
        "--add-data", "assets;assets",
        "--collect-all", "PyQt6",
        "main.py"
    ]
    print(f"[Build] Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("\n[Build] SUCCESS! Standalone distribution created at: dist/NyangBuddy/NyangBuddy.exe 🎉")


if __name__ == "__main__":
    build()
