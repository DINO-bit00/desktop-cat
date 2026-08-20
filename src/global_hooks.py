"""
Global OS Input Hooks for Comnyang-Style Interactions
Multi-layer detection for system-wide keyboard cadence, mouse wheel,
laptop precision touchpad gestures (Win32 Hook + WinEvent Scroll Hook),
and keyboard document navigation scroll keys.
100% offline, zero network, zero data storage.
"""

import sys
import time
import ctypes
from ctypes import wintypes
import threading
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except Exception:
    PYNPUT_AVAILABLE = False


# Win32 Accessibility Event Hooks
WINEVENT_OUTOFCONTEXT = 0
EVENT_SYSTEM_SCROLLINGSTART = 0x0012
EVENT_SYSTEM_SCROLLINGEND = 0x0013

WINEVENTPROC = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD
)


class GlobalInputWatcher(QObject):
    """
    Monitors typing speed, mouse movements, and scroll activity system-wide.
    Multi-layer detection guarantees 100% reliability for:
    1. Laptop Precision Touchpad 2-Finger Gestures (Win32 Hook + WinEvent Accessibility)
    2. Physical Mouse Scroll Wheel
    3. Keyboard Document Navigation (Page Down, Page Up, Down Arrow, Up Arrow)
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

        # Worker threads & native handles
        self._kb_listener = None
        self._mouse_listener = None
        self._winevent_proc = None
        self._winevent_hook = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True

        # 1. Keyboard Listener
        if PYNPUT_AVAILABLE:
            try:
                self._kb_listener = keyboard.Listener(on_press=self._on_key_press)
                self._kb_listener.daemon = True
                self._kb_listener.start()
            except Exception as e:
                print(f"[GlobalInputWatcher] Error starting keyboard listener: {e}")

        # 2. Low-level Mouse Scroll Listener (Zero move hook = 0% mouse latency & stutter-free)
        if PYNPUT_AVAILABLE:
            try:
                if sys.platform == "win32":
                    self._mouse_listener = mouse.Listener(
                        on_scroll=self._on_mouse_scroll,
                        win32_event_filter=self._win32_mouse_filter
                    )
                else:
                    self._mouse_listener = mouse.Listener(
                        on_scroll=self._on_mouse_scroll
                    )
                self._mouse_listener.daemon = True
                self._mouse_listener.start()
            except Exception as e:
                print(f"[GlobalInputWatcher] Error starting mouse listener: {e}")

        # 3. Windows Native WinEvent Hook (Catches system-wide touchpad DirectManipulation scrolling)
        if sys.platform == "win32":
            try:
                self._winevent_proc = WINEVENTPROC(self._on_win_scroll_event)
                self._winevent_hook = ctypes.windll.user32.SetWinEventHook(
                    EVENT_SYSTEM_SCROLLINGSTART,
                    EVENT_SYSTEM_SCROLLINGEND,
                    0,
                    self._winevent_proc,
                    0,
                    0,
                    WINEVENT_OUTOFCONTEXT
                )
            except Exception as e:
                print(f"[GlobalInputWatcher] WinEventHook info: {e}")

        # 4. High-frequency watchdog (40ms tick) for instant stop response
        threading.Thread(target=self._watchdog_loop, daemon=True).start()

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
        if sys.platform == "win32" and self._winevent_hook:
            try:
                ctypes.windll.user32.UnhookWinEvent(self._winevent_hook)
                self._winevent_hook = None
            except Exception:
                pass

    def _on_win_scroll_event(self, hHook, event, hwnd, idObject, idChild, dwThread, dwTime):
        """Triggered directly by Windows OS whenever any window / document scrolls."""
        self._last_scroll_time = time.time()
        self.mouse_scrolled.emit(0.0, 1.0)

    def _win32_mouse_filter(self, msg, data):
        """Low-level hook filter for fractional touchpad wheel messages."""
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
