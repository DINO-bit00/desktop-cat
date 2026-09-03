"""
Cat Yarn Bounce (Juggling Bola Benang) - NyangBuddy Arcade Mini-Game (Stage 2).
Players juggle a bouncy wool yarn ball using the desktop cat and mouse / spacebar,
keeping it in the air for as many consecutive combos as possible!
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


class YarnTrailPoint:
    """A segment of the wool yarn string trailing behind the ball."""
    def __init__(self, x: float, y: float, color: QColor):
        self.x = x
        self.y = y
        self.color = color
        self.age = 0.0
        self.lifetime = 0.45  # seconds

    def update(self, dt: float):
        self.age += dt

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime

    @property
    def opacity(self) -> float:
        return max(0.0, 1.0 - (self.age / self.lifetime))


class YarnFuzzParticle:
    """Fluffy wool fuzz particles bursting on bounce."""
    def __init__(self, x: float, y: float, color: QColor, vx: float, vy: float, size: float = 4.5):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.lifetime = random.uniform(0.35, 0.65)
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 120.0 * dt
        self.size = max(0.5, self.size * (1.0 - dt * 1.6))

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class FloatingText:
    """Floating score and combo popup."""
    def __init__(self, x: float, y: float, text: str, color: QColor):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.opacity = 1.0
        self.lifetime = 0.95
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.y -= 40.0 * dt
        self.opacity = max(0.0, 1.0 - (self.age / self.lifetime))

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime


class YarnBall:
    """Bouncy physics wool yarn ball."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 28.0  # 56px diameter
        self.vx = random.choice([-160.0, 160.0])
        self.vy = -350.0
        self.gravity = 780.0
        self.rotation = 0.0
        self.angular_velocity = 220.0
        self.color = QColor(255, 75, 130)  # Vibrant Coral Pink wool
        self.trail: List[YarnTrailPoint] = []
        self.trail_timer = 0.0

    def update(self, dt: float, screen_w: float, screen_h: float) -> bool:
        """
        Updates physics. Returns False if ball hit bottom floor (Game Over).
        """
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += (self.vx * 0.8) * dt

        # Spawn yarn trail point
        self.trail_timer += dt
        if self.trail_timer >= 0.03:
            self.trail_timer = 0.0
            self.trail.append(YarnTrailPoint(self.x, self.y, self.color))

        for tp in self.trail:
            tp.update(dt)
        self.trail = [tp for tp in self.trail if not tp.is_dead]

        # Bounce off left wall
        if self.x - self.radius <= 10:
            self.x = 10 + self.radius
            self.vx = abs(self.vx) * 0.96

        # Bounce off right wall
        if self.x + self.radius >= screen_w - 10:
            self.x = screen_w - 10 - self.radius
            self.vx = -abs(self.vx) * 0.96

        # Bounce off ceiling
        if self.y - self.radius <= 70:
            self.y = 70 + self.radius
            self.vy = abs(self.vy) * 0.92

        # Check floor collision (Game Over)
        if self.y + self.radius >= screen_h - 15:
            return False

        return True


