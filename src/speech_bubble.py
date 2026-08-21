"""
Speech Bubble Widget for Desktop Pet
Displays charming retro/modern dialogue bubbles above the cat with auto-dismissal.
"""

import sys
import ctypes
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


def set_win32_topmost(widget):
    """Enforce topmost z-order on Windows OS using native Win32 API + extended styles."""
    if sys.platform == "win32" and widget:
        try:
            hwnd = int(widget.winId())
            HWND_TOPMOST = -1
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            flags = SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW

            GWL_EXSTYLE = -20
            WS_EX_TOPMOST = 0x00000008
            cur_ex = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if not (cur_ex & WS_EX_TOPMOST):
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur_ex | WS_EX_TOPMOST)

            ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, flags)
        except Exception:
            pass


class SpeechBubble(QWidget):
    bubble_hidden = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Bubble content
        self.message = ""
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_bubble)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 18)

        self.label = QLabel("", self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Style the text
        font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #2c3e50; background: transparent;")
        self.layout.addWidget(self.label)

        self.setMinimumWidth(120)
        self.setMaximumWidth(260)
        self.hide()

    def show_message(self, text, duration_ms=4500):
        self.message = text
        self.label.setText(text)
        self.adjustSize()
        self.show()
        set_win32_topmost(self)
        if duration_ms > 0:
            self.timer.start(duration_ms)

    def hide_bubble(self):
        self.bubble_hidden.emit()
        self.timer.stop()
        self.hide()

    def update_position_relative_to(self, pet_pos: QPoint, pet_size: int = 128):
        # Position the bubble centered right above the cat
        bubble_w = self.width()
        bubble_h = self.height()

        target_x = pet_pos.x() + (pet_size // 2) - (bubble_w // 2)
        target_y = pet_pos.y() - bubble_h + 8

        # Prevent bubble from going above top of screen
        if target_y < 10:
            target_y = pet_pos.y() + pet_size - 10

        self.move(target_x, target_y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        tail_h = 10.0
        rect_h = h - tail_h
        radius = 12.0

        # Path for rounded bubble with pointing tail at the bottom
        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, w - 4, rect_h - 2), radius, radius)

        # Tail pointing down
        tail_center_x = w / 2
        tail_path = QPainterPath()
        tail_path.moveTo(tail_center_x - 7, rect_h - 1)
        tail_path.lineTo(tail_center_x, h - 2)
        tail_path.lineTo(tail_center_x + 7, rect_h - 1)
        tail_path.closeSubpath()

        combined_path = path.united(tail_path)

        # Background fill (Warm creamy soft white)
        painter.fillPath(combined_path, QColor(255, 253, 245, 245))

        # Border outline (Soft cute slate)
        pen = QPen(QColor(60, 64, 80, 200), 2.0)
        painter.strokePath(combined_path, pen)

    def mousePressEvent(self, event):
        # Click bubble to dismiss immediately
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide_bubble()
