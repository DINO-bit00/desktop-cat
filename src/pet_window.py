"""
Main Desktop Pet Window — Comnyang Modern Physics & Interaction Engine
Transparent, draggable, animated floating companion with 60 FPS sub-pixel physics,
realtime 8-direction eye tracking, live mouse hunt pounce, mochi inertia wobble,
global keyboard kneading, overheat mode, paper unroll scroll reactions,
and fully customizable character scale (64px - 256px)!
"""

import os
import sys
import ctypes
import random
import time
import math
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import (
    QPixmap, QPainter, QCursor, QAction, QIcon, QFont, QColor, QImage, QTransform
)
from PyQt6.QtWidgets import (
    QWidget, QMenu, QInputDialog, QMessageBox, QApplication
)

from src.sprites import PALETTES, render_cat_frame
from src.speech_bubble import SpeechBubble
from src.pomodoro import PomodoroManager
from src.local_watcher import LocalWatcher
from src.global_hooks import GlobalInputWatcher
from src.settings import save_settings
from src.autostart import is_startup_enabled, set_startup_enabled


def set_win32_topmost(widget):
    """Enforce topmost z-order on Windows OS using native Win32 API."""
    if sys.platform == "win32" and widget:
        try:
            HWND_TOPMOST = -1
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            flags = SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            ctypes.windll.user32.SetWindowPos(int(widget.winId()), HWND_TOPMOST, 0, 0, 0, 0, flags)
        except Exception:
            pass


