import sys
import random
import math
import time
from typing import List, Optional

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QPixmap

import src.audio as audio


class FallingItem:
    def __init__(self, x: float, y: float, item_type: str, speed: float):
        self.x = x
        self.y = y
        self.item_type = item_type  # "fish", "snack", "star", "clock"
        self.speed = speed
        self.size = 28
        self.rotation = 0.0

    def update(self):
        self.y += self.speed
        self.rotation += 2.5


class MiniBreakGameDialog(QDialog):
    """
    Catch The Fish! — 60-Second Kawaii Mini Break Game (Feature 26).
    Relaxing retro arcade game for Pomodoro break intervals:
    Catch delicious fish & stars, avoid alarm clocks, and earn affection points!
    """
    game_finished = pyqtSignal(int) # emits final score

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎮 Catch The Fish! — Mini Break Game")
        self.setFixedSize(460, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.score = 0
        self.time_left = 60 # 60 seconds
        self.basket_x = 200.0
        self.basket_width = 70
        self.basket_height = 20
        self.items: List[FallingItem] = []

        self.is_game_active = False

        self._init_ui()
        self._setup_timers()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0b1329;
                border: 2px solid #38bdf8;
                border-radius: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        # Game UI Header Overlaid
        self.setMouseTracking(True)

    def _setup_timers(self):
        # 60 FPS Game Loop
        self.game_timer = QTimer(self)
        self.game_timer.setInterval(16)
        self.game_timer.timeout.connect(self._game_tick)

        # 1-Second Countdown Timer
        self.second_timer = QTimer(self)
        self.second_timer.setInterval(1000)
        self.second_timer.timeout.connect(self._on_second_tick)

        # Item Spawner Timer
        self.spawn_timer = QTimer(self)
        self.spawn_timer.setInterval(650)
        self.spawn_timer.timeout.connect(self._spawn_item)

    def start_game(self):
        self.score = 0
        self.time_left = 60
        self.items.clear()
        self.is_game_active = True

        self.game_timer.start()
        self.second_timer.start()
        self.spawn_timer.start()
        audio.play_pop()

    def _on_second_tick(self):
        if not self.is_game_active:
            return
        self.time_left -= 1
        if self.time_left <= 0:
            self._end_game()

    def _spawn_item(self):
        if not self.is_game_active:
            return
        x = random.uniform(30.0, self.width() - 50.0)
        types = ["fish", "fish", "snack", "star", "clock"]
        t = random.choice(types)
        speed = random.uniform(2.8, 5.2)
        self.items.append(FallingItem(x, -20.0, t, speed))

    def _game_tick(self):
        if not self.is_game_active:
            return

        # Update items
        basket_y = self.height() - 45
        basket_rect = QRect(int(self.basket_x - self.basket_width / 2.0), basket_y, self.basket_width, self.basket_height)

        survived = []
        for item in self.items:
            item.update()
            item_rect = QRect(int(item.x), int(item.y), item.size, item.size)

            # Check collision with basket
            if basket_rect.intersects(item_rect):
                if item.item_type == "fish":
                    self.score += 10
                    audio.play_munch()
                elif item.item_type == "snack":
                    self.score += 15
                    audio.play_munch()
                elif item.item_type == "star":
                    self.score += 25
                    audio.play_pop()
                elif item.item_type == "clock":
                    self.score = max(0, self.score - 15)
                    audio.play_sound("blip")
                continue

            if item.y < self.height() + 20:
                survived.append(item)

        self.items = survived
        self.update()

    def _end_game(self):
        self.is_game_active = False
        self.game_timer.stop()
        self.second_timer.stop()
        self.spawn_timer.stop()

        audio.play_celebrate()
        self.game_finished.emit(self.score)
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_game_active:
            self.basket_x = float(event.position().x())
            self.basket_x = max(self.basket_width / 2.0 + 10, min(self.width() - self.basket_width / 2.0 - 10, self.basket_x))
            self.update()
        event.accept()

    def mousePressEvent(self, event):
        if not self.is_game_active:
            # Click to restart game or close
            if self.time_left <= 0:
                self.start_game()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Background gradient
        bg = QColor(11, 19, 41)
        painter.fillRect(self.rect(), bg)

        if not self.is_game_active and self.time_left == 60:
            # Start Screen
            painter.setPen(QColor(96, 165, 250))
            painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            painter.drawText(QRect(0, 140, self.width(), 40), Qt.AlignmentFlag.AlignCenter, "🐟 CATCH THE FISH! 🎮")

            painter.setPen(QColor(226, 232, 240))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(QRect(20, 200, self.width() - 40, 80), Qt.AlignmentFlag.AlignCenter,
                             "Gerakkan kursor untuk menangkap Ikan 🐟 & Bintang ⭐!\nHindari Jam Weker ⏰!")

            painter.setPen(QColor(251, 191, 36))
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(QRect(0, 320, self.width(), 40), Qt.AlignmentFlag.AlignCenter, "▶️ Klik di Sini untuk Mulai!")
            return

        if not self.is_game_active and self.time_left <= 0:
            # Game Over Screen
            painter.setPen(QColor(245, 158, 11))
            painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            painter.drawText(QRect(0, 130, self.width(), 40), Qt.AlignmentFlag.AlignCenter, "🎉 WAKTU HABIS! 🎉")

            painter.setPen(QColor(244, 114, 182))
            painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            painter.drawText(QRect(0, 185, self.width(), 35), Qt.AlignmentFlag.AlignCenter, f"Skor Akhir: {self.score} Poin")

            painter.setPen(QColor(226, 232, 240))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(QRect(20, 240, self.width() - 40, 60), Qt.AlignmentFlag.AlignCenter,
                             "Kerja hebat! Kucingmu senang sekali diajak main nya~ 🐾💖\n(+10 Poin Kasih Sayang didapatkan!)")

            painter.setPen(QColor(96, 165, 250))
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            painter.drawText(QRect(0, 340, self.width(), 40), Qt.AlignmentFlag.AlignCenter, "🔄 Klik untuk Main Lagi")
            return

        # Top HUD Banner
        painter.setPen(QColor(241, 245, 249))
        painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        painter.drawText(20, 35, f"Skor: {self.score}")
        painter.drawText(self.width() - 120, 35, f"Waktu: {self.time_left}s")

        # Falling Items
        for item in self.items:
            ix, iy = int(item.x), int(item.y)
            if item.item_type == "fish":
                # Golden Fish
                painter.setBrush(QBrush(QColor(255, 180, 40)))
                painter.setPen(QColor(20, 20, 25))
                painter.drawEllipse(ix, iy, 24, 14)
                painter.drawPolygon([QPoint(ix + 20, iy + 7), QPoint(ix + 28, iy + 2), QPoint(ix + 28, iy + 12)])
            elif item.item_type == "snack":
                # Chicken treat
                painter.setBrush(QBrush(QColor(251, 146, 60)))
                painter.setPen(QColor(20, 20, 25))
                painter.drawRoundedRect(ix, iy, 18, 18, 5, 5)
            elif item.item_type == "star":
                # Sparkle Star
                painter.setBrush(QBrush(QColor(250, 204, 21)))
                painter.setPen(QColor(20, 20, 25))
                painter.drawEllipse(ix, iy, 16, 16)
            elif item.item_type == "clock":
                # Alarm Clock
                painter.setBrush(QBrush(QColor(239, 68, 68)))
                painter.setPen(QColor(20, 20, 25))
                painter.drawEllipse(ix, iy, 20, 20)

        # Player Cat Bowl / Basket
        bx = int(self.basket_x - self.basket_width / 2.0)
        by = self.height() - 45
        painter.setBrush(QBrush(QColor(56, 189, 248)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawRoundedRect(bx, by, self.basket_width, self.basket_height, 10, 10)

        # Cute paw decor on basket
        painter.setPen(QColor(15, 23, 42))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRect(bx, by, self.basket_width, self.basket_height), Qt.AlignmentFlag.AlignCenter, "🐾 MANGKUK")
