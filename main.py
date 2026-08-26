"""
NyangBuddy - 100% Local, Private & Safe Desktop Companion
Inspired by cozy virtual pets (like Comnyang) but built from scratch with zero telemetry,
open-source Python code, and local-only interactions.
"""

import sys
import os
import ctypes
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.settings import load_settings
from src.pet_window import DesktopPet
from src.tray import CatTrayIcon


def main():
    try:
        if "--startup" in sys.argv:
            # Defer heavy loading by 5 seconds on Windows boot
            # so it doesn't fight for resources with other startup apps.
            time.sleep(5)

        # Ensure CWD is the project root (critical for autostart from Windows Registry
        # which would otherwise launch from C:\Windows\System32)
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
            os.chdir(exe_dir)
        else:
            project_root = os.path.dirname(os.path.abspath(__file__))
            os.chdir(project_root)

        # Enable Windows High-Precision Timer Period (1ms resolution) for rock-solid 60 FPS
        if sys.platform == "win32":
            try:
                ctypes.windll.winmm.timeBeginPeriod(1)
            except Exception:
                pass

        # Enable High DPI scaling
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        app = QApplication(sys.argv)
        app.setApplicationName("NyangBuddy")
        app.setQuitOnLastWindowClosed(False)

        # Load local settings
        settings = load_settings()

        # Create Pet Window
        pet = DesktopPet(settings)
        pet.show()

        # Create Tray Icon
        tray = CatTrayIcon(pet, app)

        ret = app.exec()

        if sys.platform == "win32":
            try:
                ctypes.windll.winmm.timeEndPeriod(1)
            except Exception:
                pass

        sys.exit(ret)

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        try:
            with open("crash.log", "w", encoding="utf-8") as f:
                f.write(err_msg)
        except Exception:
            pass
        if sys.platform == "win32":
            try:
                ctypes.windll.user32.MessageBoxW(0, f"Terjadi kesalahan saat menjalankan NyangBuddy:\n\n{err_msg}", "NyangBuddy Error", 0x10)
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
