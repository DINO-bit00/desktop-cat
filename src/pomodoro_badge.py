"""
Floating Pixel Pomodoro Mini UI Badge
A small retro pixel-art styled countdown overlay that hovers near the cat
during active Pomodoro sessions. Shows mode, countdown timer, and progress bar.
"""

import sys
import ctypes
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import QWidget


def _set_badge_topmost(widget):
    """Enforce topmost z-order on Windows OS using native Win32 API."""
    if sys.platform == "win32" and widget:
        try:
            hwnd = int(widget.winId())
            HWND_TOPMOST = -1
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            flags = SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, flags)
        except Exception:
            pass


# ── Visual Theme Constants ──────────────────────────────────────

# Work mode: Warm tomato red
_WORK_BG = QColor(185, 52, 42, 235)
_WORK_BG_DARK = QColor(145, 38, 30, 255)
_WORK_BORDER = QColor(95, 25, 18, 220)
_WORK_PROGRESS = QColor(255, 210, 85, 255)
_WORK_PROGRESS_BG = QColor(120, 35, 25, 180)
_WORK_TEXT = QColor(255, 255, 255, 255)
_WORK_LABEL = "🍅 FOKUS"

# Break mode: Soft teal cyan
_BREAK_BG = QColor(38, 165, 155, 235)
_BREAK_BG_DARK = QColor(28, 128, 120, 255)
_BREAK_BORDER = QColor(18, 85, 78, 220)
_BREAK_PROGRESS = QColor(180, 255, 230, 255)
_BREAK_PROGRESS_BG = QColor(22, 105, 98, 180)
_BREAK_TEXT = QColor(255, 255, 255, 255)
_BREAK_LABEL = "☕ BREAK"

# Badge dimensions
_BADGE_W = 128
_BADGE_H = 42
_PROGRESS_H = 5
_CORNER_R = 8.0


class PomodoroBadge(QWidget):
    """
    Floating pixel-art Pomodoro countdown badge.
    Shows mode label, MM:SS countdown, and a depleting progress bar.
    Follows the cat's position and auto-shows/hides with Pomodoro sessions.
    """

    clicked = pyqtSignal()  # Emitted when user clicks the badge to stop

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(_BADGE_W, _BADGE_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Klik untuk menghentikan Pomodoro")

        # State
        self._mode = "work"       # "work" or "break"
        self._total_seconds = 0
        self._remaining = 0
        self._progress = 1.0      # 1.0 = full, 0.0 = empty
        self._cycle_label = ""    # e.g. "[2/4]" for multi-cycle

        self.hide()

    # ── Public API ──────────────────────────────────────────────

    def start(self, mode: str, total_seconds: int, cycle_label: str = ""):
        """Show the badge and start tracking a Pomodoro session."""
        self._mode = mode
        self._total_seconds = max(1, total_seconds)
        self._remaining = total_seconds
        self._progress = 1.0
        self._cycle_label = cycle_label

        # Widen badge if showing cycle info
        badge_w = _BADGE_W + 42 if cycle_label else _BADGE_W
        self.setFixedSize(badge_w, _BADGE_H)

        self.show()
        _set_badge_topmost(self)
        self.update()

    def update_tick(self, remaining_seconds: int):
        """Called every second to update the countdown and progress bar."""
        self._remaining = max(0, remaining_seconds)
        if self._total_seconds > 0:
            self._progress = self._remaining / self._total_seconds
        else:
            self._progress = 0.0
        self.update()

    def stop(self):
        """Hide the badge when Pomodoro session ends."""
        self._remaining = 0
        self._progress = 0.0
        self.hide()

    def update_position_relative_to(self, pet_pos, pet_size: int = 128):
        """Position the badge at the top-right of the cat sprite."""
        # Offset to top-right so it doesn't collide with speech bubble (centered above)
        target_x = pet_pos.x() + pet_size - 16
        target_y = pet_pos.y() - self.height() + 10

        # Prevent going above screen top
        if target_y < 4:
            target_y = pet_pos.y() + 4

        # Prevent going off right edge of screen
        screen = None
        try:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
        except Exception:
            pass
        if screen:
            screen_right = screen.availableGeometry().right()
            if target_x + self.width() > screen_right:
                # Flip to top-left of cat
                target_x = pet_pos.x() - self.width() + 16

        self.move(target_x, target_y)

    # ── Rendering ───────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # Pick theme colors based on mode
        if self._mode == "work":
            bg, bg_dark = _WORK_BG, _WORK_BG_DARK
            border_c = _WORK_BORDER
            prog_c, prog_bg = _WORK_PROGRESS, _WORK_PROGRESS_BG
            text_c = _WORK_TEXT
            label = _WORK_LABEL
        else:
            bg, bg_dark = _BREAK_BG, _BREAK_BG_DARK
            border_c = _BREAK_BORDER
            prog_c, prog_bg = _BREAK_PROGRESS, _BREAK_PROGRESS_BG
            text_c = _BREAK_TEXT
            label = _BREAK_LABEL

        # ── 1. Background rounded rect with subtle gradient feel ──
        body_rect = QRectF(1.5, 1.5, w - 3, h - 3)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(body_rect, _CORNER_R, _CORNER_R)

        # Darker bottom half for depth
        bottom_rect = QRectF(1.5, h / 2, w - 3, h / 2 - 1.5)
        p.setBrush(QBrush(bg_dark))
        p.setClipRect(bottom_rect)
        p.drawRoundedRect(body_rect, _CORNER_R, _CORNER_R)
        p.setClipping(False)

        # ── 2. Border outline ──
        border_pen = QPen(border_c, 2.0)
        p.setPen(border_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(body_rect, _CORNER_R, _CORNER_R)

        # ── 3. Mode label + countdown text + cycle label ──
        mins = self._remaining // 60
        secs = self._remaining % 60
        cycle_str = f" {self._cycle_label}" if self._cycle_label else ""
        display_text = f"{label} {mins:02d}:{secs:02d}{cycle_str}"

        font = QFont("Consolas", 9, QFont.Weight.Bold)
        font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
        p.setFont(font)
        p.setPen(text_c)

        text_rect = QRectF(6, 2, w - 12, h - _PROGRESS_H - 8)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, display_text)

        # ── 4. Progress bar (bottom of badge) ──
        bar_margin = 8.0
        bar_y = h - _PROGRESS_H - 6
        bar_w = w - bar_margin * 2
        bar_x = bar_margin

        # Progress background track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(prog_bg))
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, _PROGRESS_H), 2.0, 2.0)

        # Progress fill
        fill_w = bar_w * self._progress
        if fill_w > 0:
            p.setBrush(QBrush(prog_c))
            p.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, _PROGRESS_H), 2.0, 2.0)

        p.end()

    # ── Interaction ─────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def enterEvent(self, event):
        """Subtle hover opacity feedback."""
        self.setWindowOpacity(0.85)

    def leaveEvent(self, event):
        self.setWindowOpacity(1.0)
