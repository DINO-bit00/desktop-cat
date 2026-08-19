"""
Local File & IPC Watcher
Monitors a local file (.cat_trigger.json) for state changes and messages.
Allows external CLI scripts, git hooks, AI tools, or terminal tasks to trigger
reactions locally without exposing any ports to the network.
"""

import json
import os
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

TRIGGER_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cat_trigger.json")


class LocalWatcher(QObject):
    # Signals
    event_received = pyqtSignal(dict)  # {"state": "thinking", "message": "Compiling...", "duration": 5}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_mtime = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_file)
        self.timer.start(500)  # Poll local file every 500ms

        # Clean trigger file at startup
        if os.path.exists(TRIGGER_FILE):
            try:
                self.last_mtime = os.path.getmtime(TRIGGER_FILE)
            except Exception:
                pass

    def _check_file(self):
        if not os.path.exists(TRIGGER_FILE):
            return

        try:
            mtime = os.path.getmtime(TRIGGER_FILE)
            if mtime > self.last_mtime:
                self.last_mtime = mtime
                with open(TRIGGER_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.event_received.emit(data)
        except Exception:
            pass


def trigger_event(state=None, message=None, duration=4):
    """Utility function to write a trigger payload into the local trigger file."""
    payload = {
        "timestamp": os.times().elapsed,
        "state": state,
        "message": message,
        "duration": duration
    }
    try:
        with open(TRIGGER_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Trigger] Error sending trigger: {e}")
        return False
