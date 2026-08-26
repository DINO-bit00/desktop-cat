"""
Custom Alarm Dialog (Clock Time & Scheduled Reminder)
A clean, modern Qt modal dialog for setting a specific time-of-day alarm (e.g. 11:30)
with live countdown calculation, quick presets, and custom message support.
"""

from PyQt6.QtCore import Qt, QTime, QDateTime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTimeEdit,
    QPushButton, QFrame, QLineEdit
)


class CustomAlarmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⏰ Setel Pengingat Jam")
        self.setFixedWidth(380)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e222b;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QLabel#headerTitle {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#headerSubtitle {
                font-size: 12px;
                color: #94a3b8;
            }
            QLabel#countdownLabel {
                font-size: 13px;
                font-weight: bold;
                color: #38bdf8;
                background-color: #0f172a;
                border: 1px dashed #334155;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QTimeEdit, QLineEdit {
                background-color: #0f172a;
                color: #ffffff;
                border: 1.5px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 15px;
                font-weight: bold;
                min-height: 28px;
            }
            QTimeEdit:focus, QLineEdit:focus {
                border-color: #38bdf8;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 22px;
                background: #1e293b;
                border-radius: 3px;
                margin: 2px;
            }
            QPushButton.quickBtn {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton.quickBtn:hover {
                background-color: #334155;
                color: #ffffff;
                border-color: #38bdf8;
            }
            QPushButton#btnStart {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btnStart:hover {
                background-color: #2563eb;
            }
            QPushButton#btnStart:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#btnCancel {
                background-color: #334155;
                color: #cbd5e1;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
            }
            QPushButton#btnCancel:hover {
                background-color: #475569;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("⏰ Setel Alarm & Pengingat Jam", self)
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        subtitle = QLabel("Kucing akan mengingatkanmu ke tengah layar saat jam alarm tiba.", self)
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Divider
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #334155;")
        layout.addWidget(divider)

        # Field 1: Time of Day (QTimeEdit)
        layout.addWidget(QLabel("🕒 <b>Ingatkan pada Jam (Pukul):</b>", self))
        
        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm")
        
        # Calculate default time: Current time + 30 minutes (rounded to nearest 5 mins)
        now_time = QTime.currentTime()
        def_min = ((now_time.minute() + 30 + 4) // 5) * 5
        def_hour = (now_time.hour() + (def_min // 60)) % 24
        def_min = def_min % 60
        self.time_edit.setTime(QTime(def_hour, def_min))
        self.time_edit.timeChanged.connect(self._update_countdown_label)
        layout.addWidget(self.time_edit)

        # Quick Add Offset Buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(6)
        
        offsets = [("+15 Mnt", 15), ("+30 Mnt", 30), ("+45 Mnt", 45), ("+1 Jam", 60), ("+2 Jam", 120)]
        for label, mins in offsets:
            btn = QPushButton(label, self)
            btn.setProperty("class", "quickBtn")
            btn.clicked.connect(lambda _, m=mins: self._add_minutes_from_now(m))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout)

        # Live Countdown Label
        self.lbl_countdown = QLabel("", self)
        self.lbl_countdown.setObjectName("countdownLabel")
        layout.addWidget(self.lbl_countdown)

        # Field 2: Message / Event Name
        layout.addWidget(QLabel("📝 <b>Nama Agenda / Catatan Pengingat:</b>", self))
        self.input_msg = QLineEdit(self)
        self.input_msg.setPlaceholderText("Contoh: Meeting Tim, Kuliah Online, Makan Siang...")
        layout.addWidget(self.input_msg)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("🔔 Pasang Alarm", self)
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)
        
        # Initial label update
        self._update_countdown_label()

    def _add_minutes_from_now(self, mins: int):
        target = QTime.currentTime().addSecs(mins * 60)
        self.time_edit.setTime(target)

    def _get_delay_seconds_and_details(self):
        now = QDateTime.currentDateTime()
        target_qtime = self.time_edit.time()
        target_dt = QDateTime(now.date(), target_qtime)

        is_tomorrow = False
        if target_dt <= now:
            target_dt = target_dt.addDays(1)
            is_tomorrow = True

        msecs = now.msecsTo(target_dt)
        seconds = max(1.0, msecs / 1000.0)
        minutes = int(seconds // 60)
        hours = minutes // 60
        rem_mins = minutes % 60

        time_str = target_qtime.toString("HH:mm")
        
        if hours > 0:
            count_str = f"{hours} jam {rem_mins} menit" if rem_mins > 0 else f"{hours} jam"
        else:
            count_str = f"{minutes} menit" if minutes > 0 else "kurang dari semenit"

        if is_tomorrow:
            desc = f"Besok pukul {time_str} (dalam {count_str})"
        else:
            desc = f"Dalam {count_str} (pukul {time_str})"

        return seconds, time_str, count_str, desc, is_tomorrow

    def _update_countdown_label(self):
        _, time_str, _, desc, is_tomorrow = self._get_delay_seconds_and_details()
        prefix = "🌙 " if is_tomorrow else "⏳ "
        self.lbl_countdown.setText(f"{prefix}Alarm akan berbunyi: <b>{desc}</b>")

    def get_values(self):
        """
        Returns:
            (delay_seconds, time_str, message, desc)
        """
        seconds, time_str, count_str, desc, is_tomorrow = self._get_delay_seconds_and_details()
        msg = self.input_msg.text().strip()
        if not msg:
            msg = f"Agenda Pukul {time_str}"
        return seconds, time_str, msg, count_str

