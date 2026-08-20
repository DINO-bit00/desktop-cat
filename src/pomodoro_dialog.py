"""
Custom Pomodoro Setup Dialog
A clean, modern Qt modal dialog allowing users to configure:
1. Focus duration (in minutes)
2. Break duration (in minutes)
3. Number of focus-break cycles (loops)
Displays live total estimated session time in real-time.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QFrame, QDialogButtonBox, QWidget
)


class CustomPomodoroDialog(QDialog):
    def __init__(self, parent=None, default_work=25, default_break=5, default_cycles=4):
        super().__init__(parent)
        self.setWindowTitle("⏱️ Atur Sesi Pomodoro")
        self.setFixedWidth(360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

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
            QLabel#summaryLabel {
                font-size: 12px;
                color: #38bdf8;
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
            }
            QSpinBox {
                background-color: #0f172a;
                color: #ffffff;
                border: 1.5px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: bold;
                min-height: 28px;
            }
            QSpinBox:focus {
                border-color: #38bdf8;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #1e293b;
                border-radius: 3px;
                margin: 2px;
            }
            QPushButton#btnStart {
                background-color: #22c55e;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btnStart:hover {
                background-color: #16a34a;
            }
            QPushButton#btnStart:pressed {
                background-color: #15803d;
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
        title = QLabel("⏱️ Sesi Pomodoro Terjadwal", self)
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        subtitle = QLabel("Karakter otomatis memandu fokus, istirahat, dan transisi ke tengah layar.", self)
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Divider
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #334155;")
        layout.addWidget(divider)

        # Field 1: Focus Minutes
        layout.addWidget(QLabel("🎯 <b>Waktu Fokus</b> (per sesi):", self))
        self.spin_work = QSpinBox(self)
        self.spin_work.setRange(1, 180)
        self.spin_work.setValue(default_work)
        self.spin_work.setSuffix(" Menit")
        self.spin_work.setSingleStep(5)
        self.spin_work.valueChanged.connect(self._update_summary)
        layout.addWidget(self.spin_work)

        # Field 2: Break Minutes
        layout.addWidget(QLabel("☕ <b>Waktu Istirahat</b> (per sesi):", self))
        self.spin_break = QSpinBox(self)
        self.spin_break.setRange(1, 60)
        self.spin_break.setValue(default_break)
        self.spin_break.setSuffix(" Menit")
        self.spin_break.setSingleStep(1)
        self.spin_break.valueChanged.connect(self._update_summary)
        layout.addWidget(self.spin_break)

        # Field 3: Cycles
        layout.addWidget(QLabel("🔄 <b>Jumlah Siklus</b> (fokus ⇄ istirahat):", self))
        self.spin_cycles = QSpinBox(self)
        self.spin_cycles.setRange(1, 12)
        self.spin_cycles.setValue(default_cycles)
        self.spin_cycles.setSuffix(" Siklus")
        self.spin_cycles.setSingleStep(1)
        self.spin_cycles.valueChanged.connect(self._update_summary)
        layout.addWidget(self.spin_cycles)

        # Summary box
        self.summary_label = QLabel("", self)
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("▶️ Mulai Sesi", self)
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

        # Initial summary
        self._update_summary()

    def _update_summary(self):
        w = self.spin_work.value()
        b = self.spin_break.value()
        c = self.spin_cycles.value()

        total_min = (w + b) * c
        hours = total_min // 60
        mins = total_min % 60

        time_str = f"{hours} jam {mins} menit" if hours > 0 else f"{mins} menit"
        self.summary_label.setText(
            f"📊 <b>Ringkasan:</b> {c} siklus × ({w}m fokus + {b}m rehat)<br>"
            f"⏱️ <b>Total Durasi:</b> {time_str}"
        )

    def get_values(self):
        """Returns (work_minutes, break_minutes, cycles)."""
        return (
            self.spin_work.value(),
            self.spin_break.value(),
            self.spin_cycles.value()
        )
