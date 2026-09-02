"""
Laser Hunter (Berburu Titik Laser Virtual) - NyangBuddy Arcade Mini-Game (Stage 3).
Cats love chasing red laser dots! Players guide the cat to pounce on dynamic neon laser targets,
building high speed combos within 30 seconds!
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


class LaserSparkParticle:
    """Sparkling luminous laser particles on catch."""
    def __init__(self, x: float, y: float, color: QColor, vx: float, vy: float, size: float = 5.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.lifetime = random.uniform(0.3, 0.55)
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.size = max(0.5, self.size * (1.0 - dt * 2.0))

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


class ClawSlash:
    """Luminous claw swipe visual effect on spacebar pounce."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.age = 0.0
        self.lifetime = 0.32
        self.scale = 0.6

    def update(self, dt: float):
        self.age += dt
        self.scale = min(1.4, 0.6 + (self.age / self.lifetime) * 0.8)
        self.y -= 40.0 * dt

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime

    @property
    def opacity(self) -> float:
        return max(0.0, 1.0 - (self.age / self.lifetime))


class LaserTarget:
    """
    Dynamic laser dot with smooth movement, erratic dashes, and pulse animations.
    Types:
      - 'red_dot': Standard agile laser dot (+10 PTS)
      - 'gold_dash': Super fast golden laser dot (+30 PTS)
      - 'star_pulse': Rare flashing star laser bonus (+50 PTS)
    """
    def __init__(self, target_type: str, screen_w: float, screen_h: float):
        self.target_type = target_type
        self.radius = 18.0 if target_type != "star_pulse" else 22.0
        self.is_caught = False
        self.age = 0.0
        self.lifetime = 7.0 if target_type != "star_pulse" else 4.5
        self.pulse_phase = random.uniform(0, math.pi * 2)

        # Set Colors
        if target_type == "red_dot":
            self.color = QColor(255, 30, 60)
            self.glow_color = QColor(255, 60, 90, 80)
            self.pts = 10
            self.speed = random.uniform(220.0, 360.0)
        elif target_type == "gold_dash":
            self.color = QColor(255, 190, 20)
            self.glow_color = QColor(255, 220, 50, 90)
            self.pts = 30
            self.speed = random.uniform(380.0, 520.0)
        else:  # star_pulse
            self.color = QColor(140, 240, 255)
            self.glow_color = QColor(180, 255, 255, 110)
            self.pts = 50
            self.speed = random.uniform(180.0, 280.0)

        # Positioning inside screen margins
        margin_x = 80.0
        margin_y = 100.0
        self.x = random.uniform(margin_x, max(margin_x + 100, screen_w - margin_x))
        self.y = random.uniform(margin_y, max(margin_y + 100, screen_h - margin_y - 40))

        # Target waypoint navigation
        self.target_x = self.x
        self.target_y = self.y
        self.waypoint_timer = 0.0
        self.pick_new_waypoint(screen_w, screen_h)

    def pick_new_waypoint(self, screen_w: float, screen_h: float):
        margin_x = 60.0
        margin_y = 90.0
        self.target_x = random.uniform(margin_x, max(margin_x + 100, screen_w - margin_x))
        self.target_y = random.uniform(margin_y, max(margin_y + 100, screen_h - margin_y - 40))
        self.waypoint_timer = random.uniform(0.6, 1.4)

    def update(self, dt: float, screen_w: float, screen_h: float):
        self.age += dt
        self.pulse_phase += 8.0 * dt

        # Move towards target waypoint
        self.waypoint_timer -= dt
        if self.waypoint_timer <= 0:
            self.pick_new_waypoint(screen_w, screen_h)

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 8.0:
            step = min(dist, self.speed * dt)
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
        else:
            self.pick_new_waypoint(screen_w, screen_h)

    @property
    def is_dead(self) -> bool:
        return self.is_caught or (self.age >= self.lifetime)


