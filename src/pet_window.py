"""
Main Desktop Pet Window
Transparent, draggable, animated floating companion with interactive state machine,
physics, Pomodoro timer integration, and custom context menus.
"""

import os
import sys
import ctypes
import random
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QCursor, QAction, QIcon, QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QMenu, QInputDialog, QMessageBox, QApplication
)

from src.sprites import PALETTES, render_cat_frame
from src.speech_bubble import SpeechBubble
from src.pomodoro import PomodoroManager
from src.local_watcher import LocalWatcher
from src.settings import save_settings


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
            Qt.WindowType.SubWindow |
            Qt.WindowType.Tool
        )
        if self.settings.get("stay_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Pet Dimensions
        self.sprite_size = 128
        self.setFixedSize(self.sprite_size, self.sprite_size)

        # State Machine
        self.skin = self.settings.get("skin", "oyen")
        self.state = "idle"         # idle, walk_left, walk_right, sleep, work, pet, celebrate, thinking
        self.target_state = "idle"
        self.frame_index = 0
        self.state_ticks = 0
        self.max_state_ticks = 20

        # Movement & Dragging
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.velocity_x = 0
        self.is_falling = False

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

        # Local File Event Watcher (for CLI / script triggers)
        self.watcher = LocalWatcher(self)
        self.watcher.event_received.connect(self._on_external_event)

        # Animation Loop Timer (200ms per frame)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(200)

        # Physics & AI Behavior Timer (every 50ms)
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._update_behavior)
        self.physics_timer.start(50)

        # Position at bottom-right of primary screen
        self._snap_to_initial_position()

        # Say hello at startup
        QTimer.singleShot(800, self._say_welcome)

    # -------------------------------------------------------------
    # Sprite & Cache Management
    # -------------------------------------------------------------
    def _load_skin_sprites(self, skin_name):
        self.skin = skin_name
        self.pixmap_cache.clear()
        states = ["idle", "walk_left", "walk_right", "sleep", "work", "pet", "celebrate", "thinking"]

        for st in states:
            self.pixmap_cache[st] = []
            for frame in range(4):
                # Render using Pillow then convert to QPixmap
                pil_img = render_cat_frame(skin_name, st, frame)
                # Convert PIL RGBA to QImage
                raw_bytes = pil_img.tobytes("raw", "RGBA")
                from PyQt6.QtGui import QImage
                qimg = QImage(raw_bytes, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimg)
                self.pixmap_cache[st].append(pixmap)

    def _get_current_pixmap(self):
        frames = self.pixmap_cache.get(self.state, self.pixmap_cache.get("idle", []))
        if not frames:
            return None
        return frames[self.frame_index % len(frames)]

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
        x = screen_geo.right() - self.sprite_size - 60
        y = screen_geo.bottom() - self.sprite_size
        self.move(x, y)
        self._update_bubble_position()

    def _update_bubble_position(self):
        if self.speech_bubble.isVisible():
            self.speech_bubble.update_position_relative_to(self.pos(), self.sprite_size)

    # -------------------------------------------------------------
    # State & Animation Controller
    # -------------------------------------------------------------
    def set_state(self, new_state, duration_seconds=None):
        if new_state in self.pixmap_cache or new_state == "walk":
            if new_state == "walk":
                new_state = "walk_right"
            self.state = new_state
            self.frame_index = 0
            self.state_ticks = 0
            if duration_seconds:
                self.max_state_ticks = int(duration_seconds * 5)
            self.update()

    def _update_animation(self):
        self.frame_index = (self.frame_index + 1) % 4
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self.settings.get("stay_on_top", True):
            set_win32_topmost(self)

    def _update_behavior(self):
        if self.is_dragging:
            return

        # Periodically ensure topmost if enabled
        if self.settings.get("stay_on_top", True) and random.random() < 0.05:
            set_win32_topmost(self)

        screen_geo = self._get_current_screen_geometry()
        floor_y = screen_geo.bottom() - self.sprite_size

        # Simple Gravity
        curr_x = self.x()
        curr_y = self.y()

        if curr_y < floor_y:
            # Fall gently to the floor
            new_y = min(floor_y, curr_y + 4)
            self.move(curr_x, new_y)
            self._update_bubble_position()
            return

        # Autonomous Wander Logic
        if not self.settings.get("wander_mode", True) or self.pomodoro.is_active or self.state in ["work", "sleep", "thinking", "pet"]:
            return

        self.state_ticks += 1
        if self.state_ticks > self.max_state_ticks:
            # Pick a new random action
            self.state_ticks = 0
            choices = ["idle", "idle", "walk_left", "walk_right", "sleep"]
            new_action = random.choice(choices)
            if new_action == "sleep":
                self.max_state_ticks = random.randint(80, 160)
            elif "walk" in new_action:
                self.max_state_ticks = random.randint(30, 70)
            else:
                self.max_state_ticks = random.randint(40, 90)
            self.state = new_action

        # Handle Walking physics
        if self.state == "walk_left":
            new_x = curr_x - 2
            if new_x <= screen_geo.left():
                self.state = "walk_right"
            else:
                self.move(new_x, curr_y)
                self._update_bubble_position()
        elif self.state == "walk_right":
            new_x = curr_x + 2
            if new_x >= screen_geo.right() - self.sprite_size:
                self.state = "walk_left"
            else:
                self.move(new_x, curr_y)
                self._update_bubble_position()

    # -------------------------------------------------------------
    # Paint & Render
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self._get_current_pixmap()
        if pixmap:
            painter.drawPixmap(0, 0, pixmap)

    # -------------------------------------------------------------
    # Mouse & Drag Interactions
    # -------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_start_pos
            self.move(new_pos)
            self._update_bubble_position()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # If it was a quick click without dragging, treat as petting!
            self._on_pet_clicked()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Double click: Quick start/stop Pomodoro or say greeting
            if self.pomodoro.is_active:
                self.pomodoro.stop()
                self.set_state("idle")
                self.say("Pomodoro dihentikan nya~ ⏸️")
            else:
                self.pomodoro.start_focus()
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
        if self.pomodoro.is_active and self.pomodoro.mode == "work":
            quotes = [
                "Fokus dulu ya nya! Semangat! 💪",
                "Ngebut terus kodenya nya~ 🔥",
                "Kerja bagus! Nanti kita istirahat bareng nya~ ✨"
            ]
            self.say(random.choice(quotes), 3000)
            return

        self.set_state("pet", duration_seconds=3)
        purrs = [
            "Purrr... Senang dielus nya~ ❤️",
            "Meooow~! Semangat ya hari ini! ✨",
            "Nyang~ Mau ditemenin ngoding apa santai nih? 😸",
            "Purrr purrr... Kucing senang, kerjaan lancar! 🐾",
            "Meow! Jangan lupa regangkan tanganmu ya~ 🧘"
        ]
        self.say(random.choice(purrs), 3500)

    def _play_sound_blip(self):
        if not self.settings.get("sound_enabled", True):
            return
        try:
            import winsound
            winsound.Beep(1200, 60)
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
        self.setToolTip(f"NyangBuddy - {title} [{mins:02d}:{secs:02d}]")

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

        menu.addSeparator()

        # 2. Pomodoro Submenu
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

        # 3. Actions / State Switch
        act_menu = menu.addMenu("🐾 Ganti Gaya / Aksi")
        act_menu.addAction("😺 Duduk Santai (Idle)", lambda: self.set_state("idle"))
        act_menu.addAction("💻 Mode Ngoding/Work", lambda: self.set_state("work"))
        act_menu.addAction("😴 Tidur (Sleep)", lambda: self.set_state("sleep"))
        act_menu.addAction("🎉 Melompat Senang (Jump)", lambda: self.set_state("celebrate", 4))
        act_menu.addAction("🤔 Berpikir (Thinking)", lambda: self.set_state("thinking", 4))

        menu.addSeparator()

        # 4. Sticky Note / Pinned Focus
        note_action = menu.addAction("📌 Set Target Fokus / Note")
        note_action.triggered.connect(self._prompt_sticky_note)

        # 5. Options
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

        menu.addSeparator()

        # 6. Quit
        quit_act = menu.addAction("❌ Keluar (Close)")
        quit_act.triggered.connect(self.close_app)

        menu.exec(global_pos)

    def _change_skin(self, skin_key):
        self._load_skin_sprites(skin_key)
        self.settings["skin"] = skin_key
        save_settings(self.settings)
        self.update()
        pet_name = PALETTES[skin_key]["name"]
        self.say(f"Ganti kostum ke {pet_name} nya! 🐾")

    def _toggle_wander(self, checked):
        self.settings["wander_mode"] = checked
        save_settings(self.settings)
        if not checked:
            self.state = "idle"

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
        self.speech_bubble.close()
        self.close()
        QApplication.quit()
