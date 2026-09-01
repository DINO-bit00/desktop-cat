"""
Catch the Fish (Refleks Tangkap Ikan Lompat) - NyangBuddy Arcade Mini-Game (Stage 1).
Players catch jumping pixel fish by steering the desktop cat with mouse / arrow keys
or clicking directly on fish as they leap into the air!
"""

import random
import time
import math
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QKeyEvent, QMouseEvent,
    QPainterPath, QTransform, QPolygonF
)

from src.games.base_game import BaseGameOverlay
from src.settings import save_settings


class FishItem:
    """Represents a jumping fish or junk can item."""
    def __init__(self, x: float, y: float, item_type: str, vx: float, vy: float):
        self.x = x
        self.y = y
        self.item_type = item_type  # 'silver_fish', 'golden_salmon', 'junk_can'
        self.vx = vx
        self.vy = vy
        self.gravity = 820.0  # px / sec^2
        # Larger sizes for high visibility
        if item_type == 'golden_salmon':
            self.size = 60
        elif item_type == 'silver_fish':
            self.size = 54
        else:
            self.size = 46

        self.rotation = 0.0
        self.is_caught = False
        self.is_dead = False
        self.spawn_time = time.time()

    def update(self, dt: float, screen_height: float):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Dynamic rotation following parabolic velocity angle
        self.rotation = math.degrees(math.atan2(self.vy, self.vx))

        # Check if fell off screen
        if self.y > screen_height + 60 and self.vy > 0:
            self.is_dead = True