class YarnBounceGame(BaseGameOverlay):
    """
    Cat Yarn Bounce Mini-Game Overlay.
    """
    def __init__(self, pet_window):
        super().__init__(pet_window, title="🧶 CAT YARN BOUNCE")

        # Game states: 'tutorial', 'playing', 'game_over'
        self.game_state = "tutorial"
        self.is_timer_running = False

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.total_bounces = 0

        # High Score from settings
        self.high_score = self.pet_window.settings.get("high_score_yarn_bounce", 0)

        # Game entities
        self.yarn_ball = YarnBall(self.width() / 2.0, self.height() / 2.5)
        self.floating_texts: List[FloatingText] = []
        self.fuzz_particles: List[YarnFuzzParticle] = []

        # Cat positioning & jump physics
        self.cat_target_x = float(self.width() // 2 - self.pet_window.sprite_size // 2)
        self.cat_current_x = self.cat_target_x
        self.cat_y = float(self.height() - self.pet_window.sprite_size - 25)
        self.cat_jump_offset_y = 0.0
        self.cat_jump_vy = 0.0
        self.cat_jump_active = False

        # Snap pet window to start position
        self.pet_window.move(int(self.geometry().left() + self.cat_current_x), int(self.geometry().top() + self.cat_y))
        self.pet_window.set_state("idle")
        self.pet_window.raise_()

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
        if self.game_state != "playing":
            return

        # 1. Update Cat Horizontal Movement
        if self.key_left_pressed:
            self.cat_target_x -= 620.0 * dt
        elif self.key_right_pressed:
            self.cat_target_x += 620.0 * dt

        # Clamp inside screen
        max_x = float(self.width() - self.pet_window.sprite_size - 10)
        self.cat_target_x = max(10.0, min(max_x, self.cat_target_x))

        # Smooth lerp
        dx = self.cat_target_x - self.cat_current_x
        self.cat_current_x += dx * min(1.0, dt * 16.0)

        # 2. Update Cat Jump Physics
        if self.cat_jump_active:
            self.cat_jump_vy += 1500.0 * dt
            self.cat_jump_offset_y += self.cat_jump_vy * dt
            if self.cat_jump_offset_y >= 0.0:
                self.cat_jump_offset_y = 0.0
                self.cat_jump_vy = 0.0
                self.cat_jump_active = False
                if self.pet_window.state == "celebrate":
                    self.pet_window.set_state("idle")

        # Move pet window
        screen_geo = self.geometry()
        target_screen_x = int(screen_geo.left() + self.cat_current_x)
        target_screen_y = int(screen_geo.top() + self.cat_y + self.cat_jump_offset_y)
        self.pet_window.move(target_screen_x, target_screen_y)

        # Update cat facing animation
        if not self.cat_jump_active:
            if abs(dx) > 4.0:
                if dx < 0 and self.pet_window.state != "walk_left":
                    self.pet_window.set_state("walk_left")
                elif dx > 0 and self.pet_window.state != "walk_right":
                    self.pet_window.set_state("walk_right")
            else:
                if self.pet_window.state not in ["idle", "celebrate", "stretch", "feed"]:
                    self.pet_window.set_state("idle")

        # 3. Update Yarn Ball Physics
        is_alive = self.yarn_ball.update(dt, float(self.width()), float(self.height()))
        if not is_alive:
            self._trigger_game_over()
            return

        # 4. Check Collision between Cat and Yarn Ball
        cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        cat_top_y = self.cat_y + self.cat_jump_offset_y + 15
        cat_radius = self.pet_window.sprite_size * 0.48

        # Only bounce if ball is moving downwards towards cat
        if self.yarn_ball.vy > 0:
            dist = math.hypot(self.yarn_ball.x - cat_center_x, self.yarn_ball.y - cat_top_y)
            if dist <= (cat_radius + self.yarn_ball.radius):
                self._bounce_yarn(power=False)

        # 5. Update Floating Texts & Particles
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if not ft.is_dead]

        for p in self.fuzz_particles:
            p.update(dt)
        self.fuzz_particles = [p for p in self.fuzz_particles if not p.is_dead]

    def _bounce_yarn(self, power: bool = False):
        """Triggers bounce physics, combo increase, audio & visual FX."""
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.total_bounces += 1

        pts = 10 + self.combo * 2
        if power:
            pts += 20
        self.score += pts

        # Bounce velocity
        bounce_speed = 680.0 + min(180.0, self.combo * 10.0)
        if power:
            bounce_speed += 120.0
        self.yarn_ball.vy = -bounce_speed

        # Nudge horizontal velocity based on offset from cat center
        cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        offset_x = (self.yarn_ball.x - cat_center_x) / (self.pet_window.sprite_size * 0.5)
        self.yarn_ball.vx = offset_x * 320.0 + random.uniform(-40, 40)

        # Wool color shift at high combos
        if self.combo >= 20:
            self.yarn_ball.color = QColor(255, 215, 0)  # Golden wool
        elif self.combo >= 10:
            self.yarn_ball.color = QColor(0, 220, 255)  # Cyan wool
        elif self.combo >= 5:
            self.yarn_ball.color = QColor(160, 90, 255)  # Purple wool
        else:
            self.yarn_ball.color = QColor(255, 75, 130)  # Pink wool

        # Cat animation & sound
        self.pet_window.set_state("celebrate", duration_seconds=0.4)
        sound_freq = min(2200, 1100 + self.combo * 60)
        self._play_sound_blip(freq=sound_freq, dur=35)

        # Fuzz particles
        self._spawn_fuzz_particles(self.yarn_ball.x, self.yarn_ball.y, self.yarn_ball.color, count=16)

        # Floating text
        if power:
            label = f"🚀 +{pts} POWER BOUNCE! ({self.combo}x)"
            self.floating_texts.append(FloatingText(self.yarn_ball.x, self.yarn_ball.y - 25, label, QColor(255, 220, 60)))
        elif self.combo % 5 == 0:
            label = f"✨ +{pts} ({self.combo}x MEGA COMBO!)"
            self.floating_texts.append(FloatingText(self.yarn_ball.x, self.yarn_ball.y - 25, label, QColor(100, 245, 255)))
        else:
            label = f"+{pts} 🧶 ({self.combo}x)"
            self.floating_texts.append(FloatingText(self.yarn_ball.x, self.yarn_ball.y - 20, label, self.yarn_ball.color))

    def _spawn_fuzz_particles(self, x: float, y: float, color: QColor, count: int = 14):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(80, 260)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - 60.0
            self.fuzz_particles.append(YarnFuzzParticle(x, y, color, vx, vy, size=random.uniform(3.5, 6.5)))

    def _play_sound_blip(self, freq: int = 1350, dur: int = 40):
        if self.pet_window.settings.get("sound_enabled", False):
            try:
                import winsound
                winsound.Beep(freq, dur)
            except Exception:
                pass

    def start_game_from_tutorial(self):
        """Starts or restarts the active yarn bounce game with a high loft launch from above the cat."""
        self.game_state = "playing"
        self.is_game_over = False
        self.is_timer_running = False
        self.time_remaining = 99999.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.total_bounces = 0

        # Center Cat position
        self.cat_target_x = float(self.width() // 2 - self.pet_window.sprite_size // 2)
        self.cat_current_x = self.cat_target_x
        self.cat_jump_offset_y = 0.0
        self.cat_jump_vy = 0.0
        self.cat_jump_active = False

        if hasattr(self.pet_window, "bubble"):
            self.pet_window.bubble.hide()

        screen_geo = self.geometry()
        target_screen_x = int(screen_geo.left() + self.cat_current_x)
        target_screen_y = int(screen_geo.top() + self.cat_y)
        self.pet_window.move(target_screen_x, target_screen_y)

        # Launch ball upwards from directly above the cat
        ball_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        ball_y = self.cat_y - 35.0
        self.yarn_ball = YarnBall(ball_x, ball_y)
        self.yarn_ball.vy = -680.0  # High launch arch!
        self.yarn_ball.vx = random.choice([-90.0, 90.0])

        self.floating_texts.clear()
        self.fuzz_particles.clear()
        self.floating_texts.append(FloatingText(ball_x, ball_y - 20, "SERVIS AWAL! 🧶🚀", QColor(255, 230, 80)))
        self._spawn_fuzz_particles(ball_x, ball_y, self.yarn_ball.color, count=12)
        self._play_sound_blip(freq=1450, dur=40)
        self.pet_window.set_state("celebrate", duration_seconds=0.5)

    def on_game_over(self):
        """Triggered when yarn ball touches the floor."""
        self.game_state = "game_over"
        self.is_game_over = True
        self.is_timer_running = False
        self.time_remaining = 99999.0
        self.floating_texts.clear()

        if hasattr(self.pet_window, "bubble"):
            self.pet_window.bubble.hide()

        # Check High Score
        if self.score > self.high_score:
            self.high_score = self.score
            self.pet_window.settings["high_score_yarn_bounce"] = self.high_score
            save_settings(self.pet_window.settings)

        # Pet animation reaction (dialogue is rendered cleanly inside the modal card)
        if self.max_combo >= 15:
            self.pet_window.set_state("celebrate", duration_seconds=4.0)
        else:
            self.pet_window.set_state("sulk", duration_seconds=4.0)

    def close_game(self):
        if hasattr(self.pet_window, "bubble"):
            self.pet_window.bubble.hide()
        super().close_game()

    def restart_game(self):
        self.is_game_over = False
        self.is_timer_running = False
        self.time_remaining = 99999.0
        if hasattr(self.pet_window, "bubble"):
            self.pet_window.bubble.hide()
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
                # Cat leaps into the air with power bounce
                self.cat_jump_vy = -480.0
                self.cat_jump_active = True
                self.pet_window.set_state("celebrate", duration_seconds=0.45)
                # Check if ball is within reach for power bounce
                cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
                cat_top_y = self.cat_y + self.cat_jump_offset_y
                dist = math.hypot(self.yarn_ball.x - cat_center_x, self.yarn_ball.y - cat_top_y)
                if dist <= (self.pet_window.sprite_size * 1.2 + self.yarn_ball.radius):
                    self._bounce_yarn(power=True)
                event.accept()
                return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.key_left_pressed = False
        elif event.key() in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.key_right_pressed = False
        super().keyReleaseEvent(event)

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
            # Clicking directly on the yarn ball gives a Power Bounce!
            dist = math.hypot(self.yarn_ball.x - pos.x(), self.yarn_ball.y - pos.y())
            if dist <= self.yarn_ball.radius * 1.5:
                self._bounce_yarn(power=True)
                event.accept()
                return

        super().mousePressEvent(event)

    # -------------------------------------------------------------
    # Rendering & Visual FX
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 1. Draw Arcade Top HUD
        self.draw_yarn_hud(painter)

        if self.game_state == "tutorial":
            self._draw_tutorial_modal(painter)
            return

        # 2. Draw Wool Yarn Trail String
        self._draw_yarn_trail(painter)

        # 3. Draw Bouncy Yarn Ball
        self._draw_yarn_ball(painter, self.yarn_ball)

        # 4. Draw Fuzz Particles
        for p in self.fuzz_particles:
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
            hint = "🕹️ Gerakkan Kucing ke Bawah Bola  •  [Spasi] / Klik untuk POWER BOUNCE 🚀  •  [Esc] Keluar"
            painter.drawText(QRect(0, self.height() - 32, self.width(), 22), Qt.AlignmentFlag.AlignCenter, hint)

        # 7. Draw Game Over Modal
        if self.game_state == "game_over":
            self._draw_game_over_modal(painter)

    def draw_yarn_hud(self, painter: QPainter):
        """Draws top HUD for Yarn Bounce."""
        hud_w = 640
        hud_h = 48
        hud_x = (self.width() - hud_w) // 2
        hud_y = 16

        self.close_btn_rect = QRect(hud_x + hud_w - 105, hud_y + 8, 95, 32)

        # Outer Glow / Border
        painter.setPen(QPen(QColor(255, 75, 130, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 10, 10)

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 180, 210))
        painter.drawText(hud_x + 18, hud_y + 30, "🧶 CAT YARN BOUNCE")

        # Score
        painter.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(hud_x + 280, hud_y + 31, f"🏆 {self.score} PTS")

        # Combo
        combo_col = QColor(255, 220, 50) if self.combo >= 5 else QColor(120, 255, 140)
        painter.setPen(combo_col)
        painter.drawText(hud_x + 420, hud_y + 31, f"🔥 {self.combo}x COMBO")

        # Close Button
        btn_bg = QColor(220, 50, 60, 240) if self._close_hover else QColor(40, 42, 58, 220)
        btn_border = QColor(255, 140, 140) if self._close_hover else QColor(180, 190, 220, 180)
        painter.setPen(QPen(btn_border, 1.5))
        painter.setBrush(QBrush(btn_bg))
        painter.drawRoundedRect(self.close_btn_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.close_btn_rect, Qt.AlignmentFlag.AlignCenter, "✕ KELUAR")

    def _draw_yarn_trail(self, painter: QPainter):
        """Draws glowing wool string trail behind the ball."""
        if len(self.yarn_ball.trail) < 2:
            return

        for i in range(len(self.yarn_ball.trail) - 1):
            p1 = self.yarn_ball.trail[i]
            p2 = self.yarn_ball.trail[i + 1]
            op = p1.opacity * 0.7
            col = QColor(p1.color)
            col.setAlphaF(op)
            painter.setPen(QPen(col, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(p1.x, p1.y), QPointF(p2.x, p2.y))

    def _draw_yarn_ball(self, painter: QPainter, ball: YarnBall):
        """Draws realistic stylized pixel-art wool yarn ball with windings and strands."""
        try:
            painter.save()
            painter.translate(ball.x, ball.y)
            painter.rotate(ball.rotation)

            r = ball.radius

            # Glow aura
            painter.setPen(Qt.PenStyle.NoPen)
            glow_col = QColor(ball.color)
            glow_col.setAlpha(45)
            painter.setBrush(QBrush(glow_col))
            painter.drawEllipse(QRectF(-r * 1.25, -r * 1.25, r * 2.5, r * 2.5))

            # Main Wool Ball Sphere
            dark_border = QColor(ball.color).darker(160)
            painter.setPen(QPen(dark_border, 2.5))
            painter.setBrush(QBrush(ball.color))
            painter.drawEllipse(QRectF(-r, -r, r * 2, r * 2))

            # Wool Strand Windings & Curves
            highlight_col = QColor(ball.color).lighter(140)
            painter.setPen(QPen(highlight_col, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(QRectF(-r * 0.75, -r * 0.75, r * 1.5, r * 1.5), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(-r * 0.75, -r * 0.75, r * 1.5, r * 1.5), 210 * 16, 120 * 16)

            shade_col = QColor(ball.color).darker(130)
            painter.setPen(QPen(shade_col, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(QRectF(-r * 0.85, -r * 0.35, r * 1.7, r * 0.7), 0, 180 * 16)
            painter.drawArc(QRectF(-r * 0.35, -r * 0.85, r * 0.7, r * 1.7), 90 * 16, 180 * 16)

            # Loose Hanging Yarn Strand
            painter.setPen(QPen(highlight_col, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            strand_path = QPainterPath()
            strand_path.moveTo(r * 0.6, -r * 0.4)
            strand_path.quadTo(r * 1.2, -r * 0.8, r * 1.4, -r * 0.3)
            painter.drawPath(strand_path)

            painter.restore()
        except Exception:
            try:
                painter.restore()
            except Exception:
                pass

    def _draw_tutorial_modal(self, painter: QPainter):
        """Draws clear How to Play tutorial screen before starting."""
        card_w = 540
        card_h = 390
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Glassmorphism Card
        painter.setPen(QPen(QColor(255, 75, 130, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 14, 14)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 180, 210))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "CARA BERMAIN: CAT YARN BOUNCE")

        # Subtitle
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(180, 200, 230))
        painter.drawText(QRect(card_x, card_y + 48, card_w, 20), Qt.AlignmentFlag.AlignCenter, "Jaga bola benang agar tidak menyentuh lantai selama mungkin!")

        # Visual preview of yarn ball
        preview_ball = YarnBall(card_x + 55, card_y + 115)
        preview_ball.radius = 24.0
        self._draw_yarn_ball(painter, preview_ball)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 100, 160))
        painter.drawText(card_x + 95, card_y + 110, "Bola Benang Wol (Yarn Ball)")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 95, card_y + 130, "• Pantulkan dengan kepala/cakar kucing untuk raih skor combo!")
        painter.drawText(card_x + 95, card_y + 150, "• Semakin tinggi combo, warna benang akan berubah emas!")

        # Controls Section
        ctrl_y = card_y + 185
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(card_x + 40, ctrl_y, card_x + card_w - 40, ctrl_y)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 235, 120))
        painter.drawText(card_x + 45, ctrl_y + 25, "🎮 KONTROL:")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(220, 230, 245))
        painter.drawText(card_x + 150, ctrl_y + 25, "• Geser Mouse atau tombol [A][D] untuk mengarahkan kucing.")
        painter.drawText(card_x + 150, ctrl_y + 45, "• Tekan [Spasi] atau Klik Bola untuk POWER BOUNCE 🚀.")
        painter.drawText(card_x + 150, ctrl_y + 65, "• Jangan biarkan bola menyentuh dasar lantai layar!")

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
        """Draws retro game over result dialog."""
        card_w = 440
        card_h = 320
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Backdrop Shadow
        painter.setPen(QPen(QColor(255, 75, 130, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 12, 12)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 180, 210))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "🏆 HASIL JUGGLING BENANG!")

        # Final Score & High Score
        painter.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(QRect(card_x, card_y + 58, card_w, 36), Qt.AlignmentFlag.AlignCenter, f"{self.score} PTS")

        if self.score >= self.high_score and self.score > 0:
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 215, 50))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, "🌟 REKOR JUGGLING BARU! 🌟")
        else:
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor(180, 190, 210))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, f"Rekor Tertinggi: {self.high_score} PTS")

        # Stats Breakdown
        preview_ball = YarnBall(card_x + 65, card_y + 145)
        preview_ball.radius = 16.0
        self._draw_yarn_ball(painter, preview_ball)

        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 235, 250))
        painter.drawText(card_x + 90, card_y + 145, "Total Pantulan:")
        painter.drawText(card_x + 290, card_y + 145, f"{self.total_bounces} kali")

        painter.drawText(card_x + 90, card_y + 175, "🔥 Combo Tertinggi:")
        painter.drawText(card_x + 290, card_y + 175, f"{self.max_combo}x Combo")

        # Cat Game Over Quote (Clean native font inside the card)
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.setPen(QColor(255, 215, 120))
        raw_name = self.pet_window.settings.get("user_name", "").strip()
        u_name = f" {raw_name}" if raw_name else ""
        if self.max_combo >= 15:
            quote = f"🐾 \"Jago banget jugglingnya{u_name}! Seru banget nya~ 🧶⭐\""
        else:
            quote = f"🐾 \"Ups, bolanya jatuh nya{u_name}! Mau coba main lagi?\""
        painter.drawText(QRect(card_x + 20, card_y + 204, card_w - 40, 24), Qt.AlignmentFlag.AlignCenter, quote)

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
