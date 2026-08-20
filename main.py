"""
NyangBuddy - 100% Local, Private & Safe Desktop Companion
Inspired by cozy virtual pets (like Comnyang) but built from scratch with zero telemetry,
open-source Python code, and local-only interactions.
"""

import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.settings import load_settings
from src.pet_window import DesktopPet
from src.tray import CatTrayIcon


def main():
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


if __name__ == "__main__":
    main()