class FloatingText:
    """Floating score popup (e.g. +10, +50, -10)."""
    def __init__(self, x: float, y: float, text: str, color: QColor):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.opacity = 1.0
        self.lifetime = 1.0  # seconds
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.y -= 42.0 * dt  # float upwards
        self.opacity = max(0.0, 1.0 - (self.age / self.lifetime))

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class Particle:
    """Sparkle and splash particles."""
    def __init__(self, x: float, y: float, color: QColor, vx: float, vy: float, size: float = 5.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.lifetime = random.uniform(0.4, 0.8)
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 180.0 * dt  # mild gravity
        self.size = max(0.5, self.size * (1.0 - dt * 1.4))

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class FishCatchGame(BaseGameOverlay):
    """
    Catch the Fish Arcade Mini-Game Overlay with Tutorial & Enhanced Visuals.
    """
    def __init__(self, pet_window):
        super().__init__(pet_window, title="🎮 CATCH THE FISH")

        # Game states: 'tutorial', 'playing', 'game_over'
        self.game_state = "tutorial"
        self.is_timer_running = False

        self.game_time_limit = 30.0
        self.time_remaining = self.game_time_limit
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.fish_caught_count = 0
        self.salmon_caught_count = 0

        # High Score from settings
        self.high_score = self.pet_window.settings.get("high_score_fish_catch", 0)

        # Game lists
        self.items: List[FishItem] = []
        self.floating_texts: List[FloatingText] = []
        self.particles: List[Particle] = []

        # Cat positioning & steering
        self.cat_target_x = float(self.width() // 2 - self.pet_window.sprite_size // 2)
        self.cat_current_x = self.cat_target_x
        self.cat_y = float(self.height() - self.pet_window.sprite_size - 25)

        # Snap pet window to start position
        self.pet_window.move(int(self.geometry().left() + self.cat_current_x), int(self.geometry().top() + self.cat_y))
        self.pet_window.set_state("idle")
        self.pet_window.raise_()

        # Spawn timing
        self.time_since_spawn = 0.0
        self.spawn_interval = 0.95

        # Key state
        self.key_left_pressed = False
        self.key_right_pressed = False

        # Button rects for modal dialogues
        self.start_btn_rect = QRect()
        self.restart_btn_rect = QRect()
        self.quit_btn_rect = QRect()
        self._start_hover = False
        self._restart_hover = False
        self._quit_hover = False

    def update_game_physics(self, dt: float):
        if self.game_state == "tutorial":
            # Just keep pet positioned, no timer deduction or item spawning
            return

        # Update Cat steering towards target x
        if self.game_state == "playing":
            if self.key_left_pressed:
                self.cat_target_x -= 580.0 * dt
            elif self.key_right_pressed:
                self.cat_target_x += 580.0 * dt

            # Clamp inside screen
            max_x = float(self.width() - self.pet_window.sprite_size - 10)
            self.cat_target_x = max(10.0, min(max_x, self.cat_target_x))

            # Smooth lerp
            dx = self.cat_target_x - self.cat_current_x
            self.cat_current_x += dx * min(1.0, dt * 15.0)

            # Move pet window
            screen_geo = self.geometry()
            target_screen_x = int(screen_geo.left() + self.cat_current_x)
            target_screen_y = int(screen_geo.top() + self.cat_y)
            self.pet_window.move(target_screen_x, target_screen_y)

            # Update cat facing animation
            if abs(dx) > 4.0:
                if dx < 0 and self.pet_window.state != "walk_left":
                    self.pet_window.set_state("walk_left")
                elif dx > 0 and self.pet_window.state != "walk_right":
                    self.pet_window.set_state("walk_right")
            else:
                if self.pet_window.state not in ["idle", "feed", "celebrate", "overheat"]:
                    self.pet_window.set_state("idle")

            # Spawn fish items
            self.time_since_spawn += dt
            if self.time_since_spawn >= self.spawn_interval:
                self.time_since_spawn = 0.0
                self.spawn_interval = random.uniform(0.75, 1.25)
                self._spawn_random_fish()

        # Update fish items
        cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        cat_center_y = self.cat_y + self.pet_window.sprite_size / 2.0
        cat_catch_radius = self.pet_window.sprite_size * 0.52

        for item in self.items:
            item.update(dt, float(self.height()))

            # Automatic collision check with Cat catch zone
            if not item.is_caught and self.game_state == "playing":
                dist = math.hypot(item.x - cat_center_x, item.y - cat_center_y)
                if dist <= (cat_catch_radius + item.size * 0.4):
                    self._catch_item(item)

        # Filter dead items
        self.items = [item for item in self.items if not item.is_dead]

        # Update floating texts
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if not ft.is_dead]

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead]

    def _spawn_random_fish(self):
        """Spawns an item jumping from the bottom in a parabolic curve."""
        spawn_x = random.uniform(self.width() * 0.12, self.width() * 0.88)
        spawn_y = float(self.height() + 25)

        # Decide item type: 60% silver fish, 25% golden salmon, 15% junk can
        rnd = random.random()
        if rnd < 0.60:
            item_type = "silver_fish"
        elif rnd < 0.85:
            item_type = "golden_salmon"
        else:
            item_type = "junk_can"

        # Velocity towards center screen
        target_mid = self.width() / 2.0
        dir_bias = (target_mid - spawn_x) * 0.35
        vx = random.uniform(-140, 140) + dir_bias
        vy = -random.uniform(640, 840)

        self.items.append(FishItem(spawn_x, spawn_y, item_type, vx, vy))

    def _catch_item(self, item: FishItem):
        """Handles successful catching of a fish or junk item."""
        item.is_caught = True
        item.is_dead = True

        if item.item_type == "silver_fish":
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            combo_bonus = min(15, (self.combo - 1) * 3)
            pts = 10 + combo_bonus
            self.score += pts
            self.fish_caught_count += 1

            self._play_sound_blip(freq=1250, dur=40)
            self.pet_window.set_state("feed", duration_seconds=0.7)
            self._create_particles(item.x, item.y, QColor(100, 220, 255), count=12)

            label = f"+{pts} 🐟" if self.combo <= 1 else f"+{pts} 🐟 ({self.combo}x COMBO!)"
            self.floating_texts.append(FloatingText(item.x, item.y - 20, label, QColor(100, 240, 255)))

        elif item.item_type == "golden_salmon":
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            pts = 50 + (self.combo - 1) * 5
            self.score += pts
            self.salmon_caught_count += 1

            self._play_sound_blip(freq=1650, dur=80)
            self.pet_window.set_state("celebrate", duration_seconds=0.8)
            self._create_particles(item.x, item.y, QColor(255, 220, 50), count=22)

            label = f"✨ +{pts} 🍣 GOLDEN SALMON!"
            self.floating_texts.append(FloatingText(item.x, item.y - 25, label, QColor(255, 225, 40)))

        elif item.item_type == "junk_can":
            self.combo = 0
            self.score = max(0, self.score - 10)

            self._play_sound_blip(freq=450, dur=70)
            self.pet_window.set_state("overheat", duration_seconds=0.7)
            self._create_particles(item.x, item.y, QColor(150, 150, 160), count=10)

            self.floating_texts.append(FloatingText(item.x, item.y - 20, "-10 🥫 ZONK!", QColor(255, 90, 90)))

    def _create_particles(self, x: float, y: float, color: QColor, count: int = 14):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(70, 240)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - 70.0
            self.particles.append(Particle(x, y, color, vx, vy, size=random.uniform(4.0, 7.0)))

    def _play_sound_blip(self, freq: int = 1350, dur: int = 40):
        if self.pet_window.settings.get("sound_enabled", False):
            try:
                import winsound
                winsound.Beep(freq, dur)
            except Exception:
                pass

    def start_game_from_tutorial(self):
        """Transitions from tutorial card to active gameplay."""
        self.game_state = "playing"
        self.is_timer_running = True
        self.last_tick_time = time.time()
        self.time_remaining = self.game_time_limit
        self.score = 0
        self.combo = 0
        self.fish_caught_count = 0
        self.salmon_caught_count = 0
        self.items.clear()
        self.floating_texts.clear()
        self.particles.clear()
        self.floating_texts.append(FloatingText(self.width() / 2, self.height() / 2 - 40, "GO! TANGKAP IKAN! 🐟", QColor(255, 230, 80)))
        self.pet_window.set_state("idle")

    def on_game_over(self):
        """Triggered when 30s timer runs out."""
        self.game_state = "game_over"

        # Check High Score
        if self.score > self.high_score:
            self.high_score = self.score
            self.pet_window.settings["high_score_fish_catch"] = self.high_score
            save_settings(self.pet_window.settings)

        # Pet celebration if good score
        if self.score >= 80:
            self.pet_window.set_state("celebrate", duration_seconds=4.0)
            raw_name = self.pet_window.settings.get("user_name", "").strip()
            user_name = f" {raw_name}" if raw_name else ""
            self.pet_window.say(f"Keren banget{user_name}! Kenyang makan ikan nya~ ⭐🍣", 4000)
        else:
            self.pet_window.set_state("idle")
            self.pet_window.say("Permainan selesai nya! Mau main lagi? 🐾🐟", 3500)

    def restart_game(self):
        """Restarts the catch the fish mini-game."""
        self.start_game_from_tutorial()

    def keyPressEvent(self, event: QKeyEvent):
        if self.game_state == "tutorial":
            if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.start_game_from_tutorial()
                event.accept()
                return
        elif self.game_state == "playing":
            if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_A):
                self.key_left_pressed = True
                event.accept()
                return
            elif event.key() in (Qt.Key.Key_Right, Qt.Key.Key_D):
                self.key_right_pressed = True
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Space:
                # Pounce / quick leap catch
                self._attempt_space_catch()
                event.accept()
                return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.key_left_pressed = False
        elif event.key() in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.key_right_pressed = False
        super().keyReleaseEvent(event)

    def _attempt_space_catch(self):
        """Cat pounces up slightly to snatch nearby fish."""
        cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        cat_top_y = self.cat_y + 10

        # Find closest fish within expanded catch range
        for item in self.items:
            if not item.is_caught:
                dist = math.hypot(item.x - cat_center_x, item.y - cat_top_y)
                if dist <= (self.pet_window.sprite_size * 1.0 + item.size * 0.5):
                    self._catch_item(item)
                    break

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        if self.game_state == "tutorial":
            self._start_hover = self.start_btn_rect.contains(pos)
        elif self.game_state == "playing":
            # Mouse steers cat x position smoothly
            self.cat_target_x = float(pos.x() - self.pet_window.sprite_size / 2.0)
        elif self.game_state == "game_over":
            self._restart_hover = self.restart_btn_rect.contains(pos)
            self._quit_hover = self.quit_btn_rect.contains(pos)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        if self.game_state == "tutorial":
            if self.start_btn_rect.contains(pos):
                self.start_game_from_tutorial()
                event.accept()
                return
        elif self.game_state == "game_over":
            if self.restart_btn_rect.contains(pos):
                self.restart_game()
                event.accept()
                return
            elif self.quit_btn_rect.contains(pos):
                self.close_game()
                event.accept()
                return
        elif self.game_state == "playing":
            # Clicking directly on any fish catches it!
            for item in self.items:
                if not item.is_caught:
                    if math.hypot(item.x - pos.x(), item.y - pos.y()) <= item.size * 1.2:
                        self._catch_item(item)
                        event.accept()
                        return

        super().mousePressEvent(event)

    # -------------------------------------------------------------
    # Rendering & Pixel Art Graphics
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 1. Draw Arcade Top HUD
        self.draw_arcade_hud(painter)

        if self.game_state == "tutorial":
            # Draw Tutorial Modal
            self._draw_tutorial_modal(painter)
            return

        # 2. Draw Fish Catch Zone indicator (subtle glowing ripple under cat)
        if self.game_state == "playing":
            cat_cx = self.cat_current_x + self.pet_window.sprite_size / 2.0
            cat_bot_y = self.cat_y + self.pet_window.sprite_size - 10
            painter.setPen(QPen(QColor(80, 220, 255, 110), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(40, 180, 240, 30)))
            painter.drawEllipse(QPoint(int(cat_cx), int(cat_bot_y)), int(self.pet_window.sprite_size * 0.52), 18)

        # 3. Draw Jumping Fish Items
        for item in self.items:
            self._draw_fish_item(painter, item)

        # 4. Draw Particles
        for p in self.particles:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(p.color))
            painter.drawEllipse(QPoint(int(p.x), int(p.y)), int(p.size), int(p.size))

        # 5. Draw Floating Texts
        for ft in self.floating_texts:
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            col = QColor(ft.color)
            col.setAlphaF(ft.opacity)
            painter.setPen(col)
            painter.drawText(int(ft.x - 70), int(ft.y), ft.text)

        # 6. Draw Bottom Controls Hint
        if self.game_state == "playing":
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255, 220))
            hint = "🕹️ Gerakkan Mouse / [A][D]  •  Tekan [Spasi] atau Klik Ikan untuk HAP!  •  [Esc] Keluar"
            painter.drawText(QRect(0, self.height() - 32, self.width(), 22), Qt.AlignmentFlag.AlignCenter, hint)

        # 7. Draw Game Over Modal Card
        if self.game_state == "game_over":
            self._draw_game_over_modal(painter)

    def _draw_tutorial_modal(self, painter: QPainter):
        """Draws clear How to Play tutorial screen before starting."""
        card_w = 540
        card_h = 390
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Glassmorphism Card
        painter.setPen(QPen(QColor(255, 215, 0, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 14, 14)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 225, 70))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "CARA BERMAIN: TANGKAP IKAN")

        # Subtitle
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(180, 200, 230))
        painter.drawText(QRect(card_x, card_y + 48, card_w, 20), Qt.AlignmentFlag.AlignCenter, "Bantu kucingmu menangkap ikan segar sebanyak-banyaknya!")

        # Item rules box
        box_y = card_y + 80
        # Row 1: Silver Fish
        preview_silver = FishItem(card_x + 48, box_y + 20, "silver_fish", 0, 0)
        preview_silver.size = 38
        self._draw_fish_item(painter, preview_silver)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(100, 235, 255))
        painter.drawText(card_x + 82, box_y + 24, "Ikan Sarden")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 195, box_y + 24, "• Poin: +10 PTS  (Ikan normal, berenang lincah)")

        # Row 2: Golden Salmon
        preview_salmon = FishItem(card_x + 48, box_y + 58, "golden_salmon", 0, 0)
        preview_salmon.size = 42
        self._draw_fish_item(painter, preview_salmon)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 215, 40))
        painter.drawText(card_x + 82, box_y + 62, "Salmon Emas")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 195, box_y + 62, "• Poin: +50 PTS  (Langka, berkilau & poin tinggi!)")

        # Row 3: Junk Can
        preview_can = FishItem(card_x + 48, box_y + 96, "junk_can", 0, 0)
        preview_can.size = 32
        self._draw_fish_item(painter, preview_can)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 90, 90))
        painter.drawText(card_x + 82, box_y + 100, "Kaleng Zonk")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 195, box_y + 100, "• Poin: -10 PTS  (Zonk! Hati-hati jangan ditangkap)")

        # Controls Section
        ctrl_y = box_y + 130
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(card_x + 40, ctrl_y, card_x + card_w - 40, ctrl_y)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 235, 120))
        painter.drawText(card_x + 45, ctrl_y + 25, "🎮 KONTROL:")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(220, 230, 245))
        painter.drawText(card_x + 150, ctrl_y + 25, "• Geser Mouse atau tombol [A][D] untuk menggerakkan kucing.")
        painter.drawText(card_x + 150, ctrl_y + 45, "• Tekan [Spasi] atau Klik Langsung pada Ikan untuk menangkap (HAP!).")
        painter.drawText(card_x + 150, ctrl_y + 65, "• Durasi permainan: 30 Detik.")

        # Start Button
        btn_w = 260
        btn_h = 44
        self.start_btn_rect = QRect(card_x + (card_w - btn_w) // 2, card_y + card_h - 62, btn_w, btn_h)

        s_bg = QColor(40, 175, 85, 245) if self._start_hover else QColor(25, 140, 65, 230)
        painter.setPen(QPen(QColor(120, 255, 160), 2))
        painter.setBrush(QBrush(s_bg))
        painter.drawRoundedRect(self.start_btn_rect, 8, 8)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.start_btn_rect, Qt.AlignmentFlag.AlignCenter, "▶ MULAI MAIN (SPASI)")

    def _draw_fish_item(self, painter: QPainter, item: FishItem):
        """Draws high-visibility pixel-styled jumping fish with rotation."""
        try:
            painter.save()
            painter.translate(item.x, item.y)
            painter.rotate(item.rotation)

            s = float(item.size)

            if item.item_type == "silver_fish":
                # 🐟 CUTE CYAN / SILVER SARDINE (High Visibility)
                # Outer Body with thick dark border
                painter.setPen(QPen(QColor(0, 45, 90), 2.5))
                painter.setBrush(QBrush(QColor(0, 195, 255)))
                painter.drawEllipse(QRectF(-s * 0.5, -s * 0.28, s, s * 0.56))

                # White Gleaming Belly
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(240, 252, 255)))
                painter.drawEllipse(QRectF(-s * 0.42, 0.0, s * 0.72, s * 0.24))

                # Dorsal Fin
                dorsal = QPolygonF([QPointF(-s * 0.1, -s * 0.28), QPointF(s * 0.1, -s * 0.44), QPointF(s * 0.2, -s * 0.28)])
                painter.setPen(QPen(QColor(0, 45, 90), 2.0))
                painter.setBrush(QBrush(QColor(0, 150, 225)))
                painter.drawPolygon(dorsal)

                # Tail Fin
                tail = QPolygonF([
                    QPointF(s * 0.42, 0.0),
                    QPointF(s * 0.82, -s * 0.42),
                    QPointF(s * 0.65, 0.0),
                    QPointF(s * 0.82, s * 0.42)
                ])
                painter.drawPolygon(tail)

                # Scale Highlights
                painter.setPen(QPen(QColor(255, 255, 255, 180), 2.0))
                painter.drawArc(QRectF(-s * 0.15, -s * 0.16, 12, 12), 45 * 16, 90 * 16)
                painter.drawArc(QRectF(s * 0.05, -s * 0.16, 12, 12), 45 * 16, 90 * 16)

                # Big Anime Eye
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(10, 20, 35)))
                painter.drawEllipse(QRectF(-s * 0.35, -s * 0.14, 9.0, 9.0))
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawEllipse(QRectF(-s * 0.32, -s * 0.12, 3.5, 3.5))

            elif item.item_type == "golden_salmon":
                # 🍣 RADIANT GOLDEN SALMON (Rich Gold + Salmon Stripes + Sparkles)
                # Golden Aura Glow
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(255, 215, 0, 50)))
                painter.drawEllipse(QRectF(-s * 0.65, -s * 0.40, s * 1.3, s * 0.80))

                # Main Body
                painter.setPen(QPen(QColor(130, 70, 0), 2.8))
                painter.setBrush(QBrush(QColor(255, 185, 0)))
                painter.drawEllipse(QRectF(-s * 0.54, -s * 0.30, s * 1.08, s * 0.60))

                # 3 Vivid Salmon Stripes
                painter.setPen(QPen(QColor(255, 60, 20), 3.0))
                painter.drawLine(QPointF(-s * 0.20, -s * 0.24), QPointF(-s * 0.05, s * 0.24))
                painter.drawLine(QPointF(s * 0.02, -s * 0.24), QPointF(s * 0.17, s * 0.24))
                painter.drawLine(QPointF(s * 0.24, -s * 0.18), QPointF(s * 0.36, s * 0.18))

                # Golden Belly
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(255, 245, 180, 200)))
                painter.drawEllipse(QRectF(-s * 0.45, 0.0, s * 0.75, s * 0.24))

                # Golden Tail Fin
                tail = QPolygonF([
                    QPointF(s * 0.46, 0.0),
                    QPointF(s * 0.88, -s * 0.45),
                    QPointF(s * 0.70, 0.0),
                    QPointF(s * 0.88, s * 0.45)
                ])
                painter.setPen(QPen(QColor(130, 70, 0), 2.5))
                painter.setBrush(QBrush(QColor(255, 150, 0)))
                painter.drawPolygon(tail)

                # Sparkling Star Eye
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(20, 15, 0)))
                painter.drawEllipse(QRectF(-s * 0.38, -s * 0.16, 10.0, 10.0))
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawEllipse(QRectF(-s * 0.35, -s * 0.14, 4.0, 4.0))

            elif item.item_type == "junk_can":
                # 🥫 CRUMPLED METAL TIN CAN
                # Body Cylinder
                painter.setPen(QPen(QColor(35, 40, 50), 2.5))
                painter.setBrush(QBrush(QColor(165, 172, 182)))
                painter.drawRoundedRect(QRectF(-s * 0.38, -s * 0.44, s * 0.76, s * 0.88), 4.0, 4.0)

                # Red Middle Label Band
                painter.setBrush(QBrush(QColor(225, 55, 65)))
                painter.drawRect(QRectF(-s * 0.38, -s * 0.16, s * 0.76, s * 0.32))

                # Bold White X Mark
                painter.setPen(QPen(QColor(255, 255, 255), 2.5))
                painter.drawLine(QPointF(-s * 0.18, -s * 0.10), QPointF(s * 0.18, s * 0.10))
                painter.drawLine(QPointF(-s * 0.18, s * 0.10), QPointF(s * 0.18, -s * 0.10))

                # Metal Rim & Pull Tab
                painter.setPen(QPen(QColor(35, 40, 50), 2.0))
                painter.setBrush(QBrush(QColor(210, 215, 225)))
                painter.drawEllipse(QRectF(-s * 0.18, -s * 0.48, s * 0.36, 6))

            painter.restore()
        except Exception as e:
            try:
                painter.restore()
            except Exception:
                pass

    def _draw_game_over_modal(self, painter: QPainter):
        """Draws retro game over result dialog."""
        card_w = 440
        card_h = 320
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Backdrop Shadow
        painter.setPen(QPen(QColor(255, 215, 0, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 12, 12)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 225, 70))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "🏆 HASIL TANGKAPAN!")

        # Final Score & High Score
        painter.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(QRect(card_x, card_y + 58, card_w, 36), Qt.AlignmentFlag.AlignCenter, f"{self.score} PTS")

        if self.score >= self.high_score and self.score > 0:
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 215, 50))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, "🌟 REKOR BARU TERCAPAI! 🌟")
        else:
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor(180, 190, 210))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, f"Rekor Tertinggi: {self.high_score} PTS")

        # Stats Breakdown
        preview_stat_silver = FishItem(card_x + 65, card_y + 138, "silver_fish", 0, 0)
        preview_stat_silver.size = 28
        self._draw_fish_item(painter, preview_stat_silver)

        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 235, 250))
        painter.drawText(card_x + 90, card_y + 143, "Ikan Sarden:")
        painter.drawText(card_x + 290, card_y + 143, f"{self.fish_caught_count} ekor")

        preview_stat_salmon = FishItem(card_x + 65, card_y + 168, "golden_salmon", 0, 0)
        preview_stat_salmon.size = 32
        self._draw_fish_item(painter, preview_stat_salmon)

        painter.drawText(card_x + 90, card_y + 173, "Salmon Emas:")
        painter.drawText(card_x + 290, card_y + 173, f"{self.salmon_caught_count} ekor")

        painter.drawText(card_x + 65, card_y + 201, "🔥 Combo Tertinggi:")
        painter.drawText(card_x + 290, card_y + 201, f"{self.max_combo}x Combo")

        # Buttons
        btn_w = 145
        btn_h = 40
        self.restart_btn_rect = QRect(card_x + 50, card_y + 242, btn_w, btn_h)
        self.quit_btn_rect = QRect(card_x + 245, card_y + 242, btn_w, btn_h)

        # Restart Button
        r_bg = QColor(40, 175, 85, 245) if self._restart_hover else QColor(25, 140, 65, 230)
        painter.setPen(QPen(QColor(120, 255, 160), 1.5))
        painter.setBrush(QBrush(r_bg))
        painter.drawRoundedRect(self.restart_btn_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.restart_btn_rect, Qt.AlignmentFlag.AlignCenter, "▶ MAIN LAGI")

        # Quit Button
        q_bg = QColor(210, 50, 60, 245) if self._quit_hover else QColor(150, 35, 45, 230)
        painter.setPen(QPen(QColor(255, 130, 130), 1.5))
        painter.setBrush(QBrush(q_bg))
        painter.drawRoundedRect(self.quit_btn_rect, 6, 6)

        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.quit_btn_rect, Qt.AlignmentFlag.AlignCenter, "✕ SELESAI")

