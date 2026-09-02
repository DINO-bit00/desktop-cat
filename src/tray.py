"""
System Tray Manager
Creates a Windows taskbar tray icon for quick control and status monitoring.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from src.sprites import PALETTES, render_cat_frame


class CatTrayIcon(QSystemTrayIcon):
    def __init__(self, pet_window, parent=None):
        super().__init__(parent)
        self.pet_window = pet_window
        self.setToolTip("NyangBuddy - Desktop Cat Companion")

        # Generate Tray Icon
        self._update_icon()

        # Context Menu
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 4px;
            }
            QMenu::item {
                padding: 5px 18px;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """)

        show_act = self.menu.addAction("🐾 Tampilkan Kucing")
        show_act.triggered.connect(self._show_pet)

        pom_act = self.menu.addAction("⏱️ Mulai Pomodoro (25m)")
        pom_act.triggered.connect(lambda: self.pet_window.pomodoro.start_focus(25))

        from src.autostart import is_startup_enabled
        startup_act = self.menu.addAction("🚀 Jalankan saat Startup")
        startup_act.setCheckable(True)
        startup_act.setChecked(is_startup_enabled())
        startup_act.triggered.connect(self.pet_window._toggle_startup)

        toxic_act = self.menu.addAction("🛡️ Anti-Toxic Guardian")
        toxic_act.setCheckable(True)
        toxic_act.setChecked(self.pet_window.settings.get("toxic_guardian_enabled", True))
        toxic_act.triggered.connect(self.pet_window._toggle_toxic_guardian)

        arcade_menu = self.menu.addMenu("🎮 Mini-Games Arcade")
        fish_act = arcade_menu.addAction("🐟 Tangkap Ikan (Catch the Fish)")
        fish_act.triggered.connect(self.pet_window.start_fish_catch_game)
        yarn_act = arcade_menu.addAction("🧶 Bola Benang (Cat Yarn Bounce)")
        yarn_act.triggered.connect(self.pet_window.start_yarn_bounce_game)

        self.menu.addSeparator()

        quit_act = self.menu.addAction("❌ Keluar")
        quit_act.triggered.connect(self.pet_window.close_app)

        self.setContextMenu(self.menu)
        self.activated.connect(self._on_tray_activated)
        self.show()

    def _update_icon(self):
        pil_img = render_cat_frame(self.pet_window.skin, "idle", 0)
        from PyQt6.QtGui import QImage
        raw_bytes = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        self.setIcon(QIcon(pixmap))

    def _show_pet(self):
        self.pet_window.show()
        self.pet_window.raise_()
        self.pet_window.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_pet()
