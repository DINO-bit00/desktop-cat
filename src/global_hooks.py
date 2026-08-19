"""
Global OS Input Hooks for Comnyang-Style Interactions
Listens to system-wide keyboard typing cadence (kneading & overheat)
and mouse scroll wheel (paper unroll reaction) with instant zero-lag stop response
and strict overheat threshold protection.
100% offline, zero network, zero data storage.
"""

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
    Emits signals with immediate response and zero unnecessary delays.
    """
    # Signals
    typing_started = pyqtSignal()
    typing_stopped = pyqtSignal()
    overheat_started = pyqtSignal()
    overheat_ended = pyqtSignal()
    mouse_scrolled = pyqtSignal(int)          # dy scroll amount (+1 = up, -1 = down)
    mouse_moved_fast = pyqtSignal(int, int)   # dx, dy

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self._last_key_time = 0.0
        self._typing_burst_start = 0.0
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

    def _on_key_press(self, key):
        now = time.time()
        self._last_key_time = now
        self._key_count_window.append(now)

        # Rolling window of keystrokes in last 1.5 seconds
        self._key_count_window = [t for t in self._key_count_window if now - t <= 1.5]

        if not self._is_typing:
            self._is_typing = True
            self._typing_burst_start = now
            self.typing_started.emit()

        # Strict Overheat Trigger:
        # Requires:
        # 1. At least 16 keystrokes in the last 1.5s (>100+ WPM fast furious typing)
        # 2. Continuous typing sustained for at least 0.7s (prevents accidental trigger from short bursts)
        if len(self._key_count_window) >= 16 and (now - self._typing_burst_start >= 0.7):
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
        self._last_scroll_time = time.time()
        self.mouse_scrolled.emit(int(dy))

    def _watchdog_loop(self):
        """Monitors typing cooldown and instant cease with clean window resets."""
        while self.is_running:
            time.sleep(0.04)  # 40ms snappy poll
            now = time.time()

            # Clean rolling window
            self._key_count_window = [t for t in self._key_count_window if now - t <= 1.5]

            # Check Overheat cool-down (cools down as soon as speed drops below 8 keys in 1.5s)
            if self._is_overheated and len(self._key_count_window) < 8:
                self._is_overheated = False
                self.overheat_ended.emit()

            # Snappy typing cease: Stop animation immediately when no key pressed for > 0.35s
            if self._is_typing and (now - self._last_key_time > 0.35):
                self._is_typing = False
                self._is_overheated = False
                # CRITICAL: Clear keystroke history window on typing pause so next typing starts fresh!
                self._key_count_window.clear()
                self._typing_burst_start = 0.0
                self.typing_stopped.emit()
