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

from src.sprites import PALETTES, ACCESSORIES, render_cat_frame
from src.speech_bubble import SpeechBubble
from src.pomodoro import PomodoroManager
from src.local_watcher import LocalWatcher
from src.global_hooks import GlobalInputWatcher
from src.settings import save_settings
from src.autostart import is_startup_enabled, set_startup_enabled
from src.pomodoro_badge import PomodoroBadge
from src.pomodoro_dialog import CustomPomodoroDialog
from src.sticky_note import StickyNote
from src.alarm_dialog import CustomAlarmDialog
from src.ai_watcher import AIAgentWatcher
import src.audio as audio


import ctypes
from ctypes import wintypes

class _MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("rcMonitor", ctypes.wintypes.RECT),
        ("rcWork", ctypes.wintypes.RECT),
        ("dwFlags", ctypes.wintypes.DWORD)
    ]

if sys.platform == "win32":
    try:
        user32 = ctypes.windll.user32
        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.GetForegroundWindow.argtypes = []
        user32.GetWindowRect.restype = wintypes.BOOL
        user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.MonitorFromWindow.restype = wintypes.HANDLE
        user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
        user32.GetMonitorInfoW.restype = wintypes.BOOL
        user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_MONITORINFO)]
        user32.SetWindowPos.restype = wintypes.BOOL
        user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    except Exception:
        pass


