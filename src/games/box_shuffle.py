"""
Box Shuffle (Tebak Kardus Snack Kucing) - NyangBuddy Arcade Mini-Game (Stage 3).
A brain & visual tracking puzzle game! A golden salmon treat is hidden inside 1 of 3 cute cardboard boxes.
The boxes shuffle and swap positions across the table. Guess the correct box to score points and build streaks!
"""

import random
import time
import math
from typing import List, Dict, Any, Optional, Tuple

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QKeyEvent, QMouseEvent,
    QPainterPath, QTransform, QPolygonF
)

from src.games.base_game import BaseGameOverlay
from src.settings import save_settings


class BoxParticle:
    """Confetti or dust particle on box reveal."""
    def __init__(self, x: float, y: float, color: QColor, vx: float, vy: float, size: float = 5.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.lifetime = random.uniform(0.4, 0.75)
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 180.0 * dt  # gravity
        self.size = max(0.5, self.size * (1.0 - dt * 1.5))

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class FloatingText:
    """Floating score and reaction text."""
    def __init__(self, x: float, y: float, text: str, color: QColor):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.opacity = 1.0
        self.lifetime = 1.1
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.y -= 35.0 * dt
        self.opacity = max(0.0, 1.0 - (self.age / self.lifetime))

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class CardboardBox:
    """Interactive cardboard box that can lift open and slide during shuffle."""
    def __init__(self, box_id: int, pos_idx: int, x: float, y: float):
        self.box_id = box_id      # 0, 1, 2
        self.pos_idx = pos_idx    # slot 0 (left), slot 1 (middle), slot 2 (right)
        self.x = x
        self.y = y
        self.origin_x = x
        self.target_x = x
        self.origin_y = y
        self.target_y = y
        self.has_snack = False
        self.lift_y = 0.0         # 0.0 = closed, up to 60.0 = lifted up to reveal snack
        self.target_lift_y = 0.0
        self.width = 130.0
        self.height = 105.0
        self.is_hovered = False

    def update(self, dt: float):
        # Smooth interpolation for position
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.x += dx * min(1.0, dt * 18.0)
        self.y += dy * min(1.0, dt * 18.0)

        # Smooth lift animation
        dlift = self.target_lift_y - self.lift_y
        self.lift_y += dlift * min(1.0, dt * 14.0)

    @property
    def rect(self) -> QRectF:
        return QRectF(self.x - self.width / 2.0, self.y - self.height / 2.0 - self.lift_y, self.width, self.height)


class BoxShuffleGame(BaseGameOverlay):
    """
    Tebak Kardus Snack Kucing (Shell Game / Mystery Box Shuffle).
    Zero horizontal running! Pure memory, focus, and cute cat reactions.
    """
    def __init__(self, pet_window):
        super().__init__(pet_window, title="📦 TEBAK KARDUS SNACK")

        self.game_state = "tutorial"
        self.is_timer_running = False

        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.round_num = 1
        self.correct_guesses = 0
        self.lives = 3

        # High Score
        self.high_score = self.pet_window.settings.get("high_score_box_shuffle", 0)

        # Slots on screen
        self.slot_x_positions: List[float] = []
        self._calculate_slots()

        # 3 Cardboard Boxes
        self.boxes: List[CardboardBox] = [
            CardboardBox(0, 0, self.slot_x_positions[0], self.table_y),
            CardboardBox(1, 1, self.slot_x_positions[1], self.table_y),
            CardboardBox(2, 2, self.slot_x_positions[2], self.table_y),
        ]

        # Shuffle queue
        self.shuffle_swaps: List[Tuple[int, int]] = []  # List of (pos_a, pos_b) swaps
        self.swap_timer = 0.0
        self.swap_duration = 0.32
        self.is_currently_swapping = False
        self.state_timer = 0.0

        # Visual FX
        self.particles: List[BoxParticle] = []
        self.floating_texts: List[FloatingText] = []

        # Position Pet Window sitting above or next to the boxes
        self.pet_target_x = float(self.width() // 2 - self.pet_window.sprite_size // 2)
        self.pet_y = float(self.table_y - self.pet_window.sprite_size - 40)
        self.pet_window.move(int(self.geometry().left() + self.pet_target_x), int(self.geometry().top() + self.pet_y))
        self.pet_window.set_state("idle")
        self.pet_window.raise_()

        # UI Button Rects
        self.start_btn_rect = QRect()
        self.restart_btn_rect = QRect()
        self.quit_btn_rect = QRect()
        self._start_hover = False
        self._restart_hover = False
        self._quit_hover = False

    def _calculate_slots(self):
        cx = float(self.width() / 2.0)
        spacing = 210.0
        self.table_y = float(self.height() / 2.0 + 35.0)
        self.slot_x_positions = [cx - spacing, cx, cx + spacing]

    def update_game_physics(self, dt: float):
        # Update boxes
        for box in self.boxes:
            box.update(dt)

        # Update particles & text
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead]

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if not ft.is_dead]

        # State Machine Logic
        if self.game_state == "show_snack":
            self.state_timer -= dt
            if self.state_timer <= 0:
                # Close the box and start shuffling!
                for b in self.boxes:
                    b.target_lift_y = 0.0
                self._prepare_shuffling()

        elif self.game_state == "shuffling":
            self._process_shuffle(dt)

        elif self.game_state == "revealing":
            self.state_timer -= dt
            if self.state_timer <= 0:
                if self.lives <= 0:
                    self._trigger_game_over()
                else:
                    self._start_new_round()

    def _start_new_round(self):
        """Prepares a fresh round: picks a box for snack and shows it clearly."""
        self.game_state = "show_snack"
        self.state_timer = 1.3  # Show snack for 1.3s
        self.round_num += 1

        # Pick random box for snack
        for b in self.boxes:
            b.has_snack = False
            b.target_lift_y = 0.0

        snack_box = random.choice(self.boxes)
        snack_box.has_snack = True
        snack_box.target_lift_y = 65.0  # Lift open!

        # Audio & Sparkle
        self._play_sound_blip(freq=1600, dur=40)
        self._create_sparkles(snack_box.x, snack_box.y - 25, QColor(255, 215, 50), count=12)
        self.pet_window.set_state("idle")

        slot_label = snack_box.pos_idx + 1
        self.floating_texts.append(FloatingText(snack_box.x, snack_box.y - 135, f"SNACK DI KARDUS [{slot_label}]! 🍣", QColor(255, 220, 60)))

    def _prepare_shuffling(self):
        """Generates a sequence of swaps and enters shuffling state."""
        self.game_state = "shuffling"
        self.is_currently_swapping = False
        self.swap_timer = 0.0

        # Number of swaps increases as streak/round grows
        base_swaps = 5 + min(8, self.round_num + self.streak)
        self.swap_duration = max(0.18, 0.36 - min(0.16, self.streak * 0.025))

        self.shuffle_swaps.clear()
        possible_pairs = [(0, 1), (1, 2), (0, 2)]
        last_pair = None
        for _ in range(base_swaps):
            choices = [p for p in possible_pairs if p != last_pair]
            pair = random.choice(choices)
            self.shuffle_swaps.append(pair)
            last_pair = pair

    def _process_shuffle(self, dt: float):
        """Executes position swaps in the queue smoothly."""
        if not self.is_currently_swapping:
            if not self.shuffle_swaps:
                # All swaps finished! Enter guessing state
                self.game_state = "guessing"
                self.pet_window.set_state("pounce")
                self.floating_texts.append(FloatingText(self.width() / 2, self.table_y - 100, "MANA KARDUS SNACK? [1] [2] [3] 🐾", QColor(100, 240, 255)))
                self._play_sound_blip(freq=1200, dur=60)
                return

            # Pop next swap
            pos_a, pos_b = self.shuffle_swaps.pop(0)
            box_a = next(b for b in self.boxes if b.pos_idx == pos_a)
            box_b = next(b for b in self.boxes if b.pos_idx == pos_b)

            # Swap logical slots
            box_a.pos_idx = pos_b
            box_b.pos_idx = pos_a

            box_a.target_x = self.slot_x_positions[pos_b]
            box_b.target_x = self.slot_x_positions[pos_a]

            self.is_currently_swapping = True
            self.swap_timer = self.swap_duration
            self._play_sound_blip(freq=random.randint(650, 950), dur=25)
        else:
            self.swap_timer -= dt
            if self.swap_timer <= 0:
                self.is_currently_swapping = False

    def select_box(self, box: CardboardBox):
        """Player chooses a box."""
        if self.game_state != "guessing":
            return

        self.game_state = "revealing"
        self.state_timer = 1.6  # Reveal delay
        box.target_lift_y = 65.0

        if box.has_snack:
            # CORRECT GUESS!
            self.correct_guesses += 1
            self.streak += 1
            self.max_streak = max(self.max_streak, self.streak)

            pts = 100 + (self.streak - 1) * 25
            self.score += pts

            self.pet_window.set_state("celebrate", duration_seconds=1.5)
            self._play_sound_blip(freq=1800, dur=80)
            self._create_sparkles(box.x, box.y - 25, QColor(255, 215, 40), count=25)

            streak_tag = f" 🔥 {self.streak}x STREAK!" if self.streak > 1 else ""
            self.floating_texts.append(FloatingText(box.x, box.y - 135, f"✨ +{pts} TEPAT SEKALI!{streak_tag}", QColor(255, 220, 50)))
        else:
            # WRONG GUESS (ZONK)
            self.streak = 0
            self.lives -= 1

            self.pet_window.set_state("overheat", duration_seconds=1.2)
            self._play_sound_blip(freq=350, dur=90)
            self._create_dust(box.x, box.y - 15, QColor(140, 140, 150), count=16)

            # Reveal the correct box as well so player knows where it was
            correct_b = next(b for b in self.boxes if b.has_snack)
            correct_b.target_lift_y = 65.0

            self.floating_texts.append(FloatingText(box.x, box.y - 135, "❌ ZONK! KOSONG", QColor(255, 80, 80)))

    def _create_sparkles(self, x: float, y: float, color: QColor, count: int = 16):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(80, 240)
            self.particles.append(BoxParticle(x, y, color, math.cos(angle) * spd, math.sin(angle) * spd - 60))

    def _create_dust(self, x: float, y: float, color: QColor, count: int = 12):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(40, 140)
            self.particles.append(BoxParticle(x, y, color, math.cos(angle) * spd, math.sin(angle) * spd - 30, size=random.uniform(4, 7)))

    def _play_sound_blip(self, freq: int = 1350, dur: int = 40):
        if self.pet_window.settings.get("sound_enabled", False):
            try:
                import winsound
                winsound.Beep(freq, dur)
            except Exception:
                pass

    def start_game_from_tutorial(self):
        """Starts a fresh game from tutorial card."""
        self.game_state = "show_snack"
        self.is_game_over = False
        self.is_timer_running = True
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.round_num = 0
        self.correct_guesses = 0
        self.lives = 3

        self.particles.clear()
        self.floating_texts.clear()
        self._calculate_slots()

        # Reset boxes
        for i, b in enumerate(self.boxes):
            b.pos_idx = i
            b.x = self.slot_x_positions[i]
            b.target_x = self.slot_x_positions[i]
            b.y = self.table_y
            b.target_y = self.table_y
            b.lift_y = 0.0
            b.target_lift_y = 0.0
            b.has_snack = False

        self._start_new_round()

    def on_game_over(self):
        """Triggered when lives run out."""
        self.game_state = "game_over"

        if self.score > self.high_score:
            self.high_score = self.score
            self.pet_window.settings["high_score_box_shuffle"] = self.high_score
            save_settings(self.pet_window.settings)

        if self.correct_guesses >= 5:
            self.pet_window.set_state("celebrate", duration_seconds=4.0)
            raw_name = self.pet_window.settings.get("user_name", "").strip()
            user_name = f" {raw_name}" if raw_name else ""
            self.pet_window.say(f"Mata kamu tajam banget{user_name}! Snacknya dapet banyak nya~ 📦⭐", 4000)
        else:
            self.pet_window.set_state("idle")
            self.pet_window.say("Kardusnya muter cepet banget nya! Coba lagi yuk? 🐾📦", 3500)

    def restart_game(self):
        self.start_game_from_tutorial()

    def keyPressEvent(self, event: QKeyEvent):
        if self.game_state == "tutorial":
            if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.start_game_from_tutorial()
                event.accept()
                return
        elif self.game_state == "game_over":
            if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.restart_game()
                event.accept()
                return
        elif self.game_state == "guessing":
            # Number keys [1], [2], [3] or [A], [S], [D]
            if event.key() in (Qt.Key.Key_1, Qt.Key.Key_A):
                target_box = next((b for b in self.boxes if b.pos_idx == 0), None)
                if target_box:
                    self.select_box(target_box)
                    event.accept()
                    return
            elif event.key() in (Qt.Key.Key_2, Qt.Key.Key_S):
                target_box = next((b for b in self.boxes if b.pos_idx == 1), None)
                if target_box:
                    self.select_box(target_box)
                    event.accept()
                    return
            elif event.key() in (Qt.Key.Key_3, Qt.Key.Key_D):
                target_box = next((b for b in self.boxes if b.pos_idx == 2), None)
                if target_box:
                    self.select_box(target_box)
                    event.accept()
                    return

        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        if self.game_state == "tutorial":
            self._start_hover = self.start_btn_rect.contains(pos)
        elif self.game_state == "game_over":
            self._restart_hover = self.restart_btn_rect.contains(pos)
            self._quit_hover = self.quit_btn_rect.contains(pos)
        elif self.game_state == "guessing":
            for b in self.boxes:
                b.is_hovered = b.rect.contains(pos.x(), pos.y())

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
        elif self.game_state == "guessing":
            for b in self.boxes:
                if b.rect.contains(pos.x(), pos.y()):
                    self.select_box(b)
                    event.accept()
                    return

        super().mousePressEvent(event)

    # -------------------------------------------------------------
    # Rendering & Pixel Art Graphics
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 1. Top HUD
        self.draw_box_hud(painter)

        if self.game_state == "tutorial":
            self._draw_tutorial_modal(painter)
            return

        # 2. Draw Wooden Table / Shelf surface
        self._draw_table_surface(painter)

        # 3. Draw Cardboard Boxes & Hidden Snack
        for box in self.boxes:
            self._draw_cardboard_box(painter, box)

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
            painter.drawText(int(ft.x - 100), int(ft.y), ft.text)

        # 6. Bottom Controls Hint
        if self.game_state in ["show_snack", "shuffling", "guessing"]:
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255, 220))
            if self.game_state == "guessing":
                hint = "👉 PILIH KARDUS: Klik Langsung atau Tekan [1], [2], [3]  •  [Esc] Keluar"
            elif self.game_state == "shuffling":
                hint = "👀 Perhatikan pergerakan kardus yang berputar... Jangan sampai lengah!"
            else:
                hint = "📦 Ingat-ingat kardus tempat snack disembunyikan!"
            painter.drawText(QRect(0, self.height() - 32, self.width(), 22), Qt.AlignmentFlag.AlignCenter, hint)

        # 7. Game Over Modal
        if self.game_state == "game_over":
            self._draw_game_over_modal(painter)

    def draw_box_hud(self, painter: QPainter):
        """Draws top HUD for Box Shuffle."""
        hud_w = 640
        hud_h = 48
        hud_x = (self.width() - hud_w) // 2
        hud_y = 16

        self.close_btn_rect = QRect(hud_x + hud_w - 105, hud_y + 8, 95, 32)

        # Outer Glow / Border
        painter.setPen(QPen(QColor(240, 160, 60, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 10, 10)

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 200, 120))
        painter.drawText(hud_x + 18, hud_y + 30, "📦 TEBAK KARDUS")

        # Score
        painter.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(hud_x + 225, hud_y + 31, f"🏆 {self.score} PTS")

        # Streak
        s_col = QColor(255, 215, 40) if self.streak >= 3 else QColor(140, 255, 160)
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(s_col)
        painter.drawText(hud_x + 355, hud_y + 31, f"🔥 {self.streak}x")

        # Lives (Vector Hearts)
        heart_start_x = hud_x + 435
        heart_y = hud_y + 24
        for i in range(3):
            hx = heart_start_x + i * 24
            is_active = i < self.lives
            self._draw_hud_heart(painter, hx, heart_y, active=is_active)

        # Close Button
        btn_bg = QColor(220, 50, 60, 240) if self._close_hover else QColor(40, 42, 58, 220)
        btn_border = QColor(255, 140, 140) if self._close_hover else QColor(180, 190, 220, 180)
        painter.setPen(QPen(btn_border, 1.5))
        painter.setBrush(QBrush(btn_bg))
        painter.drawRoundedRect(self.close_btn_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.close_btn_rect, Qt.AlignmentFlag.AlignCenter, "✕ KELUAR")

    def _draw_hud_heart(self, painter: QPainter, x: float, y: float, active: bool = True):
        """Draws a crisp retro heart icon for HUD."""
        painter.save()
        painter.translate(x, y)
        c_fill = QColor(255, 60, 80) if active else QColor(70, 75, 95)
        c_border = QColor(255, 150, 170) if active else QColor(100, 105, 125)

        painter.setPen(QPen(c_border, 1.2))
        painter.setBrush(QBrush(c_fill))

        # Pixel-style heart polygon
        path = QPainterPath()
        path.moveTo(0, 4)
        path.lineTo(-7, -3)
        path.arcTo(-7, -8, 7, 7, 180, -180)
        path.arcTo(0, -8, 7, 7, 180, -180)
        path.lineTo(0, 4)
        painter.drawPath(path)

        painter.restore()

    def _draw_table_surface(self, painter: QPainter):
        """Draws subtle retro wooden mat surface underneath the boxes."""
        w = 720
        h = 24
        x = (self.width() - w) // 2
        y = int(self.table_y + 55)

        painter.setPen(QPen(QColor(160, 100, 45, 180), 2))
        painter.setBrush(QBrush(QColor(65, 40, 20, 220)))
        painter.drawRoundedRect(x, y, w, h, 6, 6)

    def _draw_cardboard_box(self, painter: QPainter, box: CardboardBox):
        """Draws cute pixel-art cardboard box with flap ears, tape, and hidden salmon snack."""
        try:
            painter.save()

            # 1. Shadow underneath
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 70)))
            painter.drawEllipse(QPoint(int(box.x), int(box.y + 52)), int(box.width * 0.48), 12)

            # 2. Draw Golden Salmon Snack on the table IF box is lifted
            if box.has_snack and box.lift_y > 10.0:
                self._draw_golden_salmon_snack(painter, box.x, box.y + 20)

            # 3. Draw Box Body (shifted up by lift_y)
            bx = box.x - box.width / 2.0
            by = box.y - box.height / 2.0 - box.lift_y

            # Glow aura if hovered in guessing state
            if self.game_state == "guessing" and box.is_hovered:
                painter.setPen(QPen(QColor(255, 220, 80, 200), 3.0))
            else:
                painter.setPen(QPen(QColor(120, 75, 30), 2.5))

            # Main Cardboard Surface (Warm Kraft Brown)
            painter.setBrush(QBrush(QColor(215, 160, 95)))
            painter.drawRoundedRect(QRectF(bx, by, box.width, box.height), 10, 10)

            # Darker Side Edge / Depth
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(185, 135, 75)))
            painter.drawRoundedRect(QRectF(bx + box.width - 24, by + 4, 20, box.height - 8), 6, 6)

            # Center Packaging Tape (Warm Cream White)
            painter.setPen(QPen(QColor(150, 100, 50, 120), 1.0))
            painter.setBrush(QBrush(QColor(245, 235, 200, 220)))
            painter.drawRect(QRectF(bx + box.width / 2.0 - 15, by + 4, 30, box.height - 8))

            # Cute Cat Ears Cardboard Flaps on top
            painter.setPen(QPen(QColor(120, 75, 30), 2.0))
            painter.setBrush(QBrush(QColor(225, 175, 110)))
            ear_left = QPolygonF([QPointF(bx + 18, by + 2), QPointF(bx + 32, by - 16), QPointF(bx + 46, by + 2)])
            ear_right = QPolygonF([QPointF(bx + box.width - 46, by + 2), QPointF(bx + box.width - 32, by - 16), QPointF(bx + box.width - 18, by + 2)])
            painter.drawPolygon(ear_left)
            painter.drawPolygon(ear_right)

            # Slot Number Tag (1, 2, or 3)
            slot_num = box.pos_idx + 1
            painter.setFont(QFont("Consolas", 15, QFont.Weight.Bold))
            painter.setPen(QColor(80, 45, 15))
            painter.drawText(QRectF(bx, by + box.height - 42, box.width, 30), Qt.AlignmentFlag.AlignCenter, f"[ {slot_num} ]")

            painter.restore()
        except Exception:
            try:
                painter.restore()
            except Exception:
                pass

    def _draw_golden_salmon_snack(self, painter: QPainter, x: float, y: float, size: float = 48.0):
        """Draws glittering golden salmon treat resting on the table."""
        painter.save()
        painter.translate(x, y)

        s = size
        # Glow Halo
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 215, 0, 75)))
        painter.drawEllipse(QRectF(-s * 0.7, -s * 0.45, s * 1.4, s * 0.9))

        # Golden Body
        painter.setPen(QPen(QColor(130, 80, 0), max(1.5, s * 0.05)))
        painter.setBrush(QBrush(QColor(255, 210, 30)))
        painter.drawEllipse(QRectF(-s * 0.5, -s * 0.28, s, s * 0.56))

        # Salmon Red Stripes
        painter.setPen(QPen(QColor(240, 80, 40), max(1.5, s * 0.05)))
        painter.drawLine(QPointF(-s * 0.18, -s * 0.22), QPointF(-s * 0.18, s * 0.22))
        painter.drawLine(QPointF(0.0, -s * 0.26), QPointF(0.0, s * 0.26))
        painter.drawLine(QPointF(s * 0.18, -s * 0.22), QPointF(s * 0.18, s * 0.22))

        # Golden Tail Fin
        tail = QPolygonF([QPointF(s * 0.42, 0.0), QPointF(s * 0.82, -s * 0.42), QPointF(s * 0.65, 0.0), QPointF(s * 0.82, s * 0.42)])
        painter.setPen(QPen(QColor(130, 80, 0), max(1.2, s * 0.04)))
        painter.setBrush(QBrush(QColor(245, 165, 0)))
        painter.drawPolygon(tail)

        # Eye
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawEllipse(QRectF(-s * 0.38, -s * 0.14, s * 0.11, s * 0.11))

        painter.restore()

    def _draw_tutorial_modal(self, painter: QPainter):
        """Draws How to Play modal before starting."""
        card_w = 540
        card_h = 390
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Glassmorphism Card
        painter.setPen(QPen(QColor(240, 160, 60, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 14, 14)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 200, 120))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "CARA BERMAIN: TEBAK KARDUS")

        # Subtitle
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(180, 200, 230))
        painter.drawText(QRect(card_x, card_y + 48, card_w, 20), Qt.AlignmentFlag.AlignCenter, "Latih fokus mata & memori: cari snack lezat di dalam kardus!")

        # Visual Guide Box
        box_y = card_y + 80

        # Preview of Salmon & Box
        self._draw_golden_salmon_snack(painter, card_x + 50, box_y + 26, size=32.0)
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 215, 50))
        painter.drawText(card_x + 85, box_y + 20, "1. Perhatikan Snack")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 85, box_y + 38, "Di awal ronde, salah satu kardus akan terbuka memperlihatkan snack.")

        # Preview of Shuffle
        painter.setFont(QFont("Segoe UI", 16))
        painter.drawText(card_x + 45, box_y + 80, "🔀")
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(120, 240, 255))
        painter.drawText(card_x + 90, box_y + 70, "2. Ikuti Gerakan Kardus")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 90, box_y + 88, "Kardus-kardus akan berputar & bertukar tempat dengan cepat!")

        # Preview of Guessing
        painter.setFont(QFont("Segoe UI", 16))
        painter.drawText(card_x + 45, box_y + 130, "🎯")
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(140, 255, 160))
        painter.drawText(card_x + 90, box_y + 120, "3. Tebak & Dapatkan Poin")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 90, box_y + 138, "Tebak kardus yang benar untuk kumpulkan skor & streak kombo!")

        # Controls Section
        ctrl_y = box_y + 165
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(card_x + 40, ctrl_y, card_x + card_w - 40, ctrl_y)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 235, 120))
        painter.drawText(card_x + 45, ctrl_y + 25, "🎮 KONTROL:")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(220, 230, 245))
        painter.drawText(card_x + 150, ctrl_y + 25, "• Klik Kardus yang ingin dipilih menggunakan Mouse.")
        painter.drawText(card_x + 150, ctrl_y + 45, "• Atau Tekan Tombol [1], [2], [3] (atau [A][S][D]) di Keyboard.")
        painter.drawText(card_x + 150, ctrl_y + 65, "• Kamu memiliki 3 Kesempatan (Nyawa ❤️❤️❤️).")

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

    def _draw_game_over_modal(self, painter: QPainter):
        """Draws game over result dialog."""
        card_w = 440
        card_h = 320
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Backdrop Shadow
        painter.setPen(QPen(QColor(240, 160, 60, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 12, 12)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 200, 120))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "🏆 HASIL TEBAK KARDUS!")

        # Final Score & High Score
        painter.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(QRect(card_x, card_y + 58, card_w, 36), Qt.AlignmentFlag.AlignCenter, f"{self.score} PTS")

        if self.score >= self.high_score and self.score > 0:
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 215, 50))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, "🌟 REKOR TEBAK BARU! 🌟")
        else:
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor(180, 190, 210))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, f"Rekor Tertinggi: {self.high_score} PTS")

        # Stats Breakdown
        self._draw_golden_salmon_snack(painter, card_x + 65, card_y + 140)

        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 235, 250))
        painter.drawText(card_x + 95, card_y + 145, "Tebakan Tepat:")
        painter.drawText(card_x + 290, card_y + 145, f"{self.correct_guesses} ronde")

        painter.drawText(card_x + 95, card_y + 175, "🔥 Streak Tertinggi:")
        painter.drawText(card_x + 290, card_y + 175, f"{self.max_streak}x Streak")

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

        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.restart_btn_rect, Qt.AlignmentFlag.AlignCenter, "▶ MAIN LAGI (SPASI)")

        # Quit Button
        q_bg = QColor(210, 50, 60, 245) if self._quit_hover else QColor(150, 35, 45, 230)
        painter.setPen(QPen(QColor(255, 130, 130), 1.5))
        painter.setBrush(QBrush(q_bg))
        painter.drawRoundedRect(self.quit_btn_rect, 6, 6)

        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.quit_btn_rect, Qt.AlignmentFlag.AlignCenter, "✕ SELESAI")
