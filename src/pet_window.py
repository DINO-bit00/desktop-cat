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
from src.pomodoro_badge import PomodoroBadge


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

            # Set WS_EX_TOPMOST extended style for bulletproof topmost
            GWL_EXSTYLE = -20
            WS_EX_TOPMOST = 0x00000008
            cur_ex = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if not (cur_ex & WS_EX_TOPMOST):
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur_ex | WS_EX_TOPMOST)

            ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, flags)
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

        # Unified Center-Stage Reminder Manager (Prevents state collision & guarantees 100% accurate home restoration)
        self._active_reminder_type = None  # None, "stretch", "drink_water", etc.
        self._reminder_queue = []          # Sequential combo queue: [(type, auto, duration), ...]
        self._was_combo = False
        self._home_size = self.sprite_size
        self._home_pos = (self.x(), self.y())
        self._reminder_end_timer = QTimer(self)
        self._reminder_end_timer.setSingleShot(True)
        self._reminder_end_timer.timeout.connect(self._end_centered_reminder)

        # Smooth 60 FPS Glide & Scale Interpolation Controller
        self._glide_timer = QTimer(self)
        self._glide_timer.timeout.connect(self._on_glide_tick)
        self._glide_start_time = 0.0
        self._glide_duration = 0.55
        self._glide_from = (0.0, 0.0, 128)
        self._glide_to = (0.0, 0.0, 128)
        self._glide_callback = None

        # Frame Pixmap Cache & Idle Eye-Follow Pre-Cache (Zero runtime memory allocation)
        self.pixmap_cache = {}
        self.idle_eye_cache = {}
        self._cached_screen_geo = None
        self._last_screen_geo_time = 0.0
        self._last_cursor_pos = QPoint(0, 0)
        self._last_cursor_poll_time = time.time()
        self._sprites_ready = False

        # Load ONLY the essential idle + walk sprites synchronously (instant startup)
        self._load_essential_sprites(self.skin)

        # Speech Bubble
        self.speech_bubble = SpeechBubble()

        # Floating Pomodoro Countdown Badge (Pixel Art Mini UI)
        self.pomodoro_badge = PomodoroBadge()
        self.pomodoro_badge.clicked.connect(self._on_pomodoro_badge_clicked)

        # Pomodoro & Reminders
        self.pomodoro = PomodoroManager(self.settings)
        self.pomodoro.session_started.connect(self._on_pomodoro_start)
        self.pomodoro.session_finished.connect(self._on_pomodoro_finish)
        self.pomodoro.tick.connect(self._on_pomodoro_tick)
        self.pomodoro.reminder_triggered.connect(self._on_reminder)
        self.pomodoro.posture_reminder_triggered.connect(self._on_posture_reminder)
        self.pomodoro.hydration_reminder_triggered.connect(self._on_hydration_reminder)

        # Local File Event Watcher
        self.watcher = LocalWatcher(self)
        self.watcher.event_received.connect(self._on_external_event)

        # Global Input Watcher (Comnyang-style cadence reaction to typing, overheat, and scrolling)
        self.input_watcher = GlobalInputWatcher(self)
        self.input_watcher.typing_started.connect(self._on_global_typing_start)
        self.input_watcher.typing_stopped.connect(self._on_global_typing_stop)
        self.input_watcher.overheat_started.connect(self._on_global_overheat_start)
        self.input_watcher.overheat_ended.connect(self._on_global_overheat_end)
        self.input_watcher.mouse_scrolled.connect(self._on_global_scroll)

        # Animation Loop Timer (110ms per frame for smooth 9-10 FPS sprite cycling)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(110)

        # Physics & AI Behavior Timer (16ms = 60 FPS game loop)
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._update_physics_loop)
        self.physics_timer.start(16)

        # Aggressive Always-On-Top Enforcement Timer (every 3 seconds)
        self._topmost_timer = QTimer(self)
        self._topmost_timer.timeout.connect(self._enforce_topmost)
        if self.settings.get("stay_on_top", True):
            self._topmost_timer.start(3000)

        # Position on screen
        self._snap_to_initial_position()

        # Defer heavy sprite pre-cache & input hooks to AFTER the window is visible (non-blocking startup)
        QTimer.singleShot(50, self._deferred_startup)

    def _deferred_startup(self):
        """Runs after the window is visible — loads remaining sprites and starts input hooks."""
        # Start input watcher (pynput hooks) AFTER window is shown
        self.input_watcher.start()

        # Pre-cache all remaining sprites in batches (non-blocking via singleShot chain)
        self._deferred_load_remaining_sprites(self.skin)

        # Say hello
        QTimer.singleShot(400, self._say_welcome)

    def _enforce_topmost(self):
        """Aggressively re-enforces topmost z-order using Win32 extended window styles."""
        if self.settings.get("stay_on_top", True):
            set_win32_topmost(self)

    # -------------------------------------------------------------
    # Sprite & Cache Management (Pre-cached for instant 60 FPS O(1) rendering)
    # -------------------------------------------------------------
    def _render_state_frames(self, skin_name, state):
        """Renders 4 frames for a given state and stores them in pixmap_cache."""
        self.pixmap_cache[state] = []
        for frame in range(4):
            pil_img = render_cat_frame(skin_name, state, frame)
            raw_bytes = pil_img.tobytes("raw", "RGBA")
            qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
            self.pixmap_cache[state].append(QPixmap.fromImage(qimg))

    def _load_essential_sprites(self, skin_name):
        """Loads only idle + walk sprites synchronously for instant window display (<80ms)."""
        self.skin = skin_name
        self.pixmap_cache.clear()
        self.idle_eye_cache.clear()
        self._sprites_ready = False
        for st in ("idle", "walk_left", "walk_right", "celebrate"):
            self._render_state_frames(skin_name, st)

    def _deferred_load_remaining_sprites(self, skin_name):
        """Loads remaining state sprites + idle eye cache in small batches via QTimer chain."""
        remaining = [
            "sleep", "work", "overheat", "paper_unroll", "pet",
            "stretch", "drink_water", "thinking", "drag", "land"
        ]
        self._deferred_batch_queue = list(remaining)
        self._deferred_skin = skin_name
        self._process_next_sprite_batch()

    def _process_next_sprite_batch(self):
        """Processes 2 states per tick to avoid blocking the UI thread."""
        for _ in range(2):
            if not self._deferred_batch_queue:
                break
            st = self._deferred_batch_queue.pop(0)
            self._render_state_frames(self._deferred_skin, st)

        if self._deferred_batch_queue:
            QTimer.singleShot(16, self._process_next_sprite_batch)
        else:
            # All states loaded — now pre-cache idle eye directions
            self._deferred_load_idle_eyes()

    def _deferred_load_idle_eyes(self):
        """Pre-caches all 36 idle eye-direction frames for O(1) runtime lookup."""
        for frame in range(4):
            for ldx in (-1, 0, 1):
                for ldy in (-1, 0, 1):
                    pil_img = render_cat_frame(self._deferred_skin, "idle", frame, ldx, ldy)
                    raw_bytes = pil_img.tobytes("raw", "RGBA")
                    qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
                    self.idle_eye_cache[(frame, ldx, ldy)] = QPixmap.fromImage(qimg)
        self._sprites_ready = True

    def _load_skin_sprites(self, skin_name):
        """Full synchronous load (used by skin switcher in context menu)."""
        self._load_essential_sprites(skin_name)
        remaining = [
            "sleep", "work", "overheat", "paper_unroll", "pet",
            "stretch", "drink_water", "thinking", "drag", "land"
        ]
        for st in remaining:
            self._render_state_frames(skin_name, st)
        for frame in range(4):
            for ldx in (-1, 0, 1):
                for ldy in (-1, 0, 1):
                    pil_img = render_cat_frame(skin_name, "idle", frame, ldx, ldy)
                    raw_bytes = pil_img.tobytes("raw", "RGBA")
                    qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
                    self.idle_eye_cache[(frame, ldx, ldy)] = QPixmap.fromImage(qimg)
        self._sprites_ready = True

    def _get_current_pixmap(self):
        # O(1) dictionary lookup — zero allocation at runtime
        if self.state == "idle":
            cached = self.idle_eye_cache.get((self.frame_index % 4, self.look_dx, self.look_dy))
            if cached:
                return cached

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
    # Placement & Screen Geometry (Cached to eliminate Win32 display query churn)
    # -------------------------------------------------------------
    def _get_current_screen_geometry(self, force_refresh=False):
        now = time.time()
        if force_refresh or self._cached_screen_geo is None or (now - self._last_screen_geo_time > 2.5):
            screen = QApplication.screenAt(self.geometry().center())
            if not screen:
                screen = QApplication.primaryScreen()
            self._cached_screen_geo = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
            self._last_screen_geo_time = now
        return self._cached_screen_geo

    def _snap_to_initial_position(self):
        screen_geo = self._get_current_screen_geometry(force_refresh=True)
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
        if self.pomodoro_badge.isVisible():
            self.pomodoro_badge.update_position_relative_to(self.pos(), self.sprite_size)

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
    @property
    def is_reminder_locked(self) -> bool:
        """
        Returns True if the cat is executing a centered ergonomic reminder sequence
        (Stretch, Posture, Hydration, Break) or gliding across the screen.
        Completely blocks typing, scrolling, hunting, and auto-wandering to avoid animation clashes.
        """
        return (
            self._active_reminder_type is not None
            or self._glide_timer.isActive()
            or self.state in ["stretch", "drink_water"]
        )

    def _update_physics_loop(self):
        if self.is_reminder_locked:
            return

        if self.is_dragging:
            # Smooth inertia wobble physics (damped spring return)
            self.mochi_tilt += (self.drag_velocity_x * 0.45 - self.mochi_tilt) * 0.20
            self.drag_velocity_x *= 0.88
            self.update()
            return


        screen_geo = self._get_current_screen_geometry()
        cat_center_x = self.pos_x_f + self.sprite_size / 2.0
        cat_center_y = self.pos_y_f + self.sprite_size / 2.0

        # ── 1. DYNAMIC 8-DIRECTION EYE FOLLOW & FLICK DETECTION ──
        cursor_pos = QCursor.pos()
        dx = cursor_pos.x() - cat_center_x
        dy = cursor_pos.y() - (cat_center_y - (15 * (self.sprite_size / 128.0)))
        dist = math.hypot(dx, dy)

        # Internal zero-overhead fast mouse flick check
        now = time.time()
        dt_c = now - self._last_cursor_poll_time
        if dt_c > 0.03:
            c_dx = cursor_pos.x() - self._last_cursor_pos.x()
            c_dy = cursor_pos.y() - self._last_cursor_pos.y()
            c_spd = math.hypot(c_dx, c_dy) / dt_c
            if c_spd > 1100 and self.settings.get("mouse_hunt_enabled", False):
                self._on_fast_mouse_move(cursor_pos.x(), cursor_pos.y())
            self._last_cursor_pos = cursor_pos
            self._last_cursor_poll_time = now

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
        if self.state in ["celebrate", "thinking", "land", "stretch", "drink_water"]:
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

        # Do not wander if Pomodoro is active, typing/overheated, stretching, drinking water, or rolling paper
        if not self.settings.get("wander_mode", True) or self.pomodoro.is_active or self.state in ["work", "overheat", "paper_unroll", "sleep", "stretch", "drink_water"]:
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
        if self.is_reminder_locked:
            return
        if self.state not in ["drag", "land", "pet", "overheat"]:
            self.is_hunting = False
            self.set_state("work")

    def _on_global_typing_stop(self):
        """User stopped typing -> return to idle."""
        if self.is_reminder_locked:
            return
        if self.state in ["work", "overheat"]:
            self.set_state("idle")

    def _on_global_overheat_start(self):
        """Typing super fast -> Overheat mode with steam puffs!"""
        if self.is_reminder_locked:
            return
        if self.state not in ["drag", "land", "pet"]:
            self.set_state("overheat")
            self._play_sound_blip(freq=1650, dur=55)
            if random.random() < 0.35:
                self.say("Ngebut banget ngetiknya, boss! 🔥🐾", 2500)

    def _on_global_overheat_end(self):
        """Typing slowed down -> cool back to normal kneading."""
        if self.is_reminder_locked:
            return
        if self.state == "overheat":
            self.set_state("work")

    def _on_global_scroll(self, dx, dy):
        """
        Comnyang Feature #10: Paper Unroll!
        Spinning the paper roll with paws as user scrolls documents / pages.
        Wakes up the cat from sleep and responds to all scroll events.
        """
        if self.is_reminder_locked or self.pomodoro.is_active:
            return
        if self.state not in ["drag", "pet"]:
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
        if self.is_reminder_locked or not self.settings.get("mouse_hunt_enabled", True):
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
        if self._glide_timer.isActive():
            event.accept()
            return

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
            if self.is_reminder_locked:
                event.accept()
                return

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
        if self._glide_timer.isActive():
            event.accept()
            return

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
            total_secs = duration * 60
            self.say(f"Fokus mode aktif! ({duration} menit) Ayo selesaikan tugasnya nya~ 💻🔥", 4000)
        elif mode == "break":
            self.set_state("sleep")
            duration = self.settings.get("pomodoro_break_min", 5)
            total_secs = duration * 60
            self.say(f"Waktu istirahat ({duration} menit)! Rehat dulu ya nya~ ☕😴", 4000)
        else:
            return

        # Show floating pomodoro badge
        self.pomodoro_badge.start(mode, total_secs)
        self.pomodoro_badge.update_position_relative_to(self.pos(), self.sprite_size)

    def _on_pomodoro_finish(self, finished_mode):
        # Hide floating pomodoro badge
        self.pomodoro_badge.stop()

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

        # Update floating badge countdown & progress bar
        self.pomodoro_badge.update_tick(remaining)

    def _on_pomodoro_badge_clicked(self):
        """User clicked the floating pomodoro badge to stop the session."""
        self.pomodoro.stop()
        self.pomodoro_badge.stop()
        self.set_state("idle")
        self.say("Sesi Pomodoro dihentikan nya~ 🐾", 3000)

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
            stop_action.triggered.connect(self._on_pomodoro_badge_clicked)

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
        combo_act1 = stretch_menu.addAction("🌟 Rutinitas Lengkap (Regang + Minum)")
        combo_act1.triggered.connect(self.trigger_combo_routine)
        stretch_menu.addSeparator()
        toggle_act = stretch_menu.addAction("✅ Aktifkan Pengingat Otomatis")
        toggle_act.setCheckable(True)
        toggle_act.setChecked(is_enabled)
        toggle_act.triggered.connect(self._toggle_stretch_reminder)

        # 5. Hydration / Drink Water Submenu
        hyd_menu = menu.addMenu("💧 Pengingat Minum Air (Hydration)")
        hyd_now_act = hyd_menu.addAction("▶️ Minum Air Sekarang (Layar Tengah)")
        hyd_now_act.triggered.connect(lambda: self.trigger_drink_water(auto=False))
        hyd_menu.addSeparator()

        hyd_intervals = [
            ("⚡ 15 Menit (Tes Cepat)", 15),
            ("⏱️ 30 Menit", 30),
            ("⏱️ 45 Menit (Standar)", 45),
            ("⏱️ 60 Menit (1 Jam)", 60),
            ("⏱️ 90 Menit (1.5 Jam)", 90),
            ("⏱️ 120 Menit (2 Jam)", 120),
        ]
        cur_hyd = self.settings.get("hydration_reminder_min", 45)
        hyd_enabled = self.settings.get("hydration_reminder_enabled", True)

        for label, mins in hyd_intervals:
            act = hyd_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(hyd_enabled and cur_hyd == mins)
            act.triggered.connect(lambda checked, m=mins: self.set_hydration_interval(m))

        hyd_menu.addSeparator()
        custom_hyd_act = hyd_menu.addAction("⏱️ Atur Waktu Kustom (Menit)...")
        custom_hyd_act.triggered.connect(self._prompt_hydration_interval)

        hyd_menu.addSeparator()
        combo_act2 = hyd_menu.addAction("🌟 Rutinitas Lengkap (Regang + Minum)")
        combo_act2.triggered.connect(self.trigger_combo_routine)
        hyd_menu.addSeparator()
        toggle_hyd_act = hyd_menu.addAction("✅ Aktifkan Pengingat Otomatis")
        toggle_hyd_act.setCheckable(True)
        toggle_hyd_act.setChecked(hyd_enabled)
        toggle_hyd_act.triggered.connect(self._toggle_hydration_reminder)

        # 6. Actions / State Switch
        act_menu = menu.addMenu("🐾 Ganti Gaya / Aksi")
        act_menu.addAction("😺 Duduk Santai (Idle)", lambda: self.set_state("idle"))
        act_menu.addAction("💻 Mode Ngoding/Work", lambda: self.set_state("work"))
        act_menu.addAction("🔥 Mode Overheat (Steam)", lambda: self.set_state("overheat", 5))
        act_menu.addAction("📜 Gelar Kertas (Paper Unroll)", lambda: self.set_state("paper_unroll", 4))
        act_menu.addAction("😴 Tidur (Sleep)", lambda: self.set_state("sleep"))
        act_menu.addAction("🎉 Melompat Senang (Jump)", lambda: self.set_state("celebrate", 4))
        act_menu.addAction("🧘 Regangkan Badan (Stretch)", lambda: self.trigger_stretch(auto=False))
        act_menu.addAction("💧 Minum Air (Drink Water)", lambda: self.trigger_drink_water(auto=False))
        act_menu.addAction("🌟 Paket Sehat (Regang + Minum)", self.trigger_combo_routine)
        act_menu.addAction("🤔 Berpikir (Thinking)", lambda: self.set_state("thinking", 4))
        act_menu.addAction("❤️ Dielus / Purring (Pet)", lambda: self.set_state("pet", 4))

        menu.addSeparator()

        # 7. Sticky Note / Pinned Focus
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
            self._topmost_timer.start(3000)
        else:
            self._topmost_timer.stop()
            # Actively remove topmost using HWND_NOTOPMOST
            if sys.platform == "win32":
                try:
                    HWND_NOTOPMOST = -2
                    SWP_NOSIZE = 0x0001
                    SWP_NOMOVE = 0x0002
                    SWP_NOACTIVATE = 0x0010
                    ctypes.windll.user32.SetWindowPos(
                        int(self.winId()), HWND_NOTOPMOST, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
                    )
                except Exception:
                    pass

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

    def _start_smooth_glide(self, target_x, target_y, target_size, duration=0.55, on_complete=None):
        """Smooth 60 FPS cubic ease-in-out movement and scaling interpolation."""
        self._glide_from = (float(self.x()), float(self.y()), self.sprite_size)
        self._glide_to = (float(target_x), float(target_y), int(target_size))
        self._glide_start_time = time.time()
        self._glide_duration = duration
        self._glide_callback = on_complete
        self._glide_timer.start(16)

    def _on_glide_tick(self):
        now = time.time()
        elapsed = now - self._glide_start_time
        t = min(1.0, elapsed / self._glide_duration)

        # Cubic Ease-In-Out S-Curve: smooth acceleration & smooth deceleration
        ease = 4 * t * t * t if t < 0.5 else 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0

        fx, fy, fsize = self._glide_from
        tx, ty, tsize = self._glide_to

        cur_x = int(fx + (tx - fx) * ease)
        cur_y = int(fy + (ty - fy) * ease)
        cur_size = int(fsize + (tsize - fsize) * ease)

        if cur_size != self.sprite_size:
            self.set_sprite_size(cur_size, show_dialogue=False)

        self.move(cur_x, cur_y)
        self.pos_x_f = float(cur_x)
        self.pos_y_f = float(cur_y)
        self._update_bubble_position()

        if t >= 1.0:
            self._glide_timer.stop()
            if self._glide_callback:
                cb = self._glide_callback
                self._glide_callback = None
                cb()

    def _start_centered_reminder(self, reminder_type: str, auto: bool = False, duration: float = 7.0, queue_next: list = None):
        """
        Unified Center-Stage Reminder & Sequential Combo Manager (Option A).
        If another reminder arrives while already centered or gliding, it queues seamlessly as the next routine step!
        Guarantees that home coordinates and original size are NEVER overwritten while centered.
        """
        # If already centered or currently gliding to center, queue this reminder as the next routine step!
        if self._active_reminder_type is not None:
            if reminder_type not in [item[0] for item in self._reminder_queue] and reminder_type != self._active_reminder_type:
                self._reminder_queue.append((reminder_type, auto, duration))
            return

        if self.state in ["drag", "pet"]:
            return

        # Capture true desktop home location ONLY when departing from desktop
        self._active_reminder_type = reminder_type
        self._reminder_queue = list(queue_next) if queue_next else []
        self._was_combo = len(self._reminder_queue) > 0
        self._home_size = self.sprite_size
        self._home_pos = (self.x(), self.y())

        target_size = max(200, int(self._home_size * 1.6))
        screen_geo = self._get_current_screen_geometry()
        center_x = screen_geo.center().x() - target_size // 2
        center_y = screen_geo.center().y() - target_size // 2

        self.set_state("celebrate", duration_seconds=1.0)
        set_win32_topmost(self)

        def on_center_arrived():
            self._execute_reminder_step(reminder_type, auto, duration)

        self._start_smooth_glide(center_x, center_y, target_size, duration=0.55, on_complete=on_center_arrived)

    def _execute_reminder_step(self, reminder_type: str, auto: bool, duration: float):
        """Executes one step in the health routine."""
        self._active_reminder_type = reminder_type
        self.set_state(reminder_type, duration_seconds=duration)

        has_queued = len(self._reminder_queue) > 0

        if reminder_type == "stretch":
            self._play_sound_blip(freq=1250, dur=70)
            QTimer.singleShot(140, lambda: self._play_sound_blip(freq=1650, dur=90))
            if has_queued:
                self.say("Sesi Istirahat Sehat Terpadu! 🧘✨\nYuk regangkan badan dulu, habis ini kita minum air putih ya!", int(duration * 1000 - 500))
            elif auto:
                msg = random.choice([
                    "Waktunya istirahat sejenak! 🧘✨\nYuk berdiri dan regangkan badan bareng aku!",
                    "Udah duduk lama nih, boss! 🧘🐾\nLuruskan punggung & tarik nafas dalam-dalam ya!",
                    "Saatnya peregangan otot! 🌸🐾\nRegangkan badan biar tetap bugar & fokus!"
                ])
                self.say(msg, int(duration * 1000 - 500))
            else:
                self.say("Ngulet dulu nyaaa~ segernya badan! 🧘✨\nYuk luruskan punggung bareng aku!", int(duration * 1000 - 500))

        elif reminder_type == "drink_water":
            self._play_sound_blip(freq=1100, dur=60)
            QTimer.singleShot(120, lambda: self._play_sound_blip(freq=1450, dur=70))
            QTimer.singleShot(240, lambda: self._play_sound_blip(freq=1750, dur=90))
            if has_queued or self._was_combo:
                self.say("Lanjut minum segelas air putih! 🥛💧✨\nBiar tubuh segar & terhidrasi maksimal!", int(duration * 1000 - 500))
            elif auto:
                msg = random.choice([
                    "Waktunya minum air putih! 🥛💧✨\nTubuh terhidrasi = pikiran segar & fokus!",
                    "Segelas air putih siap membantumu tetap sehat, yuk minum bareng aku! 💧🐾",
                    "Istirahatkan mata sejenak dan minum air dulu yuk nya! 🥛🌸"
                ])
                self.say(msg, int(duration * 1000 - 500))
            else:
                self.say("Slurp slurp nyaaa~ Segernya minum air putih! 🥛💧✨\nJangan lupa minum juga ya!", int(duration * 1000 - 500))

        # Start unified step countdown timer
        self._reminder_end_timer.start(int(duration * 1000))

    def _end_centered_reminder(self):
        """Called when a step duration expires. Proceeds to next queued step or glides home."""
        if self._reminder_queue:
            next_type, next_auto, next_dur = self._reminder_queue.pop(0)
            self._was_combo = True
            self._execute_reminder_step(next_type, next_auto, next_dur)
            return

        # All routine steps finished -> glide home!
        self._was_combo = False
        if self._active_reminder_type is not None and not self._glide_timer.isActive():
            orig_x, orig_y = self._home_pos
            orig_size = self._home_size

            def on_returned_home():
                self._active_reminder_type = None
                self.set_state("idle")
                self.say("Rutinitas istirahat selesai! Badan bugar & pikiran fokus lagi nya~ 🐾💪", 4000)

            self.set_state("celebrate", duration_seconds=1.0)
            self._start_smooth_glide(orig_x, orig_y, orig_size, duration=0.55, on_complete=on_returned_home)

    def trigger_stretch(self, auto=False):
        """Executes the kawaii cat stretch yoga posture via Unified Center Stage."""
        self._start_centered_reminder("stretch", auto=auto, duration=6.0)

    def trigger_drink_water(self, auto=False):
        """Executes the kawaii cat drinking water animation via Unified Center Stage."""
        self._start_centered_reminder("drink_water", auto=auto, duration=6.0)

    def trigger_combo_routine(self):
        """Manually launches the full Sequential Combo Health Routine (Stretch + Drink Water)."""
        self._start_centered_reminder("stretch", auto=False, duration=5.0, queue_next=[("drink_water", False, 5.0)])

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

    def _toggle_hydration_reminder(self, checked):
        self.settings["hydration_reminder_enabled"] = checked
        save_settings(self.settings)
        self.pomodoro.start_health_timers()
        cur_min = self.settings.get("hydration_reminder_min", 45)
        if checked:
            self.say(f"Pengingat minum aktif! Aku ingatkan tiap {cur_min} menit ya nya~ 💧", 3500)
        else:
            self.say("Pengingat minum dinonaktifkan nya! 🐾", 3000)

    def _prompt_hydration_interval(self):
        cur_min = self.settings.get("hydration_reminder_min", 45)
        val, ok = QInputDialog.getInt(
            self, "Timer Pengingat Minum Air",
            "Masukkan interval pengingat minum air (dalam menit):\nContoh: 15 untuk tes cepat, 45 untuk hidrasi ideal.",
            value=cur_min, min=1, max=300, step=5
        )
        if ok and val > 0:
            self.set_hydration_interval(val)

    def set_hydration_interval(self, minutes):
        self.settings["hydration_reminder_min"] = minutes
        self.settings["hydration_reminder_enabled"] = True
        save_settings(self.settings)
        self.pomodoro.start_health_timers()
        self.say(f"Timer minum air diatur ke tiap {minutes} menit nya! ⏱️💧", 4000)

    def _on_hydration_reminder(self):
        """Triggered periodically when user has been working continuously without drinking water."""
        self.trigger_drink_water(auto=True)

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
