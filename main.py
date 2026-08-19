"""
NyangBuddy - 100% Local, Private & Safe Desktop Companion
Inspired by cozy virtual pets (like Comnyang) but built from scratch with zero telemetry,
open-source Python code, and local-only interactions.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.settings import load_settings
from src.pet_window import DesktopPet
from src.tray import CatTrayIcon


def main():
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

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
