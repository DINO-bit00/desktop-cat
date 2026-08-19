"""
Global OS Input Hooks for Comnyang-Style Interactions
Listens to system-wide keyboard typing, mouse strokes (petting), and scrolling
in a background thread without blocking the Qt GUI event loop.
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
    Monitors typing speed, mouse movements, and petting gestures system-wide.
    Emits signals safely to Qt main thread.
    """
    # Signals
    typing_started = pyqtSignal()
    typing_stopped = pyqtSignal()
    overheat_triggered = pyqtSignal()
    mouse_scrolled = pyqtSignal(int)      # dy scroll amount
    mouse_moved_fast = pyqtSignal(int, int) # dx, dy

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self._last_key_time = 0.0
        self._key_count_window = []  # timestamps of recent keystrokes
        self._is_typing = False

        # Mouse tracking
        self._last_mouse_pos = (0, 0)
        self._last_mouse_time = 0.0

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

            # Background checker for typing timeout
            threading.Thread(target=self._typing_watchdog, daemon=True).start()
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

        # Keep only keystrokes from the last 3 seconds
        self._key_count_window = [t for t in self._key_count_window if now - t <= 3.0]

        if not self._is_typing:
            self._is_typing = True
            self.typing_started.emit()

        # Check for Overheat Mode (Typing fast: >15 keys in 3 seconds = ~60-80 WPM)
        if len(self._key_count_window) >= 16:
            self.overheat_triggered.emit()

    def _on_mouse_move(self, x, y):
        now = time.time()
        dt = now - self._last_mouse_time
        if dt > 0.05:
            dx = x - self._last_mouse_pos[0]
            dy = y - self._last_mouse_pos[1]
            speed = (dx**2 + dy**2) ** 0.5 / dt  # px per second
            if speed > 1200:  # Fast flick/hunt motion
                self.mouse_moved_fast.emit(int(x), int(y))
            self._last_mouse_pos = (x, y)
            self._last_mouse_time = now

    def _on_mouse_scroll(self, x, y, dx, dy):
        self.mouse_scrolled.emit(int(dy))

    def _typing_watchdog(self):
        """Monitors when typing ceases for > 1.8 seconds."""
        while self.is_running:
            time.sleep(0.3)
            now = time.time()
            if self._is_typing and (now - self._last_key_time > 1.8):
                self._is_typing = False
                self.typing_stopped.emit()
