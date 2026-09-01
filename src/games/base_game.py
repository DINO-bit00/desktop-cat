"""
Base Transparent Overlay Framework for NyangBuddy Arcade Mini-Games.
Provides unified 60 FPS game loop, retro arcade HUD, input management,
and smooth lifecycle coordination with the DesktopPet instance.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QKeyEvent, QMouseEvent, QCursor
import time
import math


class BaseGameOverlay(QWidget):
    """
    Full-screen transparent overlay for desktop arcade mini-games.
    """
    def __init__(self, pet_window, title: str = "ARCADE MINI-GAME"):
        super().__init__()
        self.pet_window = pet_window
        self.game_title = title
        self.is_running = True
        self.game_time_limit = 30.0  # seconds
        self.time_remaining = self.game_time_limit
        self.score = 0
        self.is_game_over = False

        # Save previous pet state to restore on exit
        self._prev_wander_mode = self.pet_window.settings.get("wander_mode", True)
        self._prev_pet_state = self.pet_window.state
        self.pet_window.settings["wander_mode"] = False
        self.pet_window._active_reminder_type = "arcade_game"

        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        # Match screen geometry of current pet window
        screen_geo = self.pet_window._get_current_screen_geometry()
        self.setGeometry(screen_geo)

        # Close button rect (top right)
        self.close_btn_rect = QRect(self.width() - 110, 20, 90, 32)
        self._close_hover = False

        # Game update loop (60 FPS)
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._base_tick)
        self.game_timer.start(16)
        self.last_tick_time = time.time()

    def _base_tick(self):
        if not self.is_running:
            return

        now = time.time()
        dt = max(0.001, min(0.1, now - self.last_tick_time))
        self.last_tick_time = now

        if not self.is_game_over:
            self.time_remaining -= dt
            if self.time_remaining <= 0.0:
                self.time_remaining = 0.0
                self._trigger_game_over()

        self.update_game_physics(dt)
        self.update()

    def update_game_physics(self, dt: float):
        """Override in subclasses to update game state."""
        pass

    def _trigger_game_over(self):
        self.is_game_over = True
        self.on_game_over()

    def on_game_over(self):
        """Override in subclasses for game over handling."""
        pass

    def close_game(self):
        """Cleanly terminates mini-game and restores normal pet roaming & state."""
        self.is_running = False
        self.game_timer.stop()
        self.pet_window.settings["wander_mode"] = self._prev_wander_mode
        self.pet_window._active_reminder_type = None
        self.pet_window.resume_default_state()
        self.close()
        self.deleteLater()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close_game()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        self._close_hover = self.close_btn_rect.contains(pos)
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self.close_btn_rect.contains(pos):
                self.close_game()
                event.accept()
                return
        super().mousePressEvent(event)

    def draw_arcade_hud(self, painter: QPainter):
        """Draws retro 8-bit arcade top bar with score, timer, and close button."""
        # Top HUD Banner Background
        hud_w = 480
        hud_h = 44
        hud_x = (self.width() - hud_w) // 2
        hud_y = 16

        painter.setPen(QPen(QColor(255, 215, 0, 220), 2))
        painter.setBrush(QBrush(QColor(18, 18, 28, 220)))
        painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 8, 8)

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 235, 120))
        painter.drawText(hud_x + 16, hud_y + 27, self.game_title)

        # Score
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(100, 240, 255))
        painter.drawText(hud_x + 230, hud_y + 28, f"PTS: {self.score}")

        # Timer
        time_col = QColor(255, 100, 100) if self.time_remaining <= 5.0 else QColor(120, 255, 140)
        painter.setPen(time_col)
        painter.drawText(hud_x + 370, hud_y + 28, f"⏱️ {int(self.time_remaining):02d}s")

        # Close Button
        btn_bg = QColor(220, 50, 60, 230) if self._close_hover else QColor(30, 30, 42, 200)
        btn_border = QColor(255, 120, 120) if self._close_hover else QColor(180, 180, 200, 160)
        painter.setPen(QPen(btn_border, 1.5))
        painter.setBrush(QBrush(btn_bg))
        painter.drawRoundedRect(self.close_btn_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.close_btn_rect, Qt.AlignmentFlag.AlignCenter, "✕ KELUAR")
