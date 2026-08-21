"""
Sticky Note Widget
A persistent floating yellow note that displays a user's target/focus.
"""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import QWidget


class StickyNote(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # UI State
        self._text = ""
        self.setFixedSize(140, 50)
        
        # The note hides when speech bubble is active, handled by pet_window
        self._temporarily_hidden = False

    def start(self, text: str):
        """Show the sticky note with text."""
        self._text = text
        # Adjust height based on text length (simple wrap estimate)
        if len(text) > 15:
            self.setFixedSize(150, 60)
        else:
            self.setFixedSize(140, 50)
            
        if not self._temporarily_hidden:
            self.show()
        self.update()

    def stop(self):
        """Hide the sticky note permanently until restarted."""
        self._text = ""
        self.hide()

    def temp_hide(self):
        """Temporarily hide the note (e.g., when speech bubble shows)."""
        self._temporarily_hidden = True
        self.hide()

    def temp_show(self):
        """Restore visibility if there's an active text."""
        self._temporarily_hidden = False
        if self._text:
            self.show()

    def update_position_relative_to(self, pet_pos: QPoint, pet_size: int):
        """
        Positions the sticky note at the top-left of the cat.
        (Pomodoro badge is at top-right).
        """
        if not self.isVisible() and not self._text:
            return

        # Position: Left side, slightly above middle
        x = pet_pos.x() - self.width() + 20
        y = pet_pos.y() + 10
        
        # Ensure it doesn't go off-screen (left bound)
        if x < 0:
            x = pet_pos.x() + pet_size - 20 # Move to right if cramped
            
        self.move(x, y)

    def paintEvent(self, event):
        if not self._text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Draw yellow pastel background
        bg_color = QColor(254, 240, 138, 235) # #fef08a pastel yellow
        border_color = QColor(202, 138, 4, 180) # Darker yellow border
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(4, 4, w - 8, h - 8, 4, 4)

        # Draw a little "tape" or "pin" at the top center
        tape_color = QColor(255, 255, 255, 180)
        painter.setBrush(QBrush(tape_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(w // 2 - 15, 0, 30, 8)

        # Draw Text
        painter.setPen(QPen(QColor(60, 40, 20))) # Dark brown text
        font = QFont("Courier New", 9, QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        painter.setFont(font)

        # Draw text centered, allow wrapping
        text_rect = self.rect().adjusted(10, 10, -10, -5)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.TextWordWrap,
            self._text
        )