class DesktopPet(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        # Window configuration: Frameless, transparent, always-on-top, tool window
        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        if self.settings.get("stay_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setMouseTracking(True)

        # Customizable Pet Dimensions (Default: 128, range 48 to 256)
        self.sprite_size = int(self.settings.get("sprite_size", 128))
        self.setFixedSize(self.sprite_size, self.sprite_size)

        # Sub-pixel Float Coordinates
        self.pos_x_f = float(self.x())
        self.pos_y_f = float(self.y())

        # State Machine
        self.skin = self.settings.get("skin", "boss_oyen")
        self.state = "idle"
        self.pre_drag_state = "idle"
        self.frame_index = 0
        self.state_ticks = 0
        self.max_state_ticks = 180

        # Eye Follow Vectors
        self.look_dx = 0
        self.look_dy = 0

        # Movement & Mouse Hunting (Dynamic Live Target)
        self.is_hunting = False
        self.hunt_start_time = 0.0
        self.hunt_cooldown = 0.0

        # Mochi Drag & Inertia Wobble Physics
        self.is_dragging = False
        self.has_dragged = False
        self.drag_start_pos = QPoint()
        self.drag_start_global_pos = QPoint()
        self.drag_velocity_x = 0.0
        self.mochi_tilt = 0.0
        self.last_drag_global_pt = QPoint()
        self.last_drag_time = 0.0

        # Petting interaction tracking
        self._hover_pet_count = 0
        self._last_hover_time = 0.0

        # Scroll Reset Timer for Paper Unroll
        self.scroll_reset_timer = QTimer(self)
        self.scroll_reset_timer.setSingleShot(True)
        self.scroll_reset_timer.timeout.connect(self._on_scroll_timeout)
        self._scroll_delta_accum = 0.0

        # Stretch & Posture Centered Enlargement Mode
        self._is_stretch_mode = False
        self._pre_stretch_size = self.sprite_size
        self._pre_stretch_pos = (self.x(), self.y())
        self._stretch_end_timer = QTimer(self)
        self._stretch_end_timer.setSingleShot(True)
        self._stretch_end_timer.timeout.connect(self._end_stretch_mode)

        # Frame Pixmap Cache
        self.pixmap_cache = {}
        self._load_skin_sprites(self.skin)

        # Speech Bubble
        self.speech_bubble = SpeechBubble()

        # Pomodoro & Reminders
        self.pomodoro = PomodoroManager(self.settings)
        self.pomodoro.session_started.connect(self._on_pomodoro_start)
        self.pomodoro.session_finished.connect(self._on_pomodoro_finish)
        self.pomodoro.tick.connect(self._on_pomodoro_tick)
        self.pomodoro.reminder_triggered.connect(self._on_reminder)
        self.pomodoro.posture_reminder_triggered.connect(self._on_posture_reminder)

        # Local File Event Watcher
        self.watcher = LocalWatcher(self)
        self.watcher.event_received.connect(self._on_external_event)

        # Global Input Watcher (Comnyang-style reaction to typing, overheat, hunting, and scrolling)
        self.input_watcher = GlobalInputWatcher(self)
        self.input_watcher.typing_started.connect(self._on_global_typing_start)
        self.input_watcher.typing_stopped.connect(self._on_global_typing_stop)
        self.input_watcher.overheat_started.connect(self._on_global_overheat_start)
        self.input_watcher.overheat_ended.connect(self._on_global_overheat_end)
        self.input_watcher.mouse_scrolled.connect(self._on_global_scroll)
        self.input_watcher.mouse_moved_fast.connect(self._on_fast_mouse_move)
        self.input_watcher.start()

        # Animation Loop Timer (110ms per frame for smooth 9-10 FPS sprite cycling)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(110)

        # Physics & AI Behavior Timer (16ms = 60 FPS game loop)
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._update_physics_loop)
        self.physics_timer.start(16)

        # Position on screen
        self._snap_to_initial_position()

        # Say hello at startup
        QTimer.singleShot(600, self._say_welcome)

    # -------------------------------------------------------------
    # Sprite & Cache Management
    # -------------------------------------------------------------
    def _load_skin_sprites(self, skin_name):
        self.skin = skin_name
        self.pixmap_cache.clear()
        states = [
            "idle", "walk_left", "walk_right", "sleep", "work", "overheat",
            "paper_unroll", "pet", "stretch", "celebrate", "thinking", "drag", "land"
        ]

        for st in states:
            self.pixmap_cache[st] = []
            for frame in range(4):
                pil_img = render_cat_frame(skin_name, st, frame)
                raw_bytes = pil_img.tobytes("raw", "RGBA")
                qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimg)
                self.pixmap_cache[st].append(pixmap)

    def _get_current_pixmap(self):
        # Dynamic eye-follow look on idle
        if self.state == "idle" and not PALETTES.get(self.skin, {}).get("has_shades", False):
            pil_img = render_cat_frame(self.skin, "idle", self.frame_index, self.look_dx, self.look_dy)
            raw_bytes = pil_img.tobytes("raw", "RGBA")
            qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
            return QPixmap.fromImage(qimg)

        frames = self.pixmap_cache.get(self.state, self.pixmap_cache.get("idle", []))
        if not frames:
            return None
        return frames[self.frame_index % len(frames)]

    # -------------------------------------------------------------
    # Dynamic Size Scaling (48px - 256px)
    # -------------------------------------------------------------
    def set_sprite_size(self, new_size, show_dialogue=True):
        """Dynamically resize character while keeping pixel art crisp and centered."""
        new_size = max(48, min(256, int(new_size)))
        if new_size == self.sprite_size:
            return

        old_size = self.sprite_size
        self.sprite_size = new_size
        self.settings["sprite_size"] = new_size
        save_settings(self.settings)

        # Keep center position stable
        center_x = self.pos_x_f + old_size / 2.0
        center_y = self.pos_y_f + old_size / 2.0
        new_x = center_x - new_size / 2.0
        new_y = center_y - new_size / 2.0

        screen_geo = self._get_current_screen_geometry()
        self.pos_x_f = max(screen_geo.left(), min(new_x, screen_geo.right() - new_size))
        self.pos_y_f = max(screen_geo.top(), min(new_y, screen_geo.bottom() - new_size))

        self.setFixedSize(new_size, new_size)
        self.move(int(self.pos_x_f), int(self.pos_y_f))
        self._update_bubble_position()
        self.update()

        self._play_sound_blip(freq=1520, dur=40)
        if show_dialogue:
            self.say(f"Ukuran diubah: {new_size}px nya! ✨", 2000)

    def _get_head_rect(self):
        """Calculate scaled head hitbox for petting interaction."""
        s = self.sprite_size / 128.0
        return QRect(int(24 * s), int(10 * s), int(80 * s), int(62 * s))

    # -------------------------------------------------------------
    # Placement & Screen Geometry
    # -------------------------------------------------------------
    def _get_current_screen_geometry(self):
        screen = QApplication.screenAt(self.geometry().center())
        if not screen:
            screen = QApplication.primaryScreen()
        return screen.availableGeometry()

    def _snap_to_initial_position(self):
        screen_geo = self._get_current_screen_geometry()
        saved_x = self.settings.get("pos_x")
        saved_y = self.settings.get("pos_y")

        if saved_x is not None and saved_y is not None:
            x = max(screen_geo.left(), min(saved_x, screen_geo.right() - self.sprite_size))
            y = max(screen_geo.top(), min(saved_y, screen_geo.bottom() - self.sprite_size))
        else:
            x = screen_geo.right() - self.sprite_size - 60
            y = screen_geo.bottom() - self.sprite_size - 20

        self.move(x, y)
        self.pos_x_f = float(x)
        self.pos_y_f = float(y)
        self._update_bubble_position()

    def _update_bubble_position(self):
        if self.speech_bubble.isVisible():
            self.speech_bubble.update_position_relative_to(self.pos(), self.sprite_size)

    # -------------------------------------------------------------
    # State & Animation Controller
    # -------------------------------------------------------------
    def set_state(self, new_state, duration_seconds=None):
        if new_state == "walk":
            new_state = "walk_right"
        if new_state in self.pixmap_cache or new_state in ("hunt", "alert"):
            self.state = new_state
            self.frame_index = 0
            self.state_ticks = 0
            if duration_seconds:
                self.max_state_ticks = int(duration_seconds * 60)
            self.update()

    def _update_animation(self):
        self.frame_index = (self.frame_index + 1) % 4
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self.settings.get("stay_on_top", True):
            set_win32_topmost(self)

    # -------------------------------------------------------------
    # 60 FPS Game Loop & Advanced Physics (Dynamic Hunt & Eye Follow)
    # -------------------------------------------------------------
    def _update_physics_loop(self):
        if self.is_dragging:
            # Smooth inertia wobble physics (damped spring return)
            self.mochi_tilt += (self.drag_velocity_x * 0.45 - self.mochi_tilt) * 0.20
            self.drag_velocity_x *= 0.88
            self.update()
            return

        # Periodically ensure topmost if enabled
        if self.settings.get("stay_on_top", True) and random.random() < 0.015:
            set_win32_topmost(self)

        screen_geo = self._get_current_screen_geometry()
        cat_center_x = self.pos_x_f + self.sprite_size / 2.0
        cat_center_y = self.pos_y_f + self.sprite_size / 2.0

        # ── 1. DYNAMIC 8-DIRECTION EYE FOLLOW ──
        cursor_pos = QCursor.pos()
        dx = cursor_pos.x() - cat_center_x
        dy = cursor_pos.y() - (cat_center_y - (15 * (self.sprite_size / 128.0)))
        dist = math.hypot(dx, dy)

        if dist > (40 * (self.sprite_size / 128.0)):
            angle = math.degrees(math.atan2(dy, dx))
            if -22.5 <= angle < 22.5:
                self.look_dx, self.look_dy = 1, 0
            elif 22.5 <= angle < 67.5:
                self.look_dx, self.look_dy = 1, 1
            elif 67.5 <= angle < 112.5:
                self.look_dx, self.look_dy = 0, 1
            elif 112.5 <= angle < 157.5:
                self.look_dx, self.look_dy = -1, 1
            elif angle >= 157.5 or angle < -157.5:
                self.look_dx, self.look_dy = -1, 0
            elif -157.5 <= angle < -112.5:
                self.look_dx, self.look_dy = -1, -1
            elif -112.5 <= angle < -67.5:
                self.look_dx, self.look_dy = 0, -1
            elif -67.5 <= angle < -22.5:
                self.look_dx, self.look_dy = 1, -1
        else:
            self.look_dx, self.look_dy = 0, 0

        # ── 2. DYNAMIC LIVE MOUSE HUNTING PHYSICS ──
        if self.is_hunting:
            now = time.time()
            if now - self.hunt_start_time > 3.5:
                self.is_hunting = False
                self.set_state("idle")
                return

            target_x = cursor_pos.x() - self.sprite_size / 2.0
            target_y = cursor_pos.y() - self.sprite_size / 2.0
            h_dx = target_x - self.pos_x_f
            h_dy = target_y - self.pos_y_f
            h_dist = math.hypot(h_dx, h_dy)

            if h_dist <= (40.0 * (self.sprite_size / 128.0)):
                self.is_hunting = False
                self.set_state("land")
                self._play_sound_blip(freq=1450, dur=40)
                QTimer.singleShot(300, lambda: self.set_state("pet", duration_seconds=1.5))
                return

            speed = 5.2
            self.pos_x_f += (h_dx / h_dist) * speed
            self.pos_y_f += (h_dy / h_dist) * speed

            self.pos_x_f = max(screen_geo.left(), min(self.pos_x_f, screen_geo.right() - self.sprite_size))
            self.pos_y_f = max(screen_geo.top(), min(self.pos_y_f, screen_geo.bottom() - self.sprite_size))

            self.move(int(self.pos_x_f), int(self.pos_y_f))
            self._update_bubble_position()
            self.state = "walk_right" if h_dx > 0 else "walk_left"
            return

        # ── 3. TEMPORARY STATES TIMEOUT ──
        if self.state in ["celebrate", "thinking", "land", "stretch"]:
            self.state_ticks += 1
            if self.state_ticks > self.max_state_ticks:
                self.set_state("idle")
            return

        # ── REALTIME PET HEAD ZONE CHECK (Instant Stop When Cursor Leaves Head) ──
        if self.state == "pet":
            local_p = self.mapFromGlobal(QCursor.pos())
            head_rect = self._get_head_rect()
            if not self.rect().contains(local_p) or not head_rect.contains(local_p):
                self.set_state("idle")
            return

        # Do not wander if Pomodoro is active, typing/overheated, stretching, or rolling paper
        if not self.settings.get("wander_mode", True) or self.pomodoro.is_active or self.state in ["work", "overheat", "paper_unroll", "sleep", "stretch"]:
            return

        # ── 4. AUTONOMOUS WANDER LOGIC ──
        self.state_ticks += 1
        if self.state_ticks > self.max_state_ticks:
            self.state_ticks = 0
            choices = ["idle", "idle", "idle", "walk_left", "walk_right", "sleep"]
            new_action = random.choice(choices)
            if new_action == "sleep":
                self.max_state_ticks = random.randint(300, 600)
            elif "walk" in new_action:
                self.max_state_ticks = random.randint(100, 200)
            else:
                self.max_state_ticks = random.randint(120, 250)
            self.set_state(new_action)

        # Walk movements
        if self.state == "walk_left":
            self.pos_x_f -= 1.0
            if self.pos_x_f <= screen_geo.left():
                self.set_state("walk_right")
            else:
                self.move(int(self.pos_x_f), int(self.pos_y_f))
                self._update_bubble_position()
        elif self.state == "walk_right":
            self.pos_x_f += 1.0
            if self.pos_x_f >= screen_geo.right() - self.sprite_size:
                self.set_state("walk_left")
            else:
                self.move(int(self.pos_x_f), int(self.pos_y_f))
                self._update_bubble_position()

    # -------------------------------------------------------------
    # Global Input Reactions (Comnyang Phase 2 Features)
    # -------------------------------------------------------------
    def _on_global_typing_start(self):
        """User started typing -> cat begins keyboard kneading."""
        if self.state not in ["drag", "land", "pet", "overheat"]:
            self.is_hunting = False
            self.set_state("work")

    def _on_global_typing_stop(self):
        """User stopped typing -> return to idle."""
        if self.state in ["work", "overheat"]:
            self.set_state("idle")

    def _on_global_overheat_start(self):
        """Typing super fast -> Overheat mode with steam puffs!"""
        if self.state not in ["drag", "land", "pet"]:
            self.set_state("overheat")
            self._play_sound_blip(freq=1650, dur=55)
            if random.random() < 0.35:
                self.say("Ngebut banget ngetiknya, boss! 🔥🐾", 2500)

    def _on_global_overheat_end(self):
        """Typing slowed down -> cool back to normal kneading."""
        if self.state == "overheat":
            self.set_state("work")

    def _on_global_scroll(self, dx, dy):
        """
        Comnyang Feature #10: Paper Unroll!
        Spinning the paper roll with paws as user scrolls documents / pages.
        Wakes up the cat from sleep and responds to all scroll events.
        """
        if self.state not in ["drag", "pet"] and not self.pomodoro.is_active:
            if self.state != "paper_unroll":
                self.set_state("paper_unroll")
            # Advance frame dynamically on each scroll event
            self.frame_index = (self.frame_index + 1) % 4
            self.update()
            # Reset timer: return to idle immediately (400ms) after scrolling ceases
            self.scroll_reset_timer.start(400)

    def _on_scroll_timeout(self):
        """Scroll stopped -> return to idle."""
        self._scroll_delta_accum = 0.0
        if self.state == "paper_unroll":
            self.set_state("idle")

    def _on_fast_mouse_move(self, mouse_x, mouse_y):
        """Mouse Hunt & Pounce: Fast moving cursor excites the cat!"""
        if not self.settings.get("mouse_hunt_enabled", True):
            return

        now = time.time()
        if now - self.hunt_cooldown < 7.0:
            return
        if self.state in ["drag", "work", "overheat", "sleep"] or self.pomodoro.is_active or self.is_hunting:
            return

        cat_center_x = self.pos_x_f + self.sprite_size / 2.0
        cat_center_y = self.pos_y_f + self.sprite_size / 2.0
        dist = math.hypot(mouse_x - cat_center_x, mouse_y - cat_center_y)

        if (120 * (self.sprite_size / 128.0)) < dist < (550 * (self.sprite_size / 128.0)):
            self.hunt_cooldown = now
            self.hunt_start_time = now
            self.is_hunting = True
            self.say("Kejaaar nya! 🐾🎯", 1800)
            self._play_sound_blip(freq=1420, dur=35)

    # -------------------------------------------------------------
    # Paint & Render (Nearest-Neighbor Crisp Scaling + Mochi Tilt)
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        pixmap = self._get_current_pixmap()
        if not pixmap:
            return

        center = self.rect().center()

        if self.is_dragging:
            transform = QTransform()
            transform.translate(center.x(), center.y())
            clamped_tilt = max(-22.0, min(22.0, self.mochi_tilt))
            transform.rotate(clamped_tilt)
            transform.scale(0.92, 1.12)
            transform.translate(-center.x(), -center.y())
            painter.setTransform(transform)
            painter.drawPixmap(0, 0, self.sprite_size, self.sprite_size, pixmap)

        elif self.state == "land":
            w = int(self.sprite_size * 1.15)
            h = int(self.sprite_size * 0.85)
            ox = (self.sprite_size - w) // 2
            oy = self.sprite_size - h
            painter.drawPixmap(ox, oy, w, h, pixmap)

        else:
            painter.drawPixmap(0, 0, self.sprite_size, self.sprite_size, pixmap)

    # -------------------------------------------------------------
    # Mouse & Drag Interactions (Mochi Drag, Petting, & Ctrl+Wheel Zoom)
    # -------------------------------------------------------------
    def wheelEvent(self, event):
        """Ctrl + Wheel over cat to zoom in/out realtime."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.set_sprite_size(self.sprite_size + 12, show_dialogue=False)
            elif delta < 0:
                self.set_sprite_size(self.sprite_size - 12, show_dialogue=False)
            self.setToolTip(f"NyangBuddy Size: {self.sprite_size}px (Ctrl+Scroll)")
            event.accept()
        else:
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            global_pt = event.globalPosition().toPoint()
            now = time.time()
            dt = max(0.01, now - self.last_drag_time)

            vx = (global_pt.x() - self.last_drag_global_pt.x()) / dt
            self.drag_velocity_x = max(-35.0, min(35.0, vx * 0.06))

            self.last_drag_global_pt = global_pt
            self.last_drag_time = now

            move_dist = (global_pt - self.drag_start_global_pos).manhattanLength()
            if move_dist > 5:
                if not self.has_dragged:
                    self.has_dragged = True
                    self.set_state("drag")
                    self.anim_timer.setInterval(90)
                    self._play_sound_blip(freq=1350, dur=40)

            new_pos = global_pt - self.drag_start_pos
            screen_geo = self._get_current_screen_geometry()

            clamped_x = max(screen_geo.left() - 10, min(new_pos.x(), screen_geo.right() - self.sprite_size + 10))
            clamped_y = max(screen_geo.top() - 5, min(new_pos.y(), screen_geo.bottom() - self.sprite_size + 5))

            self.pos_x_f = float(clamped_x)
            self.pos_y_f = float(clamped_y)
            self.move(clamped_x, clamped_y)
            self._update_bubble_position()
            self.update()
            event.accept()
        else:
            # Petting / Pat-pat detection: only active directly on cat head!
            local_pos = event.position().toPoint()
            head_rect = self._get_head_rect()

            if head_rect.contains(local_pos):
                if self.state != "pet" and self.state not in ["drag", "land", "work", "overheat"]:
                    self.set_state("pet")
                    self._play_sound_blip(freq=1480, dur=35)
            else:
                if self.state == "pet":
                    self.set_state("idle")

    def leaveEvent(self, event):
        """Immediately stop petting as soon as cursor leaves the cat window."""
        super().leaveEvent(event)
        if self.state == "pet":
            self.set_state("idle")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.has_dragged = False
            self.is_hunting = False
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.drag_start_global_pos = event.globalPosition().toPoint()
            self.last_drag_global_pt = self.drag_start_global_pos
            self.last_drag_time = time.time()
            self.drag_velocity_x = 0.0
            self.mochi_tilt = 0.0
            self.pre_drag_state = self.state if self.state not in ["drag", "land"] else "idle"
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.mochi_tilt = 0.0
            self.anim_timer.setInterval(110)

            if self.has_dragged:
                self.settings["pos_x"] = int(self.pos_x_f)
                self.settings["pos_y"] = int(self.pos_y_f)
                save_settings(self.settings)

                # Landing squish bounce
                self.set_state("land")
                self._play_sound_blip(freq=950, dur=50)
                QTimer.singleShot(350, lambda: self.set_state("idle"))

                if random.random() < 0.35:
                    landing_quotes = [
                        "Duduk di sini ya nya~ 🐾",
                        "Spot baru yang nyaman nya! 😸",
                        "Siap mantau dari sini nya~ ✨",
                        "Tempat yang bagus nya! 📍"
                    ]
                    QTimer.singleShot(400, lambda: self.say(random.choice(landing_quotes), 3000))
            else:
                # Option A: Single left-click only speaks & plays sound without changing animation!
                self._on_pet_clicked()

            event.accept()

    # -------------------------------------------------------------
    # Dialogues & Responses
    # -------------------------------------------------------------
    def say(self, message, duration_ms=4500):
        self.speech_bubble.show_message(message, duration_ms)
        self._update_bubble_position()
        self._play_sound_blip()

    def _say_welcome(self):
        pet_name = PALETTES.get(self.skin, {}).get("name", "Nyang")
        self.say(f"Halo! Aku {pet_name} siap nemenin kamu kerja nya~ 🐾")

    def _on_pet_clicked(self):
        """Single left-click response: Shows dialogue and cute sound without changing animation."""
        if self.pomodoro.is_active and self.pomodoro.mode == "work":
            if self.skin == "boss_oyen":
                quotes = [
                    "Tetap fokus, boss. Jangan terdistraksi 😎",
                    "Gaskeun kodenya, boss! 💻🕶️",
                    "Beresin dulu tugasnya baru santai, boss! 🔥"
                ]
            elif self.skin == "mochi":
                quotes = [
                    "Semangat fokusnya nya! Aku temenin dari sini~ 🐾",
                    "Cakar mini siap nemenin ngetik kodenya nya! 👀",
                    "Kerja bagus nya! Sedikit lagi selesai~ ✨"
                ]
            else:
                quotes = [
                    "Fokus dulu ya nya! Semangat! 💪",
                    "Ngebut terus kodenya nya~ 🔥",
                    "Kerja bagus! Nanti kita istirahat bareng nya~ ✨"
                ]
            self.say(random.choice(quotes), 3000)
            return

        if self.skin == "boss_oyen":
            purrs = [
                "Kerja santai, hasil maksimal. Santai aja, boss 😎",
                "Kacamata hitam biar ga silau liat masa depan cerahmu 🕶️✨",
                "Gaya nomor satu, ngoding nomor dua, boss! 🐾",
                "Mew... Mau traktir snack apa hari ini, boss? 🍗",
                "Jangan lupa kopi hitamnya, boss ☕🕶️"
            ]
        elif self.skin == "mochi":
            purrs = [
                "Mew! Kalung biruku berkilau kan nya? 🐾",
                "Purrr... Senang banget ditemenin kamu nya! ❤️",
                "Chibi kitten siap nemenin kamu seharian nya! ✨",
                "Meow~! Jangan lupa istirahat kalau capek ya~ 🧘"
            ]
        else:
            purrs = [
                "Purrr... Senang ditemenin kamu nya~ ❤️",
                "Meooow~! Semangat ya hari ini! ✨",
                "Nyang~ Mau ditemenin ngoding apa santai nih? 😸",
                "Purrr purrr... Kucing senang, kerjaan lancar! 🐾",
                "Meow! Jangan lupa regangkan tanganmu ya~ 🧘"
            ]
        self.say(random.choice(purrs), 3500)

    def _play_sound_blip(self, freq=1200, dur=60):
        if not self.settings.get("sound_enabled", True):
            return
        try:
            import winsound
            winsound.Beep(int(freq), int(dur))
        except Exception:
            pass

    # -------------------------------------------------------------
    # Pomodoro & Reminder Handlers
    # -------------------------------------------------------------
    def _on_pomodoro_start(self, mode):
        if mode == "work":
            self.set_state("work")
            duration = self.settings.get("pomodoro_work_min", 25)
            self.say(f"Fokus mode aktif! ({duration} menit) Ayo selesaikan tugasnya nya~ 💻🔥", 4000)
        elif mode == "break":
            self.set_state("sleep")
            duration = self.settings.get("pomodoro_break_min", 5)
            self.say(f"Waktu istirahat ({duration} menit)! Rehat dulu ya nya~ ☕😴", 4000)

    def _on_pomodoro_finish(self, finished_mode):
        if finished_mode == "work":
            self.set_state("celebrate", duration_seconds=6)
            self.say("YAY! Sesi fokus selesai! Waktunya istirahat sejenak nya~ 🎉🥳", 6000)
        else:
            self.set_state("idle")
            self.say("Waktu istirahat selesai! Siap mulai lagi nya? 😺", 4500)

    def _on_pomodoro_tick(self, remaining, mode):
        mins = remaining // 60
        secs = remaining % 60
        title = "Fokus" if mode == "work" else "Break"
        self.setToolTip(f"NyangBuddy - {title} [{mins:02d}:{secs:02d}] (Ctrl+Scroll: Zoom)")

    def _on_reminder(self, text):
        self.say(text, 5000)

    # -------------------------------------------------------------
    # External Event (CLI / Watcher)
    # -------------------------------------------------------------
    def _on_external_event(self, data):
        state = data.get("state")
        message = data.get("message")
        duration = data.get("duration", 4)

        if state:
            self.set_state(state, duration_seconds=duration)
        if message:
            self.say(message, duration * 1000)

    # -------------------------------------------------------------
    # Context Menu
    # -------------------------------------------------------------
    def _show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #465a6e;
                margin: 4px 8px;
            }
        """)

        # 1. Skin Menu
        skin_menu = menu.addMenu("🐱 Ganti Karakter (Skin)")
        for skin_key, data in PALETTES.items():
            action = skin_menu.addAction(data["name"])
            action.setCheckable(True)
            action.setChecked(self.skin == skin_key)
            action.triggered.connect(lambda checked, k=skin_key: self._change_skin(k))

        # 2. Size / Scale Submenu
        size_menu = menu.addMenu("🔍 Ukuran Karakter (Size)")
        sizes = [
            ("🔎 Mini (64px)", 64),
            ("🐱 Sedang (96px)", 96),
            ("😺 Standar (128px - Default)", 128),
            ("🦁 Besar (160px)", 160),
            ("👑 Jumbo (192px)", 192)
        ]
        for label, sz in sizes:
            act = size_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(self.sprite_size == sz)
            act.triggered.connect(lambda checked, s=sz: self.set_sprite_size(s))

        size_menu.addSeparator()
        custom_size_act = size_menu.addAction("📐 Atur Ukuran Bebas (Custom)...")
        custom_size_act.triggered.connect(self._prompt_custom_size)

        menu.addSeparator()

        # 3. Pomodoro Submenu
        pom_menu = menu.addMenu("⏱️ Pomodoro Timer")
        if not self.pomodoro.is_active:
            start_25 = pom_menu.addAction("▶️ Mulai Fokus (25 Menit)")
            start_25.triggered.connect(lambda: self.pomodoro.start_focus(25))
            start_50 = pom_menu.addAction("▶️ Mulai Fokus (50 Menit)")
            start_50.triggered.connect(lambda: self.pomodoro.start_focus(50))
            start_break = pom_menu.addAction("☕ Mulai Break (5 Menit)")
            start_break.triggered.connect(lambda: self.pomodoro.start_break(5))
        else:
            stop_action = pom_menu.addAction(f"⏹️ Hentikan ({self.pomodoro.format_time()})")
            stop_action.triggered.connect(self.pomodoro.stop)

        # 4. Stretch & Posture Submenu
        stretch_menu = menu.addMenu("🧘 Pengingat Regang & Postur")
        now_act = stretch_menu.addAction("▶️ Regangkan Badan Sekarang (Layar Tengah)")
        now_act.triggered.connect(lambda: self.trigger_stretch(auto=False))
        stretch_menu.addSeparator()

        intervals = [
            ("⚡ 15 Menit (Tes Cepat)", 15),
            ("⏱️ 30 Menit", 30),
            ("⏱️ 45 Menit", 45),
            ("⏱️ 60 Menit (1 Jam - Standar)", 60),
            ("⏱️ 90 Menit (1.5 Jam)", 90),
            ("⏱️ 120 Menit (2 Jam)", 120),
        ]
        cur_int = self.settings.get("stretch_reminder_min", 60)
        is_enabled = self.settings.get("stretch_reminder_enabled", True)

        for label, mins in intervals:
            act = stretch_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(is_enabled and cur_int == mins)
            act.triggered.connect(lambda checked, m=mins: self.set_stretch_interval(m))

        stretch_menu.addSeparator()
        custom_act = stretch_menu.addAction("⏱️ Atur Waktu Kustom (Menit)...")
        custom_act.triggered.connect(self._prompt_stretch_interval)

        stretch_menu.addSeparator()
        toggle_act = stretch_menu.addAction("✅ Aktifkan Pengingat Otomatis")
        toggle_act.setCheckable(True)
        toggle_act.setChecked(is_enabled)
        toggle_act.triggered.connect(self._toggle_stretch_reminder)

        # 5. Actions / State Switch
        act_menu = menu.addMenu("🐾 Ganti Gaya / Aksi")
        act_menu.addAction("😺 Duduk Santai (Idle)", lambda: self.set_state("idle"))
        act_menu.addAction("💻 Mode Ngoding/Work", lambda: self.set_state("work"))
        act_menu.addAction("🔥 Mode Overheat (Steam)", lambda: self.set_state("overheat", 5))
        act_menu.addAction("📜 Gelar Kertas (Paper Unroll)", lambda: self.set_state("paper_unroll", 4))
        act_menu.addAction("😴 Tidur (Sleep)", lambda: self.set_state("sleep"))
        act_menu.addAction("🎉 Melompat Senang (Jump)", lambda: self.set_state("celebrate", 4))
        act_menu.addAction("🧘 Regangkan Badan (Stretch)", lambda: self.trigger_stretch(auto=False))
        act_menu.addAction("🤔 Berpikir (Thinking)", lambda: self.set_state("thinking", 4))
        act_menu.addAction("❤️ Dielus / Purring (Pet)", lambda: self.set_state("pet", 4))

        menu.addSeparator()

        # 6. Sticky Note / Pinned Focus
        note_action = menu.addAction("📌 Set Target Fokus / Note")
        note_action.triggered.connect(self._prompt_sticky_note)

        # 7. Options
        hunt_act = menu.addAction("🎯 Kejar Kursor Cepat (Mouse Hunt)")
        hunt_act.setCheckable(True)
        hunt_act.setChecked(self.settings.get("mouse_hunt_enabled", True))
        hunt_act.triggered.connect(self._toggle_mouse_hunt)

        wander_act = menu.addAction("🚶 Jalan Santai Sendiri (Auto Wander)")
        wander_act.setCheckable(True)
        wander_act.setChecked(self.settings.get("wander_mode", True))
        wander_act.triggered.connect(self._toggle_wander)

        ontop_act = menu.addAction("🔝 Selalu di Atas (Always on Top)")
        ontop_act.setCheckable(True)
        ontop_act.setChecked(self.settings.get("stay_on_top", True))
        ontop_act.triggered.connect(self._toggle_stay_on_top)

        sound_act = menu.addAction("🔔 Suara Blip Efek")
        sound_act.setCheckable(True)
        sound_act.setChecked(self.settings.get("sound_enabled", True))
        sound_act.triggered.connect(self._toggle_sound)

        startup_act = menu.addAction("🚀 Jalankan saat Startup (Auto-Start)")
        startup_act.setCheckable(True)
        startup_act.setChecked(is_startup_enabled())
        startup_act.triggered.connect(self._toggle_startup)

        menu.addSeparator()

        # 7. Quit
        quit_act = menu.addAction("❌ Keluar (Close)")
        quit_act.triggered.connect(self.close_app)

        menu.exec(global_pos)

    def _change_skin(self, skin_key):
        self._load_skin_sprites(skin_key)
        self.settings["skin"] = skin_key
        save_settings(self.settings)
        self.update()
        if skin_key == "boss_oyen":
            self.say("Boss Oyen siap mengawal produktivitasmu, boss! 😎🕶️")
        elif skin_key == "mochi":
            self.say("Mochi si kalung biru siap nemenin kamu nya! 🐾✨")
        else:
            pet_name = PALETTES[skin_key]["name"]
            self.say(f"Ganti kostum ke {pet_name} nya! 🐾")

    def _prompt_custom_size(self):
        val, ok = QInputDialog.getInt(
            self, "Ukuran Karakter Kustom", "Masukkan ukuran pixel karakter (48 - 256 px):",
            value=self.sprite_size, min=48, max=256, step=8
        )
        if ok:
            self.set_sprite_size(val)

    def _toggle_mouse_hunt(self, checked):
        self.settings["mouse_hunt_enabled"] = checked
        save_settings(self.settings)
        if not checked:
            self.is_hunting = False

    def _toggle_wander(self, checked):
        self.settings["wander_mode"] = checked
        save_settings(self.settings)
        if not checked:
            self.set_state("idle")

    def _toggle_stay_on_top(self, checked):
        self.settings["stay_on_top"] = checked
        save_settings(self.settings)
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        if checked:
            set_win32_topmost(self)

    def _toggle_sound(self, checked):
        self.settings["sound_enabled"] = checked
        save_settings(self.settings)

    def _toggle_startup(self, checked):
        success = set_startup_enabled(checked)
        if success:
            self.settings["run_on_startup"] = checked
            save_settings(self.settings)
            if checked:
                self.say("NyangBuddy sekarang otomatis nemenin kamu tiap laptop nyala nya! 🚀🐾", 4000)
            else:
                self.say("Auto-startup dinonaktifkan nya! 🐾", 3000)
        else:
            self.say("Gagal mengubah pengaturan startup nya! 😿", 3000)

    def _toggle_stretch_reminder(self, checked):
        self.settings["stretch_reminder_enabled"] = checked
        save_settings(self.settings)
        self.pomodoro.start_health_timers()
        cur_min = self.settings.get("stretch_reminder_min", 60)
        if checked:
            self.say(f"Pengingat postur aktif! Aku ingatkan tiap {cur_min} menit ya nya~ 🧘", 3500)
        else:
            self.say("Pengingat postur dinonaktifkan nya! 🐾", 3000)

    def _prompt_stretch_interval(self):
        cur_min = self.settings.get("stretch_reminder_min", 60)
        val, ok = QInputDialog.getInt(
            self, "Timer Pengingat Peregangan",
            "Masukkan interval pengingat regang badan (dalam menit):\nContoh: 15 untuk tes cepat, 45 atau 60 untuk kerja normal.",
            value=cur_min, min=1, max=300, step=5
        )
        if ok and val > 0:
            self.set_stretch_interval(val)

    def set_stretch_interval(self, minutes):
        self.settings["stretch_reminder_min"] = minutes
        self.settings["stretch_reminder_enabled"] = True
        save_settings(self.settings)
        self.pomodoro.start_health_timers()
        self.say(f"Timer regang badan diatur ke tiap {minutes} menit nya! ⏱️🧘", 4000)

    def _on_posture_reminder(self):
        """Triggered periodically when user has been working continuously."""
        self.trigger_stretch(auto=True)

    def trigger_stretch(self, auto=False):
        """
        Executes the kawaii cat stretch yoga posture.
        Automatically enlarges character and glides to screen center!
        """
        if self.state in ["drag", "pet"]:
            return

        if not self._is_stretch_mode:
            self._is_stretch_mode = True
            self._pre_stretch_size = self.sprite_size
            self._pre_stretch_pos = (self.x(), self.y())

            # Enlarge to prominent size (1.6x of normal or min 200px)
            target_size = max(200, int(self.sprite_size * 1.6))
            screen_geo = self._get_current_screen_geometry()
            center_x = screen_geo.center().x() - target_size // 2
            center_y = screen_geo.center().y() - target_size // 2

            self.set_sprite_size(target_size, show_dialogue=False)
            self.move(center_x, center_y)
            self.pos_x_f = float(center_x)
            self.pos_y_f = float(center_y)
            set_win32_topmost(self)

        self.set_state("stretch", duration_seconds=7.0)
        self._play_sound_blip(freq=1250, dur=70)
        QTimer.singleShot(120, lambda: self._play_sound_blip(freq=1650, dur=90))

        if auto:
            msg = random.choice([
                "Waktunya istirahat sejenak! 🧘✨\nYuk berdiri dan regangkan badan bareng aku!",
                "Udah duduk lama nih, boss! 🧘🐾\nLuruskan punggung & tarik nafas dalam-dalam ya!",
                "Saatnya peregangan otot! 🌸🐾\nRegangkan badan biar tetap bugar & fokus!"
            ])
            self.say(msg, 6500)
        else:
            self.say("Ngulet dulu nyaaa~ segernya badan! 🧘✨\nYuk luruskan punggung bareng aku!", 5500)

        # Automatically restore size and return to original position after 7 seconds
        self._stretch_end_timer.start(7000)

    def _end_stretch_mode(self):
        """Restores size and returns to previous desktop position after stretch ends."""
        if self._is_stretch_mode:
            self._is_stretch_mode = False
            # Restore original scale
            self.set_sprite_size(self._pre_stretch_size, show_dialogue=False)
            # Restore original position
            orig_x, orig_y = self._pre_stretch_pos
            self.move(orig_x, orig_y)
            self.pos_x_f = float(orig_x)
            self.pos_y_f = float(orig_y)
            self.set_state("idle")
            self.say("Segernya! Lanjut fokus kerja lagi ya nya~ 🐾💪", 3500)

    def _prompt_sticky_note(self):
        current_note = self.settings.get("sticky_note", "")
        text, ok = QInputDialog.getText(
            self, "Target Fokus / Catatan", "Tulis fokus kerjamu sekarang nya:", text=current_note
        )
        if ok and text:
            self.settings["sticky_note"] = text
            save_settings(self.settings)
            self.say(f"Target: \"{text}\" - Aku pantau terus ya nya! 🎯", 6000)

    def close_app(self):
        self.input_watcher.stop()
        self.speech_bubble.close()
        self.close()
        QApplication.quit()
