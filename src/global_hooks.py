"""
Global OS Input Hooks for Comnyang-Style Interactions
Listens to system-wide keyboard typing cadence (kneading & overheat),
laptop precision touchpad 2-finger scroll (all Windows wheel & pointer messages),
keyboard document navigation scroll (PageDown, PageUp, Arrow keys),
and mouse wheel.
100% offline, zero network, zero data storage.
"""

import sys
import time
import threading
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except Exception:
    PYNPUT_AVAILABLE = False


class GlobalInputWatcher(QObject):
    """
    Monitors typing speed, mouse movements, and scroll activity system-wide.
    Comprehensive scroll detection for:
    1. Laptop touchpad 2-finger scrolling (WM_MOUSEWHEEL, WM_MOUSEHWHEEL, WM_POINTERWHEEL)
    2. Physical mouse scroll wheel
    3. Keyboard document navigation (Page Down, Page Up, Down Arrow, Up Arrow)
    """
    # Signals
    typing_started = pyqtSignal()
    typing_stopped = pyqtSignal()
    overheat_started = pyqtSignal()
    overheat_ended = pyqtSignal()
    mouse_scrolled = pyqtSignal(float, float)   # dx, dy as floats
    mouse_moved_fast = pyqtSignal(int, int)     # dx, dy

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self._last_key_time = 0.0
        self._key_count_window = []  # timestamps of recent keystrokes
        self._is_typing = False
        self._is_overheated = False

        # Mouse tracking
        self._last_mouse_pos = (0, 0)
        self._last_mouse_time = 0.0

        # Scroll tracking
        self._last_scroll_time = 0.0

        # Worker threads
        self._kb_listener = None
        self._mouse_listener = None

    def start(self):
        if not PYNPUT_AVAILABLE or self.is_running:
            return

        self.is_running = True
        try:
            self._kb_listener = keyboard.Listener(on_press=self._on_key_press)
            self._kb_listener.daemon = True
            self._kb_listener.start()

            if sys.platform == "win32":
                self._mouse_listener = mouse.Listener(
                    on_move=self._on_mouse_move,
                    on_scroll=self._on_mouse_scroll,
                    win32_event_filter=self._win32_mouse_filter
                )
            else:
                self._mouse_listener = mouse.Listener(
                    on_move=self._on_mouse_move,
                    on_scroll=self._on_mouse_scroll
                )
            self._mouse_listener.daemon = True
            self._mouse_listener.start()

            # High-frequency watchdog (40ms tick) for instant stop response
            threading.Thread(target=self._watchdog_loop, daemon=True).start()
        except Exception as e:
            print(f"[GlobalInputWatcher] Error starting listeners: {e}")

    def stop(self):
        self.is_running = False
        if self._kb_listener:
            try:
                self._kb_listener.stop()
            except Exception:
                pass
        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass

    def _win32_mouse_filter(self, msg, data):
        """
        Low-level Windows event filter:
        Catches fractional 2-finger touchpad scrolling (WM_MOUSEWHEEL, WM_MOUSEHWHEEL, WM_POINTERWHEEL)
        and emits scroll signals immediately.
        """
        # WM_MOUSEWHEEL = 0x020A, WM_MOUSEHWHEEL = 0x020E, WM_POINTERWHEEL = 0x024E, WM_POINTERHWHEEL = 0x024F
        if msg in (0x020A, 0x020E, 0x024E, 0x024F):
            try:
                raw = (data.mouseData >> 16) & 0xFFFF
                if raw > 32767:
                    raw -= 65536
                float_delta = raw / 120.0 if raw != 0 else 1.0
                self._last_scroll_time = time.time()
                if msg in (0x020A, 0x024E):
                    self.mouse_scrolled.emit(0.0, float_delta)
                else:
                    self.mouse_scrolled.emit(float_delta, 0.0)
            except Exception:
                pass
        return True

    def _on_key_press(self, key):
        now = time.time()

        # Keyboard Document Navigation Scroll Keys (trigger Paper Unroll instead of typing)
        if hasattr(keyboard, 'Key'):
            if key in (keyboard.Key.page_down, keyboard.Key.page_up, keyboard.Key.down, keyboard.Key.up):
                self._last_scroll_time = now
                dy = 1.0 if key in (keyboard.Key.page_up, keyboard.Key.up) else -1.0
                self.mouse_scrolled.emit(0.0, dy)
                return

        self._last_key_time = now
        self._key_count_window.append(now)

        # Rolling window of keystrokes in last 1.8 seconds
        self._key_count_window = [t for t in self._key_count_window if now - t <= 1.8]

        if not self._is_typing:
            self._is_typing = True
            self.typing_started.emit()

        # Balanced Overheat Trigger: 11 keys in 1.8s (~75 WPM)
        if len(self._key_count_window) >= 11:
            if not self._is_overheated:
                self._is_overheated = True
                self.overheat_started.emit()

    def _on_mouse_move(self, x, y):
        now = time.time()
        dt = now - self._last_mouse_time
        if dt > 0.04:
            dx = x - self._last_mouse_pos[0]
            dy = y - self._last_mouse_pos[1]
            speed = (dx**2 + dy**2) ** 0.5 / dt
            if speed > 1100:  # Fast flick/hunt motion
                self.mouse_moved_fast.emit(int(x), int(y))
            self._last_mouse_pos = (x, y)
            self._last_mouse_time = now

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Called by standard pynput listener on all platforms."""
        self._last_scroll_time = time.time()
        self.mouse_scrolled.emit(float(dx), float(dy))

    def _watchdog_loop(self):
        """Monitors typing cooldown and instant cease with clean window resets."""
        while self.is_running:
            time.sleep(0.04)  # 40ms snappy poll
            now = time.time()

            # Clean rolling window
            self._key_count_window = [t for t in self._key_count_window if now - t <= 1.8]

            # Check Overheat cool-down
            if self._is_overheated and len(self._key_count_window) < 5:
                self._is_overheated = False
                self.overheat_ended.emit()

            # Snappy typing cease: Stop animation immediately when no key pressed for > 0.35s
            if self._is_typing and (now - self._last_key_time > 0.35):
                self._is_typing = False
                self._is_overheated = False
                # Clear keystroke memory on pause so next typing session starts fresh!
                self._key_count_window.clear()
                self.typing_stopped.emit()
