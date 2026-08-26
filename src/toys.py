import sys
import math
import time
import random
from typing import Optional

from PIL import Image, ImageDraw
from PyQt6.QtWidgets import QWidget, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QPixmap, QImage, QColor, QPen, QBrush, QCursor, QTransform

import src.audio as audio


def render_yarn_ball_image(size: int = 40, color_name: str = "pink") -> Image.Image:
    """Render crisp pixel art yarn ball with wound wool thread pattern."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if color_name == "pink":
        MAIN = (255, 110, 150, 255)
        SHADE = (215, 65, 110, 255)
        LIGHT = (255, 185, 210, 255)
    elif color_name == "blue":
        MAIN = (80, 170, 255, 255)
        SHADE = (45, 120, 210, 255)
        LIGHT = (160, 215, 255, 255)
    else:  # mint
        MAIN = (80, 220, 160, 255)
        SHADE = (45, 170, 115, 255)
        LIGHT = (165, 245, 210, 255)

    K = (25, 25, 30, 255)

    cx, cy, r = size // 2, size // 2, (size // 2) - 4
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAIN, outline=K, width=2)

    # Shading crescent
    d.arc([cx - r, cy - r, cx + r, cy + r], start=30, end=150, fill=SHADE, width=3)
    # Highlight crescent
    d.arc([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], start=210, end=330, fill=LIGHT, width=2)

    # Wound thread arcs
    d.arc([cx - 10, cy - 8, cx + 8, cy + 10], start=45, end=225, fill=SHADE, width=2)
    d.arc([cx - 8, cy - 10, cx + 10, cy + 8], start=180, end=360, fill=LIGHT, width=2)
    d.line([(cx - 7, cy + 3), (cx + 7, cy - 3)], fill=SHADE, width=2)
    d.line([(cx - 3, cy - 7), (cx + 3, cy + 7)], fill=LIGHT, width=2)

    # Loose curled thread strand
    d.line([(cx + r, cy + 4), (cx + r + 3, cy + 6), (cx + r + 1, cy + 10), (cx + r + 4, cy + 12)], fill=MAIN, width=2)
    d.point((cx + r + 4, cy + 12), fill=LIGHT)

    return img


class YarnBallWidget(QWidget):
    """
    Interactive Floating Yarn Ball Toy:
    - Bounces and rolls across the desktop with realistic 60 FPS gravity and friction physics.
    - Can be dragged and flicked/thrown with mouse velocity!
    - Cat chases, pounces, and bats at the yarn ball when nearby.
    """
    ball_moved = pyqtSignal(float, float, float, float) # x, y, vel_x, vel_y

    def __init__(self, color_name="pink", initial_pos=(300, 300), parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.ball_size = 44

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.ball_size, self.ball_size)

        # Physics state
        self.pos_x = float(initial_pos[0])
        self.pos_y = float(initial_pos[1])
        self.vel_x = random.uniform(-4.0, 4.0)
        self.vel_y = -3.0
        self.rotation_angle = 0.0

        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.last_mouse_pos = QPoint()
        self.last_mouse_time = time.time()

        # Cache pixmap
        pil_img = render_yarn_ball_image(self.ball_size, self.color_name)
        raw_bytes = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        self.pixmap = QPixmap.fromImage(qimg)

        # Move to initial position
        self.move(int(self.pos_x), int(self.pos_y))

        # 60 FPS Physics Timer
        self.physics_timer = QTimer(self)
        self.physics_timer.setInterval(16)
        self.physics_timer.timeout.connect(self._update_physics)
        self.physics_timer.start()

    def _get_screen_bounds(self):
        screen = QApplication.primaryScreen()
        if screen:
            return screen.geometry()
        return QRect(0, 0, 1920, 1080)

    def _update_physics(self):
        if self.is_dragging:
            return

        screen = self._get_screen_bounds()
        floor_y = screen.bottom() - self.ball_size - 10
        left_x = screen.left() + 5
        right_x = screen.right() - self.ball_size - 5
        ceiling_y = screen.top() + 5

        # Apply gravity
        self.vel_y += 0.38

        # Update position
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        # Roll rotation proportional to horizontal speed
        self.rotation_angle += self.vel_x * 4.5

        # Floor bounce & friction
        if self.pos_y >= floor_y:
            self.pos_y = float(floor_y)
            if abs(self.vel_y) > 0.8:
                self.vel_y = -self.vel_y * 0.62 # elastic bounce
            else:
                self.vel_y = 0.0 # resting on floor

            # Ground friction
            self.vel_x *= 0.965
            if abs(self.vel_x) < 0.05:
                self.vel_x = 0.0

        # Ceiling bounce
        if self.pos_y < ceiling_y:
            self.pos_y = float(ceiling_y)
            self.vel_y = abs(self.vel_y) * 0.7

        # Wall bounces
        if self.pos_x < left_x:
            self.pos_x = float(left_x)
            self.vel_x = abs(self.vel_x) * 0.75
        elif self.pos_x > right_x:
            self.pos_x = float(right_x)
            self.vel_x = -abs(self.vel_x) * 0.75

        self.move(int(self.pos_x), int(self.pos_y))
        self.update()
        self.ball_moved.emit(self.pos_x, self.pos_y, self.vel_x, self.vel_y)

    def bat_away(self, from_x: float, from_y: float):
        """Cat bats / swats the yarn ball with paws!"""
        dx = (self.pos_x + self.ball_size / 2.0) - from_x
        dy = (self.pos_y + self.ball_size / 2.0) - from_y
        dist = math.hypot(dx, dy) or 1.0

        power = random.uniform(7.0, 12.0)
        self.vel_x = (dx / dist) * power + random.uniform(-2.0, 2.0)
        self.vel_y = -random.uniform(4.0, 8.0)
        audio.play_pop()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.last_mouse_pos = event.globalPosition().toPoint()
            self.last_mouse_time = time.time()
            self.vel_x = 0.0
            self.vel_y = 0.0
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            cur_pos = event.globalPosition().toPoint()
            now = time.time()
            dt = max(0.001, now - self.last_mouse_time)

            # Calculate throw velocity
            vx = (cur_pos.x() - self.last_mouse_pos.x()) / dt / 50.0
            vy = (cur_pos.y() - self.last_mouse_pos.y()) / dt / 50.0

            # Smooth velocity filter
            self.vel_x = self.vel_x * 0.4 + vx * 0.6
            self.vel_y = self.vel_y * 0.4 + vy * 0.6

            self.last_mouse_pos = cur_pos
            self.last_mouse_time = now

            new_pt = cur_pos - self.drag_start_pos
            self.pos_x = float(new_pt.x())
            self.pos_y = float(new_pt.y())
            self.move(new_pt)
            self.update()
            self.ball_moved.emit(self.pos_x, self.pos_y, self.vel_x, self.vel_y)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # Cap maximum throw speed
            speed = math.hypot(self.vel_x, self.vel_y)
            if speed > 22.0:
                scale = 22.0 / speed
                self.vel_x *= scale
                self.vel_y *= scale
            event.accept()

    def mouseDoubleClickEvent(self, event):
        # Double click to give a playful bounce
        self.vel_y = -9.0
        self.vel_x = random.choice([-6.0, 6.0])
        audio.play_pop()
        event.accept()

    def _show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e2430;
                color: #e2e8f0;
                border: 2px solid #5865f2;
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #5865f2;
                color: #ffffff;
            }
        """)
        menu.addAction("💖 Ganti Warna: Merah Muda (Pink)", lambda: self.set_color("pink"))
        menu.addAction("💙 Ganti Warna: Biru Langit (Blue)", lambda: self.set_color("blue"))
        menu.addAction("💚 Ganti Warna: Hijau Mint (Mint)", lambda: self.set_color("mint"))
        menu.addSeparator()
        menu.addAction("❌ Simpan Mainan (Tutup)", self.close)
        menu.exec(global_pos)

    def set_color(self, color_name: str):
        self.color_name = color_name
        pil_img = render_yarn_ball_image(self.ball_size, self.color_name)
        raw_bytes = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        self.pixmap = QPixmap.fromImage(qimg)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        # Rotate around center
        cx, cy = self.ball_size / 2.0, self.ball_size / 2.0
        painter.translate(cx, cy)
        painter.rotate(self.rotation_angle % 360.0)
        painter.translate(-cx, -cy)

        painter.drawPixmap(0, 0, self.pixmap)