class LaserHunterGame(BaseGameOverlay):
    """
    Laser Hunter Mini-Game Overlay with 30s timer, laser dots, and high-energy pounce action.
    """
    def __init__(self, pet_window):
        super().__init__(pet_window, title="🔴 LASER HUNTER")

        # Game states: 'tutorial', 'playing', 'game_over'
        self.game_state = "tutorial"
        self.is_timer_running = False

        self.game_time_limit = 30.0
        self.time_remaining = self.game_time_limit
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.red_caught_count = 0
        self.gold_caught_count = 0
        self.star_caught_count = 0

        # High Score from settings
        self.high_score = self.pet_window.settings.get("high_score_laser_hunter", 0)

        # Entities
        self.lasers: List[LaserTarget] = []
        self.sparks: List[LaserSparkParticle] = []
        self.floating_texts: List[FloatingText] = []
        self.claw_slashes: List[ClawSlash] = []

        # Cat steering & vertical leaping physics
        self.cat_target_x = float(self.width() // 2 - self.pet_window.sprite_size // 2)
        self.cat_current_x = self.cat_target_x
        self.cat_y = float(self.height() - self.pet_window.sprite_size - 25)
        self.cat_jump_offset_y = 0.0
        self.cat_jump_vy = 0.0
        self.cat_jump_active = False

        # Snap pet window
        self.pet_window.move(int(self.geometry().left() + self.cat_current_x), int(self.geometry().top() + self.cat_y))
        self.pet_window.set_state("idle")
        self.pet_window.raise_()

        # Controls & Buttons
        self.key_left_pressed = False
        self.key_right_pressed = False
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
            self.cat_target_x -= 640.0 * dt
        elif self.key_right_pressed:
            self.cat_target_x += 640.0 * dt

        max_x = float(self.width() - self.pet_window.sprite_size - 10)
        self.cat_target_x = max(10.0, min(max_x, self.cat_target_x))

        dx = self.cat_target_x - self.cat_current_x
        self.cat_current_x += dx * min(1.0, dt * 16.0)

        # 2. Update Cat Jump / Pounce Physics
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

        # 3. Maintain active lasers (keep 2-3 lasers on screen)
        target_count = 2 if self.combo < 5 else 3
        while len(self.lasers) < target_count:
            # Pick random type based on rarity
            roll = random.random()
            if roll < 0.60:
                ltype = "red_dot"
            elif roll < 0.88:
                ltype = "gold_dash"
            else:
                ltype = "star_pulse"
            self.lasers.append(LaserTarget(ltype, float(self.width()), float(self.height())))

        # 4. Update Laser Targets
        cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        cat_top_y = self.cat_y + self.cat_jump_offset_y + 15
        catch_radius = self.pet_window.sprite_size * 0.52

        for laser in self.lasers:
            laser.update(dt, float(self.width()), float(self.height()))

            # Check collision with cat body/head
            if not laser.is_caught:
                dist = math.hypot(laser.x - cat_center_x, laser.y - cat_top_y)
                if dist <= (catch_radius + laser.radius):
                    self._catch_laser(laser, power=False)

        # Filter dead lasers
        self.lasers = [l for l in self.lasers if not l.is_dead]

        # 5. Update Sparks, Floating Texts, Claw Slashes
        for p in self.sparks:
            p.update(dt)
        self.sparks = [p for p in self.sparks if not p.is_dead]

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if not ft.is_dead]

        for cs in self.claw_slashes:
            cs.update(dt)
        self.claw_slashes = [cs for cs in self.claw_slashes if not cs.is_dead]

    def _catch_laser(self, laser: LaserTarget, power: bool = False):
        """Cat successfully pounces and snatches the laser dot."""
        laser.is_caught = True
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)

        pts = laser.pts + (self.combo - 1) * 2
        if power:
            pts += 15
        self.score += pts

        # Track category
        if laser.target_type == "red_dot":
            self.red_caught_count += 1
            sound_freq = 1500 + min(600, self.combo * 40)
            tag = "🔴 RED LASER!"
        elif laser.target_type == "gold_dash":
            self.gold_caught_count += 1
            sound_freq = 1800 + min(600, self.combo * 40)
            tag = "⚡ GOLD DASH!"
        else:  # star_pulse
            self.star_caught_count += 1
            sound_freq = 2200
            tag = "🌟 STAR LASER!"

        # Cat reaction & sound
        self.pet_window.set_state("celebrate", duration_seconds=0.4)
        self._play_sound_blip(freq=sound_freq, dur=35)

        # Visual feedback
        self._create_sparks(laser.x, laser.y, laser.color, count=18)

        if power:
            label = f"🚀 +{pts} POUNCE CATCH! ({self.combo}x)"
        elif self.combo % 5 == 0:
            label = f"✨ +{pts} {tag} ({self.combo}x FRENZY!)"
        else:
            label = f"+{pts} {tag}"

        self.floating_texts.append(FloatingText(laser.x, laser.y - 20, label, laser.color))

    def _attempt_space_pounce(self):
        """Cat leaps towards the closest laser with high-energy claw swipe."""
        self.cat_jump_vy = -480.0
        self.cat_jump_active = True
        self.pet_window.set_state("celebrate", duration_seconds=0.45)

        cat_center_x = self.cat_current_x + self.pet_window.sprite_size / 2.0
        cat_top_y = self.cat_y + self.cat_jump_offset_y - 20
        self.claw_slashes.append(ClawSlash(cat_center_x, cat_top_y))

        self._play_sound_blip(freq=1650, dur=35)
        self._create_sparks(cat_center_x, cat_top_y, QColor(255, 60, 90), count=6)

        # Snatch laser in expanded air zone
        for laser in self.lasers:
            if not laser.is_caught:
                dist = math.hypot(laser.x - cat_center_x, laser.y - (cat_top_y - 25))
                if dist <= (self.pet_window.sprite_size * 1.3 + laser.radius * 1.5):
                    self._catch_laser(laser, power=True)
                    break

    def _create_sparks(self, x: float, y: float, color: QColor, count: int = 14):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(90, 280)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            self.sparks.append(LaserSparkParticle(x, y, color, vx, vy, size=random.uniform(3.5, 6.5)))

    def _play_sound_blip(self, freq: int = 1350, dur: int = 40):
        if self.pet_window.settings.get("sound_enabled", False):
            try:
                import winsound
                winsound.Beep(freq, dur)
            except Exception:
                pass

    def start_game_from_tutorial(self):
        """Starts or restarts the laser hunter game."""
        self.game_state = "playing"
        self.is_game_over = False
        self.is_timer_running = True
        self.last_tick_time = time.time()
        self.time_remaining = self.game_time_limit
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.red_caught_count = 0
        self.gold_caught_count = 0
        self.star_caught_count = 0

        # Center Cat
        self.cat_target_x = float(self.width() // 2 - self.pet_window.sprite_size // 2)
        self.cat_current_x = self.cat_target_x
        self.cat_jump_offset_y = 0.0
        self.cat_jump_vy = 0.0
        self.cat_jump_active = False

        screen_geo = self.geometry()
        target_screen_x = int(screen_geo.left() + self.cat_current_x)
        target_screen_y = int(screen_geo.top() + self.cat_y)
        self.pet_window.move(target_screen_x, target_screen_y)

        self.lasers.clear()
        self.sparks.clear()
        self.floating_texts.clear()
        self.claw_slashes.clear()
        self.floating_texts.append(FloatingText(self.width() / 2, self.height() / 2 - 40, "GO! TANGKAP TITIK LASER! 🔴", QColor(255, 60, 90)))
        self.pet_window.set_state("idle")

    def on_game_over(self):
        """Triggered when 30s timer runs out."""
        self.game_state = "game_over"

        if self.score > self.high_score:
            self.high_score = self.score
            self.pet_window.settings["high_score_laser_hunter"] = self.high_score
            save_settings(self.pet_window.settings)

        if self.score >= 100:
            self.pet_window.set_state("celebrate", duration_seconds=4.0)
            raw_name = self.pet_window.settings.get("user_name", "").strip()
            user_name = f" {raw_name}" if raw_name else ""
            self.pet_window.say(f"Hebat banget sergapannya{user_name}! Semua laser ketangkep nya~ 🔴⭐", 4000)
        else:
            self.pet_window.set_state("idle")
            self.pet_window.say("Waktu habis nya! Capek tapi seru kejar laser 🐾🔴", 3500)

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
                self._attempt_space_pounce()
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
            # Clicking directly on any laser dot catches it with power bonus!
            for laser in self.lasers:
                if not laser.is_caught:
                    dist = math.hypot(laser.x - pos.x(), laser.y - pos.y())
                    if dist <= laser.radius * 1.6:
                        self._catch_laser(laser, power=True)
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
        self.draw_laser_hud(painter)

        if self.game_state == "tutorial":
            self._draw_tutorial_modal(painter)
            return

        # 2. Draw Active Laser Targets
        for laser in self.lasers:
            self._draw_laser_target(painter, laser)

        # 3. Draw Claw Slashes
        for cs in self.claw_slashes:
            self._draw_claw_slash(painter, cs)

        # 4. Draw Laser Sparks
        for p in self.sparks:
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
            hint = "🕹️ Gerakkan Mouse / [A][D]  •  [Spasi] untuk SERGAP LOMPAT  •  Klik Titik Laser  •  [Esc] Keluar"
            painter.drawText(QRect(0, self.height() - 32, self.width(), 22), Qt.AlignmentFlag.AlignCenter, hint)

        # 7. Draw Game Over Modal Card
        if self.game_state == "game_over":
            self._draw_game_over_modal(painter)

    def draw_laser_hud(self, painter: QPainter):
        """Draws top HUD for Laser Hunter."""
        hud_w = 640
        hud_h = 48
        hud_x = (self.width() - hud_w) // 2
        hud_y = 16

        self.close_btn_rect = QRect(hud_x + hud_w - 105, hud_y + 8, 95, 32)

        # Outer Neon Border
        painter.setPen(QPen(QColor(255, 45, 75, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 10, 10)

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 120, 140))
        painter.drawText(hud_x + 18, hud_y + 30, "🔴 LASER HUNTER")

        # Score
        painter.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(hud_x + 235, hud_y + 31, f"🏆 {self.score} PTS")

        # Timer
        secs = max(0, int(math.ceil(self.time_remaining)))
        t_col = QColor(255, 75, 75) if secs <= 5 else QColor(255, 235, 120)
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(t_col)
        painter.drawText(hud_x + 355, hud_y + 31, f"⏱️ {secs}s")

        # Combo
        c_col = QColor(255, 215, 40) if self.combo >= 5 else QColor(140, 255, 160)
        painter.setPen(c_col)
        painter.drawText(hud_x + 430, hud_y + 31, f"🔥 {self.combo}x COMBO")

        # Close Button
        btn_bg = QColor(220, 50, 60, 240) if self._close_hover else QColor(40, 42, 58, 220)
        btn_border = QColor(255, 140, 140) if self._close_hover else QColor(180, 190, 220, 180)
        painter.setPen(QPen(btn_border, 1.5))
        painter.setBrush(QBrush(btn_bg))
        painter.drawRoundedRect(self.close_btn_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.close_btn_rect, Qt.AlignmentFlag.AlignCenter, "✕ KELUAR")

    def _draw_laser_target(self, painter: QPainter, laser: LaserTarget):
        """Draws realistic high-intensity laser dot with glowing outer halos and core."""
        try:
            painter.save()
            painter.translate(laser.x, laser.y)

            pulse = 1.0 + 0.15 * math.sin(laser.pulse_phase)
            r = laser.radius * pulse

            # 1. Outer Diffuse Glow Halo
            painter.setPen(Qt.PenStyle.NoPen)
            glow_c = QColor(laser.color)
            glow_c.setAlpha(40)
            painter.setBrush(QBrush(glow_c))
            painter.drawEllipse(QRectF(-r * 2.2, -r * 2.2, r * 4.4, r * 4.4))

            # 2. Mid Neon Ring Pulse
            mid_c = QColor(laser.color)
            mid_c.setAlpha(95)
            painter.setBrush(QBrush(mid_c))
            painter.drawEllipse(QRectF(-r * 1.35, -r * 1.35, r * 2.7, r * 2.7))

            # 3. Main Saturated Color Core
            painter.setBrush(QBrush(laser.color))
            painter.drawEllipse(QRectF(-r * 0.85, -r * 0.85, r * 1.7, r * 1.7))

            # 4. Pure White Hot Center
            painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
            painter.drawEllipse(QRectF(-r * 0.42, -r * 0.42, r * 0.84, r * 0.84))

            # 5. Crosshair glints for Star / Gold
            if laser.target_type in ["gold_dash", "star_pulse"]:
                painter.setPen(QPen(QColor(255, 255, 255, 200), 1.5))
                painter.drawLine(QPointF(-r * 1.5, 0), QPointF(r * 1.5, 0))
                painter.drawLine(QPointF(0, -r * 1.5), QPointF(0, r * 1.5))

            painter.restore()
        except Exception:
            try:
                painter.restore()
            except Exception:
                pass

    def _draw_claw_slash(self, painter: QPainter, slash: ClawSlash):
        """Draws animated luminous red/white claw swipe arc."""
        try:
            painter.save()
            painter.translate(slash.x, slash.y)
            painter.scale(slash.scale, slash.scale)

            op = slash.opacity
            col_main = QColor(255, 60, 90, int(230 * op))
            col_glow = QColor(255, 255, 255, int(255 * op))

            # 3 Curved Claw Arcs
            painter.setPen(QPen(col_main, 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(QRectF(-40, -30, 36, 50), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(-18, -45, 36, 60), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(4, -30, 36, 50), 30 * 16, 120 * 16)

            # Bright Core Glint
            painter.setPen(QPen(col_glow, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(QRectF(-18, -45, 36, 60), 40 * 16, 100 * 16)

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
        painter.setPen(QPen(QColor(255, 45, 75, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 14, 14)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 120, 140))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "CARA BERMAIN: LASER HUNTER")

        # Subtitle
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(180, 200, 230))
        painter.drawText(QRect(card_x, card_y + 48, card_w, 20), Qt.AlignmentFlag.AlignCenter, "Bantu kucingmu menyergap titik-titik laser merah lincah!")

        # Target rules box
        box_y = card_y + 80

        # Row 1: Red Dot
        p_red = LaserTarget("red_dot", 100, 100)
        p_red.radius = 12.0
        p_red.x = card_x + 48
        p_red.y = box_y + 18
        self._draw_laser_target(painter, p_red)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 80, 100))
        painter.drawText(card_x + 82, box_y + 22, "Laser Merah")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 195, box_y + 22, "• Poin: +10 PTS  (Laser standar, lincah)")

        # Row 2: Gold Dash
        p_gold = LaserTarget("gold_dash", 100, 100)
        p_gold.radius = 12.0
        p_gold.x = card_x + 48
        p_gold.y = box_y + 58
        self._draw_laser_target(painter, p_gold)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 215, 40))
        painter.drawText(card_x + 82, box_y + 62, "Laser Kilat")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 195, box_y + 62, "• Poin: +30 PTS  (Gerak kilat & poin ekstra!)")

        # Row 3: Star Pulse
        p_star = LaserTarget("star_pulse", 100, 100)
        p_star.radius = 14.0
        p_star.x = card_x + 48
        p_star.y = box_y + 98
        self._draw_laser_target(painter, p_star)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor(120, 240, 255))
        painter.drawText(card_x + 82, box_y + 102, "Laser Bintang")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 240, 255))
        painter.drawText(card_x + 195, box_y + 102, "• Poin: +50 PTS  (Langka, bonus frenzy multiplier)")

        # Controls Section
        ctrl_y = box_y + 130
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(card_x + 40, ctrl_y, card_x + card_w - 40, ctrl_y)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 235, 120))
        painter.drawText(card_x + 45, ctrl_y + 25, "🎮 KONTROL:")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(220, 230, 245))
        painter.drawText(card_x + 150, ctrl_y + 25, "• Geser Mouse atau tombol [A][D] untuk mengejar laser.")
        painter.drawText(card_x + 150, ctrl_y + 45, "• Tekan [Spasi] atau Klik Titik Laser untuk SERGAP LOMPAT (HAP!).")
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

    def _draw_game_over_modal(self, painter: QPainter):
        """Draws retro game over result dialog."""
        card_w = 440
        card_h = 320
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2 - 20

        # Backdrop Shadow
        painter.setPen(QPen(QColor(255, 45, 75, 240), 2.5))
        painter.setBrush(QBrush(QColor(14, 16, 28, 245)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 12, 12)

        # Header Title
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 120, 140))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 32), Qt.AlignmentFlag.AlignCenter, "🏆 HASIL SERGAPAN LASER!")

        # Final Score & High Score
        painter.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        painter.setPen(QColor(100, 245, 255))
        painter.drawText(QRect(card_x, card_y + 58, card_w, 36), Qt.AlignmentFlag.AlignCenter, f"{self.score} PTS")

        if self.score >= self.high_score and self.score > 0:
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 215, 50))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, "🌟 REKOR SERGAP BARU! 🌟")
        else:
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor(180, 190, 210))
            painter.drawText(QRect(card_x, card_y + 96, card_w, 20), Qt.AlignmentFlag.AlignCenter, f"Rekor Tertinggi: {self.high_score} PTS")

        # Stats Breakdown
        p_stat_red = LaserTarget("red_dot", 100, 100)
        p_stat_red.x = card_x + 65
        p_stat_red.y = card_y + 140
        self._draw_laser_target(painter, p_stat_red)

        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(230, 235, 250))
        painter.drawText(card_x + 90, card_y + 145, "Laser Tertangkap:")
        total_caught = self.red_caught_count + self.gold_caught_count + self.star_caught_count
        painter.drawText(card_x + 290, card_y + 145, f"{total_caught} titik")

        p_stat_star = LaserTarget("star_pulse", 100, 100)
        p_stat_star.x = card_x + 65
        p_stat_star.y = card_y + 168
        self._draw_laser_target(painter, p_stat_star)

        painter.drawText(card_x + 90, card_y + 173, "Laser Bintang:")
        painter.drawText(card_x + 290, card_y + 173, f"{self.star_caught_count} titik")

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