def set_win32_topmost(widget):
    """Enforce topmost z-order on Windows OS using native Win32 API."""
    if sys.platform == "win32" and widget:
        try:
            hwnd = int(widget.winId())
            if hwnd:
                HWND_TOPMOST = -1
                SWP_NOSIZE = 0x0001
                SWP_NOMOVE = 0x0002
                SWP_NOACTIVATE = 0x0010
                flags = SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
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

        # State Continuity & Interruption Memory (Preserves active feature during typing/scroll)
        self.pre_interruption_state = "idle"
        self.pre_interruption_ticks = 0
        self.pre_interruption_max_ticks = 99999999
        self._was_peeking_before_drag = False

        # Unified Center-Stage Reminder Manager (Prevents state collision & guarantees 100% accurate home restoration)
        self._active_reminder_type = None  # None, "stretch", "drink_water", etc.
        self._reminder_queue = []          # Sequential combo queue: [(type, auto, duration), ...]
        self._was_combo = False
        self._home_size = self.sprite_size
        self._home_pos = (self.x(), self.y())
        self._reminder_end_timer = QTimer(self)
        self._reminder_end_timer.setSingleShot(True)
        self._reminder_end_timer.timeout.connect(self._end_centered_reminder)
        self._reminder_finish_callback = None

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
        self.accessory = self.settings.get("accessory", "none")

        # Load ONLY the essential idle + walk sprites synchronously (instant startup)
        self._load_essential_sprites(self.skin)

        # Floating Widgets (Speech, Pomodoro Badge, Sticky Note)
        self.speech_bubble = SpeechBubble()
        self.speech_bubble.bubble_hidden.connect(self._on_bubble_hidden)
        self.pomodoro_badge = PomodoroBadge()
        self.pomodoro_badge.clicked.connect(self._on_pomodoro_badge_clicked)
        self.sticky_note = StickyNote()

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

        # AI Agent Auto-Watcher (Comnyang AI auto-thinking & celebration)
        self.ai_watcher = AIAgentWatcher(self.settings, parent=self)
        self.ai_watcher.ai_thinking_started.connect(self._on_ai_thinking_started)
        self.ai_watcher.ai_task_completed.connect(self._on_ai_task_completed)
        self.ai_watcher.external_message_received.connect(lambda msg: self.say(msg, 3500))

        # Global Input Watcher (Comnyang-style cadence reaction to typing, overheat, scrolling, and toxic detection)
        toxic_enabled = self.settings.get("toxic_guardian_enabled", True)
        self.input_watcher = GlobalInputWatcher(self, toxic_guardian_enabled=toxic_enabled)
        self.input_watcher.typing_started.connect(self._on_global_typing_start)
        self.input_watcher.typing_started.connect(self.ai_watcher.on_user_activity)
        self.input_watcher.typing_stopped.connect(self._on_global_typing_stop)
        self.input_watcher.overheat_started.connect(self._on_global_overheat_start)
        self.input_watcher.overheat_ended.connect(self._on_global_overheat_end)
        self.input_watcher.mouse_scrolled.connect(self._on_global_scroll)
        self.input_watcher.mouse_scrolled.connect(lambda dx, dy: self.ai_watcher.on_user_activity())
        self.input_watcher.enter_pressed.connect(self.ai_watcher.on_user_pressed_enter)
        self.input_watcher.toxic_detected.connect(self._on_toxic_detected)

        # Animation Loop Timer (110ms per frame for smooth 9-10 FPS sprite cycling)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(110)

        # Anti-Toxic Guardian Micro-Jitter Shock Shake
        self.toxic_session_count = 0
        self._shock_shake_offset = (0, 0)
        self._shock_shake_ticks = 0
        self._shock_shake_timer = QTimer(self)
        self._shock_shake_timer.timeout.connect(self._on_shock_shake_tick)

        # Physics & AI Behavior Timer (16ms = 60 FPS game loop)
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._update_physics_loop)
        self.physics_timer.start(16)

        # Peek Mode State & Auto Fullscreen Scanner
        self.is_peeking = False
        self.peek_side = "right"
        self._peek_return_pos = None
        self._auto_peeked = False
        self._fullscreen_timer = QTimer(self)
        self._fullscreen_timer.timeout.connect(self._check_fullscreen_activity)
        if self.settings.get("auto_peek_fullscreen", True):
            self._fullscreen_timer.start(350)

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

    # -------------------------------------------------------------
    # Sprite & Cache Management (Pre-cached for instant 60 FPS O(1) rendering)
    # -------------------------------------------------------------
    def _render_state_frames(self, skin_name, state):
        """Renders 4 frames for a given state and stores them in pixmap_cache."""
        self.pixmap_cache[state] = []
        acc = getattr(self, "accessory", "none")
        for frame in range(4):
            pil_img = render_cat_frame(skin_name, state, frame, accessory=acc)
            raw_bytes = pil_img.tobytes("raw", "RGBA")
            qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
            self.pixmap_cache[state].append(QPixmap.fromImage(qimg))

    def _ensure_state_frames(self, state):
        """Ensures frames for a state are rendered in cache immediately on-demand."""
        if state not in self.pixmap_cache or not self.pixmap_cache[state]:
            self._render_state_frames(self.skin, state)

    def _load_essential_sprites(self, skin_name):
        """Loads essential sprites synchronously for instant window display (<80ms)."""
        self.skin = skin_name
        self.pixmap_cache.clear()
        self.idle_eye_cache.clear()
        self._sprites_ready = False
        for st in ("idle", "walk_left", "walk_right", "celebrate", "work", "sleep"):
            self._render_state_frames(skin_name, st)

    def _deferred_load_remaining_sprites(self, skin_name):
        """Loads remaining state sprites + idle eye cache in small batches via QTimer chain."""
        remaining = [
            "overheat", "paper_unroll", "pet",
            "stretch", "drink_water", "feed", "thinking", "drag", "land"
        ]
        self._deferred_batch_queue = list(remaining)
        self._deferred_skin = skin_name
        self._process_next_sprite_batch()

    def _process_next_sprite_batch(self):
        """Processes 1 state per tick to avoid blocking the UI thread."""
        if not self._deferred_batch_queue:
            self._deferred_load_idle_eyes()
            return
            
        st = self._deferred_batch_queue.pop(0)
        self._render_state_frames(self._deferred_skin, st)

        if self._deferred_batch_queue:
            QTimer.singleShot(24, self._process_next_sprite_batch)
        else:
            # All states loaded — now pre-cache idle eye directions
            self._deferred_load_idle_eyes()

    def _deferred_load_idle_eyes(self):
        """Pre-caches all 36 idle eye-direction frames for O(1) runtime lookup."""
        acc = getattr(self, "accessory", "none")
        for frame in range(4):
            for ldx in (-1, 0, 1):
                for ldy in (-1, 0, 1):
                    pil_img = render_cat_frame(self._deferred_skin, "idle", frame, ldx, ldy, accessory=acc)
                    raw_bytes = pil_img.tobytes("raw", "RGBA")
                    qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
                    self.idle_eye_cache[(frame, ldx, ldy)] = QPixmap.fromImage(qimg)
        self._sprites_ready = True

    def _load_skin_sprites(self, skin_name):
        """Full synchronous load (used by skin & accessory switcher)."""
        self._load_essential_sprites(skin_name)
        remaining = [
            "overheat", "paper_unroll", "pet",
            "stretch", "drink_water", "feed", "thinking", "drag", "land"
        ]
        for st in remaining:
            self._render_state_frames(skin_name, st)
        acc = getattr(self, "accessory", "none")
        for frame in range(4):
            for ldx in (-1, 0, 1):
                for ldy in (-1, 0, 1):
                    pil_img = render_cat_frame(skin_name, "idle", frame, ldx, ldy, accessory=acc)
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

        frames = self.pixmap_cache.get(self.state)
        if not frames:
            self._ensure_state_frames(self.state)
            frames = self.pixmap_cache.get(self.state)

        if not frames:
            frames = self.pixmap_cache.get("idle", [])

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
        if self.sticky_note.isVisible() or self.sticky_note._text:
            self.sticky_note.update_position_relative_to(self.pos(), self.sprite_size)

    # -------------------------------------------------------------
    # State & Animation Controller
    # -------------------------------------------------------------
    def set_state(self, new_state, duration_seconds=None):
        if new_state == "walk":
            new_state = "walk_right"
        elif new_state == "jump":
            new_state = "celebrate"
        if new_state not in ("hunt", "alert"):
            self._ensure_state_frames(new_state)
        self.state = new_state
        self.frame_index = 0
        self.state_ticks = 0
        if duration_seconds is not None:
            self.max_state_ticks = int(duration_seconds * 60)
        else:
            self.max_state_ticks = 99999999  # Infinite until explicit state change
        self.update()

    def get_default_resume_state(self) -> str:
        """Returns the appropriate resting state to return to after temporary interruptions."""
        # 1. Active AI Thinking session takes top priority
        if hasattr(self, "ai_watcher") and self.ai_watcher.is_active_ai_session:
            return "thinking"
        # 2. Active Pomodoro session
        if hasattr(self, "pomodoro") and self.pomodoro.is_active:
            if self.pomodoro.mode == "break":
                return "sleep"
            return "idle"
        # 3. Active Screen Edge Peek mode
        if hasattr(self, "is_peeking") and self.is_peeking:
            return f"peek_{self.peek_side}"
        # 4. Long-running persistent activities (stretch, drink_water, feed, sleep)
        if hasattr(self, "pre_interruption_state") and self.pre_interruption_state in [
            "stretch", "drink_water", "feed", "sleep"
        ]:
            return self.pre_interruption_state
        return "idle"

    def resume_default_state(self):
        """Restores the active continuous state (thinking, pomodoro, peek, or previous state)."""
        target = self.get_default_resume_state()
        if self.state != target:
            if hasattr(self, "pre_interruption_state") and target == self.pre_interruption_state and self.pre_interruption_max_ticks < 10000:
                rem_ticks = max(60, self.pre_interruption_max_ticks - self.pre_interruption_ticks)
                self.set_state(target, duration_seconds=(rem_ticks / 60.0))
            else:
                self.set_state(target)

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
        to ensure critical health dialogs are shown clearly.
        """
        return self._active_reminder_type is not None

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
        if self.state in ["celebrate", "land", "stretch", "drink_water", "overheat", "sulk"]:
            if not getattr(self.input_watcher, "_is_overheated", False) or self.max_state_ticks < 100000:
                self.state_ticks += 1
                if self.state_ticks > self.max_state_ticks:
                    self.resume_default_state()
            return
        elif self.state == "thinking":
            if not self.ai_watcher.is_active_ai_session and self.max_state_ticks < 10000:
                self.state_ticks += 1
                if self.state_ticks > self.max_state_ticks:
                    self.resume_default_state()
            return
        elif self.state in ["peek_left", "peek_right", "peek_bottom", "peek"]:
            return

        # ── REALTIME PET HEAD ZONE CHECK (Instant Stop When Cursor Leaves Head) ──
        if self.state == "pet":
            local_p = self.mapFromGlobal(QCursor.pos())
            head_rect = self._get_head_rect()
            if not self.rect().contains(local_p) or not head_rect.contains(local_p):
                self.resume_default_state()
            return

        # Do not wander if Pomodoro is active, typing/overheated, stretching, drinking water, thinking, celebrating, peeking, or sulking
        if not self.settings.get("wander_mode", True) or self.pomodoro.is_active or self.state in [
            "work", "overheat", "paper_unroll", "sleep", "stretch", "drink_water",
            "thinking", "celebrate", "sulk", "peek_left", "peek_right", "peek_bottom", "peek"
        ]:
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
        """User started typing -> cat begins keyboard kneading, preserving active session/previous state."""
        if self.is_reminder_locked:
            return
        if self.state not in ["drag", "land", "pet", "overheat", "work"]:
            if self.state in ["stretch", "drink_water", "feed", "sleep"]:
                self.pre_interruption_state = self.state
                self.pre_interruption_ticks = self.state_ticks
                self.pre_interruption_max_ticks = self.max_state_ticks
            else:
                self.pre_interruption_state = "idle"
            self.is_hunting = False
            self.set_state("work")

    def _on_global_typing_stop(self):
        """User stopped typing -> resume active/previous state."""
        if self.is_reminder_locked:
            return
        if self.state in ["work", "overheat"]:
            self.resume_default_state()

    def _on_global_overheat_start(self):
        """Typing super fast -> Overheat mode with steam puffs!"""
        if self.is_reminder_locked:
            return
        if self.state not in ["drag", "land", "pet", "overheat"]:
            if self.state != "work":
                if self.state in ["stretch", "drink_water", "feed", "sleep"]:
                    self.pre_interruption_state = self.state
                    self.pre_interruption_ticks = self.state_ticks
                    self.pre_interruption_max_ticks = self.max_state_ticks
                else:
                    self.pre_interruption_state = "idle"
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
        Resumes previous active state (AI Thinking, Pomodoro, Peek, Stretch, etc.) once scrolling ends.
        """
        if self.is_reminder_locked:
            return
        if self.state not in ["drag", "pet"]:
            if self.state != "paper_unroll":
                if self.state not in ["work", "overheat"]:
                    if self.state in ["stretch", "drink_water", "feed", "sleep"]:
                        self.pre_interruption_state = self.state
                        self.pre_interruption_ticks = self.state_ticks
                        self.pre_interruption_max_ticks = self.max_state_ticks
                    else:
                        self.pre_interruption_state = "idle"
                self.set_state("paper_unroll")
            self.frame_index = (self.frame_index + 1) % 4
            self.update()
            self.scroll_reset_timer.start(400)

    def _on_scroll_timeout(self):
        """Scroll stopped -> return to active/previous state."""
        self._scroll_delta_accum = 0.0
        if self.state == "paper_unroll":
            self.resume_default_state()

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

    def _trigger_shock_jitter(self, ticks=8):
        """Triggers a snappy, visible micro-jitter vibration on the cat when shocked."""
        self._shock_shake_ticks = ticks
        if not self._shock_shake_timer.isActive():
            self._shock_shake_timer.start(35)

    def _on_shock_shake_tick(self):
        if self._shock_shake_ticks > 0:
            self._shock_shake_ticks -= 1
            # Random snappy jitter offsets (-3 to +3 pixels)
            jx = random.choice([-3, 3, -2, 2, -1, 1])
            jy = random.choice([-2, 2, -1, 1, 0])
            self._shock_shake_offset = (jx, jy)
            self.update()
        else:
            self._shock_shake_offset = (0, 0)
            self._shock_shake_timer.stop()
            self.update()

    def _on_toxic_detected(self, snippet: str, severity: str, matched_words: str):
        """
        Anti-Toxic Guardian reaction (Tahap 1 & 2):
        Cat alerts user with micro-jitter shock, personalized name, session frequency tracking,
        and sulking / overheat funny reactions with animated anime anger mark 💢.
        """
        if self.is_reminder_locked or self.is_dragging:
            return

        raw_name = self.settings.get("user_name", "").strip()
        user_name = f" {raw_name}" if raw_name else " bro"

        self.toxic_session_count += 1

        # Intervention dialogue on repeated toxicity in current session (every 3rd or >=4th time)
        if self.toxic_session_count >= 4 and (self.toxic_session_count % 2 == 0):
            self._trigger_shock_jitter(ticks=12)
            self._play_sound_blip(freq=550, dur=120)
            self.set_state("sulk", duration_seconds=5.0)
            intervention_quotes = [
                f"Waduh{user_name}, udah {self.toxic_session_count}x ngegas sesi ini! Meong ngambek nih 😾💢",
                f"Duh jarimu panas banget{user_name} (udah {self.toxic_session_count}x toxic)! Istirahat minum air dulu yuk 💧🐾",
                f"Sabar ya{user_name}... Jangan biarin emosi ngalahin fokus kamu! Semangat meong! ✨🐱",
                f"Keyboard kamu capek diketik kasar terus{user_name}... Tarik napas 3 detik bareng meong yuk 🐾🧘"
            ]
            self.say(random.choice(intervention_quotes), 5000)
            return

        # Choose distinct reactions & dialogues according to severity level
        if severity == "high":
            self._trigger_shock_jitter(ticks=10)
            self._play_sound_blip(freq=600, dur=100)
            # 55% chance to sulk (pout facing away) or 45% overheat
            if random.random() < 0.55:
                self.set_state("sulk", duration_seconds=4.5)
                high_quotes = [
                    f"Hmph! Meong ngambek ya{user_name}! Kasar banget jarimu 😾💢",
                    f"Astaghfirullah jarimu{user_name}! 😾 Istighfar dulu yuk...",
                    f"Meong buang muka nih! Jangan toxic dong nya{user_name} 😾",
                    f"Waduh kasar banget meong! 🙀 Tarik napas panjang dulu{user_name}...",
                    f"Dih ngegas parah meong! Santai{user_name}, jangan kebawa emosi game! 🔥🎮",
                    f"Keyboard lu ga salah apa-apa{user_name}, jangan dihantam kasar nya~ 🐾"
                ]
            else:
                self.set_state("overheat", duration_seconds=3.5)
                high_quotes = [
                    f"Astaghfirullah jarimu{user_name}! 😾 Istighfar dulu yuk...",
                    f"Waduh kasar banget meong! 🙀 Tarik napas panjang dulu{user_name}...",
                    f"Jangan toxic dong nya! Nanti kena banned/report lho{user_name}! 😾",
                    f"Meong kaget dengernya! Jarimu butuh ditenangin meong 🐾💧",
                    f"Dih ngegas parah meong! Santai{user_name}, jangan kebawa emosi game! 🔥🎮",
                    f"Keyboard lu ga salah apa-apa{user_name}, jangan dihantam kasar nya~ 🐾"
                ]
            self.say(random.choice(high_quotes), 4500)
        elif severity == "medium":
            self._trigger_shock_jitter(ticks=6)
            self._play_sound_blip(freq=800, dur=80)
            if random.random() < 0.35:
                self.set_state("sulk", duration_seconds=3.5)
                med_quotes = [
                    f"Hmph! Dih ngegas amat meong... Santai dulu napa{user_name} 😾💢",
                    f"Meong gamau denger kata kasar nya{user_name}~ 🐾",
                    f"Kok toxic sih meong? Senyum dulu yuk{user_name}! 🐱✨"
                ]
            else:
                self.set_state("thinking", duration_seconds=3.0)
                med_quotes = [
                    f"Dih ngegas amat meong... Santai dulu napa{user_name} 😾",
                    f"Sabar{user_name}, main game/ngetik dibawa santai aja nya~ 🐾",
                    f"Kok toxic sih meong? Senyum dulu yuk{user_name}! 🐱✨",
                    f"Jangan emosi{user_name}, keyboardnya kasian diketik kasar 🐾",
                    f"Kalo emosi mending minum air dulu ya nya{user_name}~ 💧",
                    f"Fokus santai{user_name}, emosi ga bikin menang kok nya 🐾🎯"
                ]
            self.say(random.choice(med_quotes), 4000)
        else:  # mild
            self._play_sound_blip(freq=1100, dur=60)
            self.set_state("thinking", duration_seconds=2.5)
            mild_quotes = [
                f"Eits, ada yang lagi kesel nih meong~ 🐾",
                f"Santai{user_name}, peluk meong dulu biar adem 🐱💤",
                f"Sabar ya{user_name}, semua masalah pasti ada solusinya ✨",
                f"Tarik napas hembuskan nya~ Meong temenin di sini 🐾"
            ]
            self.say(random.choice(mild_quotes), 3500)

    # -------------------------------------------------------------
    # Paint & Render (Nearest-Neighbor Crisp Scaling + Mochi Tilt)
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        # Micro-Jitter Shock Shake Translation
        shake_x, shake_y = getattr(self, "_shock_shake_offset", (0, 0))
        if shake_x != 0 or shake_y != 0:
            painter.translate(shake_x, shake_y)

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

        elif self.state in ["celebrate", "jump"]:
            fi = self.frame_index % 4
            if fi == 0:
                # Squash prep
                w = int(self.sprite_size * 1.06)
                h = int(self.sprite_size * 0.92)
                ox = (self.sprite_size - w) // 2
                oy = self.sprite_size - h
                painter.drawPixmap(ox, oy, w, h, pixmap)
            elif fi == 1:
                # Upward launch stretch
                w = int(self.sprite_size * 0.94)
                h = int(self.sprite_size * 1.06)
                ox = (self.sprite_size - w) // 2
                oy = int(-self.sprite_size * 0.08)
                painter.drawPixmap(ox, oy, w, h, pixmap)
            elif fi == 2:
                # High apex jump in air
                ox = 0
                oy = int(-self.sprite_size * 0.14)
                painter.drawPixmap(ox, oy, self.sprite_size, self.sprite_size, pixmap)
            else:
                # Soft descent
                ox = 0
                oy = int(-self.sprite_size * 0.04)
                painter.drawPixmap(ox, oy, self.sprite_size, self.sprite_size, pixmap)

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
                if self.state != "pet" and self.state not in ["drag", "land", "work", "overheat", "sulk"]:
                    self.set_state("pet")
                    audio.play_purr(self.settings)
            else:
                if self.state == "pet":
                    self.resume_default_state()

    def leaveEvent(self, event):
        """Immediately stop petting as soon as cursor leaves the cat window."""
        super().leaveEvent(event)
        if self.state == "pet":
            self.resume_default_state()

    def mousePressEvent(self, event):
        if self._glide_timer.isActive():
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.has_dragged = False
            self.is_hunting = False
            self._was_peeking_before_drag = self.is_peeking or self.state.startswith("peek")
            self._auto_peeked = False
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.drag_start_global_pos = event.globalPosition().toPoint()
            self.last_drag_global_pt = self.drag_start_global_pos
            self.last_drag_time = time.time()
            self.drag_velocity_x = 0.0
            self.mochi_tilt = 0.0
            self.pre_drag_state = self.state if self.state not in ["drag", "land"] else self.get_default_resume_state()
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
                screen = self._get_current_screen_geometry()
                mid_x = screen.left() + screen.width() / 2.0
                dist_left = self.pos_x_f - screen.left()
                dist_right = (screen.right() - self.sprite_size) - self.pos_x_f
                dist_bottom = (screen.bottom() - self.sprite_size) - self.pos_y_f
                dist_top = self.pos_y_f - screen.top()

                # If the cat was peeking before drag, snap cleanly to nearest screen edge (left, right, or bottom)
                if getattr(self, "_was_peeking_before_drag", False) or self.is_peeking or self.state.startswith("peek"):
                    self._auto_peeked = False
                    if self.pos_y_f >= screen.bottom() - self.sprite_size - 130 and (dist_bottom < min(dist_left, dist_right)):
                        target_side = "bottom"
                    elif self.pos_x_f >= mid_x:
                        target_side = "right"
                    else:
                        target_side = "left"

                    self.enter_peek_mode(side=target_side, manual=False)
                    self._play_sound_blip(freq=1350, dur=40)
                else:
                    self.settings["pos_x"] = int(self.pos_x_f)
                    self.settings["pos_y"] = int(self.pos_y_f)
                    save_settings(self.settings)

                    # Landing squish bounce
                    self.set_state("land")
                    self._play_sound_blip(freq=950, dur=50)
                    restore_state = self.pre_drag_state if self.pre_drag_state not in ["drag", "land"] else self.get_default_resume_state()
                    QTimer.singleShot(350, lambda: self.set_state(restore_state))

                if random.random() < 0.35:
                    landing_quotes = [
                        "Duduk di sini ya nya~ 🐾",
                        "Spot baru yang nyaman nya! 😸",
                        "Siap mantau dari sini nya~ ✨",
                        "Tempat yang bagus nya! 📍"
                    ]
                    QTimer.singleShot(400, lambda: self.say(random.choice(landing_quotes), 3000))
            else:
                # Single left-click response
                self._on_pet_clicked()

            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if hasattr(self, "laser_overlay") and self.laser_overlay and self.laser_overlay.isVisible():
                self.laser_overlay.stop_laser()
                self.say("Mode Laser dimatikan nya~ 🐾", 2500)
                event.accept()
                return
        super().keyPressEvent(event)

    # -------------------------------------------------------------
    # Dialogues & Responses
    # -------------------------------------------------------------
    def say(self, message, duration_ms=4500):
        self.sticky_note.temp_hide()
        if hasattr(self.pomodoro_badge, "temp_hide"):
            self.pomodoro_badge.temp_hide()
        else:
            self.pomodoro_badge.hide()
        self.speech_bubble.show_message(message, duration_ms)
        self._update_bubble_position()
        self._play_sound_blip("pop")

    def _on_bubble_hidden(self):
        # Restore floating widgets when speech bubble hides
        self.sticky_note.temp_show()
        if hasattr(self.pomodoro_badge, "temp_show"):
            self.pomodoro_badge.temp_show()
        elif self.pomodoro.is_active:
            self.pomodoro_badge.show()

    def _say_welcome(self):
        pet_name = PALETTES.get(self.skin, {}).get("name", "Nyang")
        user_name = self.settings.get("user_name", "").strip()
        greeting = f"Halo {user_name}!" if user_name else "Halo!"
        self.say(f"{greeting} Aku {pet_name} siap nemenin kamu kerja nya~ 🐾")

        # Initialize sticky note if exists
        saved_note = self.settings.get("sticky_note", "").strip()
        if saved_note:
            self.sticky_note.start(saved_note)

    def _on_pet_clicked(self):
        """Single left-click response: Shows dialogue and cute sound without changing animation."""
        if self.state == "sulk":
            self._trigger_shock_jitter(ticks=6)
            self._play_sound_blip(freq=750, dur=60)
            raw_name = self.settings.get("user_name", "").strip()
            user_name = f" {raw_name}" if raw_name else " bro"
            pout_quotes = [
                f"Hmph! Meong lagi ngambek{user_name}! 😾💢",
                f"Nanti dulu elusnya meong, jarimu masih kasar tadi... 😾",
                f"Jangan toxic lagi ya{user_name}, meong sedih dengernya nya~ 🐾💧",
                f"Meong lagi buang muka nih! Jangan diganggu dulu meong~ 😾"
            ]
            self.say(random.choice(pout_quotes), 3500)
            return

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
        audio.play_meow_for_skin(self.skin, self.settings)
        self.say(random.choice(purrs), 3500)

    def _play_sound_blip(self, sound_type="blip", freq=None, dur=None):
        if not self.settings.get("sound_enabled", False):
            return
        audio.play_sound(sound_type if isinstance(sound_type, str) else "blip", self.settings)

    # -------------------------------------------------------------
    # Pomodoro & Reminder Handlers
    # -------------------------------------------------------------
    def _on_pomodoro_start(self, mode):
        cycle_info = self.pomodoro.cycle_label()
        cycle_text = f" ({cycle_info})" if cycle_info else ""
        if mode == "work":
            self.set_state("work")
            duration = self.pomodoro.work_minutes
            total_secs = duration * 60
            self.say(f"Fokus mode aktif! ({duration} menit){cycle_text} Ayo selesaikan tugasnya nya~ 💻✨", 4000)
        elif mode == "break":
            self.set_state("sleep")
            duration = self.pomodoro.break_minutes
            total_secs = duration * 60
            self.say(f"Waktu istirahat ({duration} menit)!{cycle_text} Rehat dulu ya nya~ ☕😴", 4000)
        else:
            return

        # Show floating pomodoro badge with cycle info
        self.pomodoro_badge.start(mode, total_secs, cycle_info)
        if self.speech_bubble.isVisible():
            self.pomodoro_badge.temp_hide()
        self.pomodoro_badge.update_position_relative_to(self.pos(), self.sprite_size)

    def _on_pomodoro_finish(self, finished_mode):
        # Hide floating pomodoro badge during center stage
        self.pomodoro_badge.stop()

        if finished_mode == "work":
            # Work session ended -> Glide to center of screen for celebratory reminder
            is_auto = self.pomodoro.is_auto_cycle
            break_min = self.pomodoro.break_minutes

            def on_focus_reminder_returned():
                if is_auto:
                    # Proceed to break time automatically!
                    self.pomodoro.start_break(break_min)
                else:
                    self.set_state("idle")

            self._start_centered_reminder(
                "pomodoro_work_done",
                auto=True,
                duration=6.0,
                on_finish_callback=on_focus_reminder_returned
            )

        elif finished_mode == "break":
            # Break session ended -> Glide to center of screen for reminder
            is_auto = self.pomodoro.is_auto_cycle
            cycle = self.pomodoro.current_cycle
            total = self.pomodoro.total_cycles
            work_min = self.pomodoro.work_minutes

            def on_break_reminder_returned():
                if is_auto:
                    if cycle < total:
                        # Advance to next cycle automatically!
                        self.pomodoro.current_cycle += 1
                        self.pomodoro.start_focus(work_min)
                    else:
                        # Completed all cycles!
                        self.pomodoro.stop()
                        self.set_state("idle")
                        self.say("Semua siklus fokus selesai! Kamu produktif banget hari ini! 🌟🐾", 5000)
                else:
                    self.set_state("idle")

            self._start_centered_reminder(
                "pomodoro_break_done",
                auto=True,
                duration=6.0,
                on_finish_callback=on_break_reminder_returned
            )

    def _on_pomodoro_tick(self, remaining, mode):
        mins = remaining // 60
        secs = remaining % 60
        title = "Fokus" if mode == "work" else "Break"
        cycle_info = f" {self.pomodoro.cycle_label()}" if self.pomodoro.cycle_label() else ""
        self.setToolTip(f"NyangBuddy - {title} [{mins:02d}:{secs:02d}]{cycle_info} (Ctrl+Scroll: Zoom)")

        # Update floating badge countdown & progress bar
        self.pomodoro_badge.update_tick(remaining)

    def _on_pomodoro_badge_clicked(self):
        """User clicked the floating pomodoro badge to stop the session."""
        self.pomodoro.stop()
        self.pomodoro_badge.stop()
        self.set_state("idle")
        self.say("Sesi Pomodoro dihentikan nya~ 🐾", 3000)

    def _prompt_custom_pomodoro_session(self):
        """Prompt user for custom focus, break, and cycle count via unified dialog."""
        dialog = CustomPomodoroDialog(
            parent=None,
            default_work=self.settings.get("pomodoro_work_min", 25),
            default_break=self.settings.get("pomodoro_break_min", 5),
            default_cycles=self.settings.get("pomodoro_cycles", 4)
        )
        geo = self._get_current_screen_geometry()
        dialog.move(
            geo.center().x() - dialog.width() // 2,
            geo.center().y() - dialog.height() // 2
        )
        accepted = (dialog.exec() == 1)

        # Re-enforce main pet window visibility and topmost priority
        self.show()
        self.raise_()
        if self.settings.get("stay_on_top", True):
            set_win32_topmost(self)

        if accepted:
            work_min, break_min, cycles = dialog.get_values()
            self.settings["pomodoro_work_min"] = work_min
            self.settings["pomodoro_break_min"] = break_min
            self.settings["pomodoro_cycles"] = cycles
            save_settings(self.settings)
            self.pomodoro.start_auto_cycle(work_min, break_min, cycles)

    def _on_reminder(self, text):
        self.say(text, 5000)

    # -------------------------------------------------------------
    # External Event (CLI / Watcher)
    # -------------------------------------------------------------
    def _on_external_event(self, data):
        state = data.get("state")
        message = data.get("message")
        duration = data.get("duration", 4)

        if state == "thinking":
            self.trigger_thinking(duration=duration, message=message)
        elif state in ["celebrate", "jump"]:
            self.trigger_celebrate(duration=duration, message=message)
        elif state in ["peek", "peek_right"]:
            self.enter_peek_mode(side="right", manual=True)
            if message:
                self.say(message, duration * 1000)
        elif state == "peek_left":
            self.enter_peek_mode(side="left", manual=True)
            if message:
                self.say(message, duration * 1000)
        elif state in ["peek_bottom", "peek_down"]:
            self.enter_peek_mode(side="bottom", manual=True)
            if message:
                self.say(message, duration * 1000)
        elif state in ["unpeek", "exit_peek"]:
            self.exit_peek_mode(manual=True)
            if message:
                self.say(message, duration * 1000)
        else:
            if state:
                self.set_state(state, duration_seconds=duration)
            if message:
                self.say(message, duration * 1000)

    def trigger_thinking(self, duration=None, message=None):
        """AI Agent Thinking reaction: curious head tilt + animated floating thought cloud."""
        self.set_state("thinking", duration_seconds=duration)
        audio.play_sound("pop", self.settings)
        if message:
            dur_ms = int(duration * 1000) if duration else 4000
            self.say(message, dur_ms)

    def trigger_celebrate(self, duration=4, message=None):
        """AI Agent Done / Celebrate Jump reaction: 4-frame victory jump with stars & celebratory chime."""
        self.set_state("celebrate", duration_seconds=duration)
        audio.play_celebrate(self.settings)
        if message:
            self.say(message, duration * 1000)

    def _on_ai_thinking_started(self, tool_name):
        """Auto-triggered when an active AI coding tool starts generating / thinking."""
        if self.is_reminder_locked or self.is_dragging:
            return
        if self.state not in ["drag", "land", "stretch", "drink_water"]:
            # Persistent thinking state until AI task completed signal arrives
            self.trigger_thinking(duration=None, message=f"AI ({tool_name}) sedang berpikir nya~ 🧠💭")

    def _on_ai_task_completed(self, tool_name):
        """Auto-triggered when an active AI coding tool finishes generating / task complete."""
        if self.is_reminder_locked or self.is_dragging:
            return
        if self.state not in ["drag", "land", "stretch", "drink_water"]:
            self.trigger_celebrate(duration=4, message=f"YAY! {tool_name} selesai bekerja nya! 🎉✨")

    def _check_fullscreen_activity(self):
        """Auto-detect fullscreen gaming/video and enter/exit peek mode."""
        if not self.settings.get("auto_peek_fullscreen", True):
            return
        if self.is_reminder_locked or self.is_dragging or self.pomodoro.is_active:
            return

        is_fs = self._is_active_window_fullscreen()
        if is_fs:
            if not self.is_peeking:
                self._auto_peeked = True
                self.enter_peek_mode(side="right", manual=False)
        else:
            if self.is_peeking and self._auto_peeked:
                self._auto_peeked = False
                self.exit_peek_mode(manual=False)

    def _is_active_window_fullscreen(self) -> bool:
        if sys.platform != "win32":
            return False
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd or hwnd == int(self.winId()):
                return False

            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buf, 256)
            cls = class_buf.value
            if cls in ("Progman", "WorkerW", "Shell_TrayWnd", "Windows.UI.Core.CoreWindow", "Qt6QWindowIcon"):
                return False

            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

            MONITOR_DEFAULTTONEAREST = 2
            hmon = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
            if not hmon:
                return False

            mi = _MONITORINFO()
            mi.cbSize = ctypes.sizeof(_MONITORINFO)
            if not user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
                return False

            mon = mi.rcMonitor
            work = mi.rcWork

            # Covers the physical display resolution (covering taskbar)
            covers_monitor = (
                rect.left <= mon.left and
                rect.top <= mon.top and
                rect.right >= mon.right and
                rect.bottom >= mon.bottom
            )
            if not covers_monitor:
                return False

            # If taskbar exists on monitor and window covers past work area -> true fullscreen
            if (work.bottom - work.top < mon.bottom - mon.top) or (work.right - work.left < mon.right - mon.left):
                return True

            return False
        except Exception:
            return False

    def enter_peek_mode(self, side: str = "right", manual: bool = True):
        """Enters Peek Mode: glides to screen edge and peeks with head & paws."""
        if self.is_reminder_locked:
            return

        if not self.is_peeking:
            self._peek_return_pos = (self.pos_x_f, self.pos_y_f)

        self.is_peeking = True
        self.peek_side = side
        self.set_state(f"peek_{side}")
        screen = self._get_current_screen_geometry()

        if side == "left":
            target_x = screen.left() - int(self.sprite_size * 0.45)
            target_y = max(screen.top() + 40, min(int(self.pos_y_f), screen.bottom() - self.sprite_size - 40))
        elif side == "bottom":
            target_x = max(screen.left() + 40, min(int(self.pos_x_f), screen.right() - self.sprite_size - 40))
            target_y = screen.bottom() - int(self.sprite_size * 0.48)
        else:  # "right"
            target_x = screen.right() - int(self.sprite_size * 0.55)
            target_y = max(screen.top() + 40, min(int(self.pos_y_f), screen.bottom() - self.sprite_size - 40))

        def on_arrived():
            self._play_sound_blip(freq=1350, dur=40)
            if manual:
                self.say("Mode Mengintip aktif! Aku di tepi layar ya nya~ 🫣🐾", 3000)

        self._start_smooth_glide(target_x, target_y, self.sprite_size, duration=0.22, on_complete=on_arrived)

    def exit_peek_mode(self, manual: bool = True):
        """Exits Peek Mode: glides back to original position."""
        if not self.is_peeking:
            return

        self.is_peeking = False
        self._auto_peeked = False
        screen = self._get_current_screen_geometry()

        if self._peek_return_pos:
            ret_x, ret_y = self._peek_return_pos
        else:
            ret_x = screen.right() - self.sprite_size - 60
            ret_y = screen.bottom() - self.sprite_size - 60

        def on_returned():
            self.set_state("idle")
            self._play_sound_blip(freq=1450, dur=45)
            if manual:
                self.say("Kembali ke layar utama nya! 🐾✨", 2500)

        self._start_smooth_glide(ret_x, ret_y, self.sprite_size, duration=0.45, on_complete=on_returned)

    def _toggle_auto_peek_fullscreen(self, checked):
        self.settings["auto_peek_fullscreen"] = checked
        save_settings(self.settings)
        if checked:
            self._fullscreen_timer.start(350)
            self.say("Auto-Peek Fullscreen aktif nya! 🎬🫣", 3000)
        else:
            self._fullscreen_timer.stop()
            self.say("Auto-Peek dinonaktifkan nya! 🐾", 3000)

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

        # -------------------------------------------------------------
        # 1. 🐱 Karakter & Kostum (Customization)
        # -------------------------------------------------------------
        cat_menu = menu.addMenu("🐱 Karakter & Kostum")

        skin_sub = cat_menu.addMenu("🐱 Ganti Skin Karakter")
        for skin_key, data in PALETTES.items():
            action = skin_sub.addAction(data["name"])
            action.setCheckable(True)
            action.setChecked(self.skin == skin_key)
            action.triggered.connect(lambda checked, k=skin_key: self._change_skin(k))

        wardrobe_sub = cat_menu.addMenu("👑 Lemari Aksesoris (Wardrobe)")
        for acc_key, data in ACCESSORIES.items():
            act = wardrobe_sub.addAction(data["name"])
            act.setCheckable(True)
            act.setChecked(self.accessory == acc_key)
            act.triggered.connect(lambda checked, k=acc_key: self.set_accessory(k))

        size_sub = cat_menu.addMenu("🔍 Ukuran Karakter (Size)")
        sizes = [
            ("🔎 Mini (64px)", 64),
            ("🐱 Sedang (96px)", 96),
            ("😺 Standar (128px - Default)", 128),
            ("🦁 Besar (160px)", 160),
            ("👑 Jumbo (192px)", 192)
        ]
        for label, sz in sizes:
            act = size_sub.addAction(label)
            act.setCheckable(True)
            act.setChecked(self.sprite_size == sz)
            act.triggered.connect(lambda checked, s=sz: self.set_sprite_size(s))
        size_sub.addSeparator()
        custom_size_act = size_sub.addAction("📐 Atur Ukuran Bebas (Custom)...")
        custom_size_act.triggered.connect(self._prompt_custom_size)

        cat_menu.addSeparator()
        name_action = cat_menu.addAction("👤 Set Panggilan Nama Kamu...")
        name_action.triggered.connect(self._prompt_user_name)

        # -------------------------------------------------------------
        # 2. ⏱️ Produktivitas & Kesehatan (Focus & Wellness)
        # -------------------------------------------------------------
        prod_menu = menu.addMenu("⏱️ Produktivitas & Kesehatan")

        pom_sub = prod_menu.addMenu("⏱️ Pomodoro Timer")
        if not self.pomodoro.is_active:
            auto_std = pom_sub.addAction("▶️ Mulai Standar (25m Fokus / 5m Break • 4 Siklus)")
            auto_std.triggered.connect(lambda: self.pomodoro.start_auto_cycle(25, 5, 4))
            auto_sprint = pom_sub.addAction("⚡ Mulai Sprint (50m Fokus / 10m Break • 2 Siklus)")
            auto_sprint.triggered.connect(lambda: self.pomodoro.start_auto_cycle(50, 10, 2))
            pom_sub.addSeparator()
            custom_sess = pom_sub.addAction("⚙️ Atur Sesi Kustom (Fokus + Break + Siklus)...")
            custom_sess.triggered.connect(self._prompt_custom_pomodoro_session)
            pom_sub.addSeparator()
            single_focus = pom_sub.addAction("🎯 Fokus Tunggal Saja (25 Menit)")
            single_focus.triggered.connect(lambda: self.pomodoro.start_focus(25))
            single_break = pom_sub.addAction("☕ Break Tunggal Saja (5 Menit)")
            single_break.triggered.connect(lambda: self.pomodoro.start_break(5))
        else:
            cycle_str = f" {self.pomodoro.cycle_label()}" if self.pomodoro.cycle_label() else ""
            stop_action = pom_sub.addAction(f"⏹️ Hentikan Pomodoro ({self.pomodoro.format_time()}{cycle_str})")
            stop_action.triggered.connect(self._on_pomodoro_badge_clicked)

        alarm_action = prod_menu.addAction("⏰ Setel Alarm Pengingat (Jam HH:mm)...")
        alarm_action.triggered.connect(self._prompt_custom_alarm)

        prod_menu.addSeparator()

        stretch_sub = prod_menu.addMenu("🧘 Pengingat Regang & Postur")
        now_stretch = stretch_sub.addAction("▶️ Regangkan Badan Sekarang (Layar Tengah)")
        now_stretch.triggered.connect(lambda: self.trigger_stretch(auto=False))
        stretch_sub.addSeparator()
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
            act = stretch_sub.addAction(label)
            act.setCheckable(True)
            act.setChecked(is_enabled and cur_int == mins)
            act.triggered.connect(lambda checked, m=mins: self.set_stretch_interval(m))
        stretch_sub.addSeparator()
        custom_act = stretch_sub.addAction("⏱️ Atur Waktu Kustom (Menit)...")
        custom_act.triggered.connect(self._prompt_stretch_interval)
        stretch_sub.addSeparator()
        toggle_act = stretch_sub.addAction("✅ Aktifkan Pengingat Otomatis")
        toggle_act.setCheckable(True)
        toggle_act.setChecked(is_enabled)
        toggle_act.triggered.connect(self._toggle_stretch_reminder)

        hyd_sub = prod_menu.addMenu("💧 Pengingat Minum Air (Hydration)")
        now_hyd = hyd_sub.addAction("▶️ Minum Air Sekarang (Layar Tengah)")
        now_hyd.triggered.connect(lambda: self.trigger_drink_water(auto=False))
        hyd_sub.addSeparator()
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
            act = hyd_sub.addAction(label)
            act.setCheckable(True)
            act.setChecked(hyd_enabled and cur_hyd == mins)
            act.triggered.connect(lambda checked, m=mins: self.set_hydration_interval(m))
        hyd_sub.addSeparator()
        custom_hyd_act = hyd_sub.addAction("⏱️ Atur Waktu Kustom (Menit)...")
        custom_hyd_act.triggered.connect(self._prompt_hydration_interval)
        hyd_sub.addSeparator()
        toggle_hyd_act = hyd_sub.addAction("✅ Aktifkan Pengingat Otomatis")
        toggle_hyd_act.setCheckable(True)
        toggle_hyd_act.setChecked(hyd_enabled)
        toggle_hyd_act.triggered.connect(self._toggle_hydration_reminder)

        combo_act = prod_menu.addAction("🌟 Paket Sehat (Regang + Minum Air)")
        combo_act.triggered.connect(self.trigger_combo_routine)

        prod_menu.addSeparator()
        note_action = prod_menu.addAction("📌 Catatan Tempel (Sticky Note)...")
        note_action.triggered.connect(self._prompt_sticky_note)

        # -------------------------------------------------------------
        # 3. ⚙️ Pengaturan & Perilaku (Settings & Behavior)
        # -------------------------------------------------------------
        settings_menu = menu.addMenu("⚙️ Pengaturan & Perilaku")

        peek_sub = settings_menu.addMenu("🫣 Mode Mengintip Layar (Peek Mode)")
        peek_sub.addAction("➡️ Mengintip dari Kanan (Right Edge)", lambda: self.enter_peek_mode("right", manual=True))
        peek_sub.addAction("⬅️ Mengintip dari Kiri (Left Edge)", lambda: self.enter_peek_mode("left", manual=True))
        peek_sub.addAction("⬇️ Mengintip dari Bawah (Bottom Edge)", lambda: self.enter_peek_mode("bottom", manual=True))
        if self.is_peeking:
            peek_sub.addAction("↩️ Keluar dari Mode Mengintip", lambda: self.exit_peek_mode(manual=True))
        peek_sub.addSeparator()
        auto_peek_act = peek_sub.addAction("✅ Otomatis Mengintip saat Fullscreen / Nonton")
        auto_peek_act.setCheckable(True)
        auto_peek_act.setChecked(self.settings.get("auto_peek_fullscreen", True))
        auto_peek_act.triggered.connect(self._toggle_auto_peek_fullscreen)

        settings_menu.addSeparator()

        sound_act = settings_menu.addAction("🔔 Efek Suara (Nonaktif = Mode Senyap Total)")
        sound_act.setCheckable(True)
        sound_act.setChecked(self.settings.get("sound_enabled", False))
        sound_act.triggered.connect(self._toggle_sound)

        hunt_act = settings_menu.addAction("🎯 Kejar Kursor Cepat (Mouse Hunt)")
        hunt_act.setCheckable(True)
        hunt_act.setChecked(self.settings.get("mouse_hunt_enabled", True))
        hunt_act.triggered.connect(self._toggle_mouse_hunt)

        wander_act = settings_menu.addAction("🚶 Jalan Santai Sendiri (Auto Wander)")
        wander_act.setCheckable(True)
        wander_act.setChecked(self.settings.get("wander_mode", True))
        wander_act.triggered.connect(self._toggle_wander)

        ai_act = settings_menu.addAction("🤖 Deteksi AI Agent Otomatis (Auto AI Watcher)")
        ai_act.setCheckable(True)
        ai_act.setChecked(self.settings.get("ai_watcher_enabled", True))
        ai_act.triggered.connect(self._toggle_ai_watcher)

        toxic_act = settings_menu.addAction("🛡️ Mode Anti-Toxic Guardian (NyangGuard)")
        toxic_act.setCheckable(True)
        toxic_act.setChecked(self.settings.get("toxic_guardian_enabled", True))
        toxic_act.triggered.connect(self._toggle_toxic_guardian)

        ontop_act = settings_menu.addAction("🔝 Selalu di Atas Layar (Always on Top)")
        ontop_act.setCheckable(True)
        ontop_act.setChecked(self.settings.get("stay_on_top", True))
        ontop_act.triggered.connect(self._toggle_stay_on_top)

        startup_act = settings_menu.addAction("🚀 Jalankan Otomatis saat Startup")
        startup_act.setCheckable(True)
        startup_act.setChecked(is_startup_enabled())
        startup_act.triggered.connect(self._toggle_startup)

        settings_menu.addSeparator()
        folder_act = settings_menu.addAction("📁 Buka Lokasi File (.exe)")
        folder_act.triggered.connect(self._open_app_folder)

        menu.addSeparator()

        # -------------------------------------------------------------
        # 5. ❌ Keluar (Close)
        # -------------------------------------------------------------
        quit_act = menu.addAction("❌ Keluar (Close)")
        quit_act.triggered.connect(self.close_app)

        menu.exec(global_pos)

    def _open_app_folder(self):
        """Opens Windows Explorer to the dist/ directory containing NyangBuddy.exe."""
        try:
            if getattr(sys, "frozen", False):
                folder = os.path.dirname(sys.executable)
            else:
                dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
                folder = dist_dir if os.path.exists(dist_dir) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.startfile(folder)
        except Exception as e:
            print(f"[App] Error opening folder: {e}")

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

    def set_accessory(self, acc_name: str):
        """Equips a wardrobe accessory dynamically across all states."""
        if acc_name == self.accessory:
            return
        self.accessory = acc_name
        self.settings["accessory"] = acc_name
        save_settings(self.settings)
        self._load_skin_sprites(self.skin)
        self.update()

        # Celebratory sound & dialogue
        audio.play_celebrate(self.settings)
        self.set_state("celebrate", duration_seconds=1.5)

        dialogues = {
            "wizard_hat": "Abrakadabra nya! Aku penyihir kucing sakti! 🧙✨",
            "royal_crown": "Sujudlah di hadapan Yang Mulia Kucing Kerajaan! 👑🐾",
            "cute_ribbon": "Pita manisnya cocok banget kan nya? Cantik sekali! 🎀🌸",
            "winter_scarf": "Syal merahnya hangat banget nya~ Nyaman! 🧣❤️",
            "sunglasses": "Keren maksimal! Siap beraksi, boss! 🕶️🔥",
            "flower_pin": "Bunga sakuranya harum dan indah nya~ 🌸✨",
            "none": "Aksesoris dilepas, kembali tampil natural nya~ 🐾"
        }
        self.say(dialogues.get(acc_name, "Tampilan baru nya! ✨"), 3500)

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

    def _toggle_toxic_guardian(self, checked: bool):
        self.settings["toxic_guardian_enabled"] = checked
        save_settings(self.settings)
        if hasattr(self, "input_watcher") and self.input_watcher:
            self.input_watcher.set_toxic_guardian_enabled(checked)
        if checked:
            self.say("Mode Anti-Toxic aktif! Meong siap jagain kamu ya~ 🛡️🐾", 3500)
            self._play_sound_blip(freq=1450, dur=40)
        else:
            self.say("Mode Anti-Toxic dinonaktifkan nya~ 🐾", 2500)

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
            self._topmost_timer.start(1000)
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

    def _test_sound(self, sound_type: str):
        if not self.settings.get("sound_enabled", True):
            self.settings["sound_enabled"] = True
            save_settings(self.settings)
            self.say("Suara Kucing diaktifkan nya! 🔊🐾", 2000)
        audio.play_sound(sound_type, self.settings, force=True)

    def _toggle_sound(self, checked):
        self.settings["sound_enabled"] = checked
        save_settings(self.settings)
        if checked:
            audio.play_sound("meow_cute", self.settings, force=True)
            self.say("Suara Kucing diaktifkan nya! 🔊🐾", 3000)
        else:
            self.say("Suara dimatikan nya! 🔇🐾", 3000)

    def _toggle_ai_watcher(self, checked):
        self.ai_watcher.set_enabled(checked)
        save_settings(self.settings)
        if checked:
            self.say("Deteksi AI Agent diaktifkan nya! 🤖✨", 3500)
        else:
            self.say("Deteksi AI Agent dinonaktifkan nya! 🐾", 3000)

    def _toggle_startup(self, checked):
        success = set_startup_enabled(checked)
        if success:
            self.settings["run_on_startup"] = checked
            save_settings(self.settings)
            if checked:
                self.say("NyangBuddy sekarang otomatis nemenin kamu tiap laptop nyala nya! 🚀✨", 4000)
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

    def _start_centered_reminder(self, reminder_type: str, auto: bool = False, duration: float = 7.0, queue_next: list = None, on_finish_callback: callable = None, custom_message: str = None):
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

        # Check if currently peeking: save peek state so we can return to peek after reminder!
        self._was_peeking_before_reminder = getattr(self, "is_peeking", False)
        self._peek_side_before_reminder = getattr(self, "peek_side", "right")
        if self.is_peeking:
            self.is_peeking = False

        # Capture true desktop home location ONLY when departing from desktop
        self._active_custom_msg = custom_message
        self._active_reminder_type = reminder_type
        self._reminder_queue = list(queue_next) if queue_next else []
        self._was_combo = len(self._reminder_queue) > 0
        self._home_size = self.sprite_size
        self._home_pos = (self.x(), self.y())
        self._reminder_finish_callback = on_finish_callback

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
        """Executes one step in the health routine or Pomodoro transition."""
        self._active_reminder_type = reminder_type

        if reminder_type in ["pomodoro_work_done", "pomodoro_break_done", "alarm_done"]:
            self.set_state("celebrate", duration_seconds=duration)
        else:
            self.set_state(reminder_type, duration_seconds=duration)

        has_queued = len(self._reminder_queue) > 0

        if reminder_type == "stretch":
            audio.play_stretch(self.settings)
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
            audio.play_water(self.settings)
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

        elif reminder_type == "pomodoro_work_done":
            audio.play_celebrate(self.settings)
            cycle = self.pomodoro.current_cycle
            total = self.pomodoro.total_cycles
            is_auto = self.pomodoro.is_auto_cycle
            break_min = self.pomodoro.break_minutes

            if is_auto and total > 1:
                msg = f"YAY! Sesi fokus selesai! ({cycle}/{total}) 🎉🥳\nSaatnya istirahat {break_min} menit, regangkan badan dan santai ya nya~"
            else:
                msg = f"YAY! Sesi fokus selesai! 🎉🥳\nSaatnya istirahat {break_min} menit, rehat sejenak nya~"
            self.say(msg, int(duration * 1000 - 500))

        elif reminder_type == "alarm_done":
            audio.play_celebrate(self.settings)
            msg = self._active_custom_msg if self._active_custom_msg else "Waktunya agenda alarm kamu!"
            self.say(f"{msg}", int(duration * 1000 - 500))

        elif reminder_type == "pomodoro_break_done":
            self._play_sound_blip(freq=1200, dur=70)
            QTimer.singleShot(140, lambda: self._play_sound_blip(freq=1550, dur=90))
            cycle = self.pomodoro.current_cycle
            total = self.pomodoro.total_cycles
            is_auto = self.pomodoro.is_auto_cycle
            work_min = self.pomodoro.work_minutes

            if is_auto and cycle < total:
                msg = f"Waktu istirahat selesai! ☕\nSiap mulai sesi fokus ke-{cycle + 1} dari {total} ({work_min} menit) nya? 💻✨"
            elif is_auto and cycle >= total:
                msg = f"Selamat! Semua {total} siklus Pomodoro selesai! 🎉🐾\nKamu luar biasa fokus hari ini! Istirahat total ya~ ✨"
            else:
                msg = "Waktu istirahat selesai! Siap mulai lagi nya? ☕✨"
            self.say(msg, int(duration * 1000 - 500))

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
        if self._active_reminder_type is not None:
            self._glide_timer.stop()
            orig_x, orig_y = self._home_pos
            orig_size = self._home_size
            completed_type = self._active_reminder_type
            cb = self._reminder_finish_callback
            self._reminder_finish_callback = None
            was_peeking = getattr(self, "_was_peeking_before_reminder", False)
            peek_side = getattr(self, "_peek_side_before_reminder", "right")
            self._was_peeking_before_reminder = False

            def on_returned_home():
                self._active_reminder_type = None
                if cb:
                    cb()
                if was_peeking:
                    self.enter_peek_mode(side=peek_side, manual=False)
                elif completed_type in ["stretch", "drink_water"]:
                    self.set_state("idle")
                    self.say("Rutinitas istirahat selesai! Badan bugar & pikiran fokus lagi nya~ 🐾💪", 4000)
                else:
                    self.set_state("idle")

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


    def _prompt_user_name(self):
        current_name = self.settings.get("user_name", "")
        text, ok = QInputDialog.getText(
            self, "Panggilan Nama", "NyangBuddy harus panggil kamu apa?", text=current_name
        )
        if ok:
            text = text.strip()
            self.settings["user_name"] = text
            save_settings(self.settings)
            if text:
                self.say(f"Halo {text}! Salam kenal ya nya~ 🐾", 5000)
            else:
                self.say("Oke, aku panggil kamu secara umum aja nya~", 4000)

    def _prompt_custom_alarm(self):
        dialog = CustomAlarmDialog(parent=None)
        
        # Center dialog
        geo = self._get_current_screen_geometry()
        dialog.move(
            geo.center().x() - dialog.width() // 2,
            geo.center().y() - dialog.height() // 2
        )
        
        accepted = (dialog.exec() == 1) # QDialog.DialogCode.Accepted is 1
        
        self.show()
        self.raise_()
        if self.settings.get("stay_on_top", True):
            set_win32_topmost(self)
            
        if accepted:
            delay_sec, time_str, msg, count_str = dialog.get_values()
            delay_ms = int(delay_sec * 1000)
            
            def alarm_callback():
                self.set_state("idle")

            # QTimer singleShot expects milliseconds
            QTimer.singleShot(delay_ms, lambda: self._start_centered_reminder(
                "alarm_done",
                auto=True,
                duration=7.5,
                on_finish_callback=alarm_callback,
                custom_message=f"⏰ Waktunya: {msg}!\n(Pukul {time_str}) nya! 📢✨"
            ))
            
            self.say(f"Siap! Alarm disetel untuk pukul {time_str} ({count_str} lagi) nya! ⏰🐾", 5000)

    def _prompt_sticky_note(self):
        current_note = self.settings.get("sticky_note", "")
        text, ok = QInputDialog.getText(
            self, "Target Fokus / Catatan", "Tulis fokus kerjamu sekarang (Kosongkan untuk menghapus):", text=current_note
        )
        if ok:
            text = text.strip()
            self.settings["sticky_note"] = text
            save_settings(self.settings)
            if text:
                self.sticky_note.start(text)
                self.say(f"Catatan disematkan: \"{text}\"! 📝", 5000)
            else:
                self.sticky_note.stop()
                self.say("Catatan dilepas nya~", 3000)
            self._update_bubble_position()
    def close_app(self):
        self.input_watcher.stop()
        self.speech_bubble.close()
        self.close()
        QApplication.quit()