def make_win32_clickthrough(widget):
    """Enforce native Win32 click-through so mouse events pass 100% through to background apps."""
    if sys.platform == "win32" and widget:
        try:
            import ctypes
            hwnd = int(widget.winId())
            GWL_EXSTYLE = -20
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_LAYERED = 0x00080000
            cur = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur | WS_EX_TRANSPARENT | WS_EX_LAYERED)
        except Exception:
            pass


class LaserPointerOverlay(QWidget):
    """
    Interactive Laser Pointer Dot (Small 40x40 Floating Click-Through Widget):
    - Renders a glowing red dot at the mouse cursor.
    - 100% click-through to underlying Windows apps (WS_EX_TRANSPARENT).
    - Emits laser_position_changed(x, y) for the cat to track and pounce.
    """
    laser_position_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFixedSize(40, 40)

        self.laser_x = -100
        self.laser_y = -100
        self.pulse = 0.0

        # Laser tracking timer
        self.track_timer = QTimer(self)
        self.track_timer.setInterval(16)
        self.track_timer.timeout.connect(self._track_cursor)

    def start_laser(self):
        self.show()
        make_win32_clickthrough(self)
        self._track_cursor()
        self.track_timer.start()

    def stop_laser(self):
        self.track_timer.stop()
        self.hide()

    def _track_cursor(self):
        pos = QCursor.pos()
        self.laser_x = pos.x()
        self.laser_y = pos.y()
        self.move(self.laser_x - 20, self.laser_y - 20)
        self.pulse = (self.pulse + 0.15) % (2.0 * math.pi)
        self.update()
        self.laser_position_changed.emit(self.laser_x, self.laser_y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        cx, cy = 20, 20

        # Outer glowing halo
        halo_radius = 8 + int(math.sin(self.pulse) * 3)
        glow_color = QColor(255, 30, 30, 80)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(cx, cy), halo_radius, halo_radius)

        # Inner bright core
        core_color = QColor(255, 70, 70, 220)
        painter.setBrush(QBrush(core_color))
        painter.drawEllipse(QPoint(cx, cy), 4, 4)

        # Center laser pinpoint
        painter.setBrush(QBrush(QColor(255, 240, 240, 255)))
        painter.drawEllipse(QPoint(cx, cy), 2, 2)
